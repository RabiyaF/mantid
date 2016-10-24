#include "MantidCurveFitting/Functions/CrystalFieldPeakUtils.h"

#include "MantidAPI/CompositeFunction.h"
#include "MantidAPI/IPeakFunction.h"
#include "MantidAPI/FunctionFactory.h"
#include "MantidCurveFitting/Constraints/BoundaryConstraint.h"

#include <algorithm>

namespace Mantid {
namespace CurveFitting {
namespace Functions {
namespace CrystalFieldUtils {

using namespace CurveFitting;
using namespace Kernel;
using namespace API;

/// Calculate the width of a peak cenrted at x using 
/// an interpolated value of a function tabulated at xVec points
/// @param x :: Peak centre.
/// @param xVec :: x-values of a tabulated width function.
/// @param yVec :: y-values of a tabulated width function.
double calculateWidth(double x, const std::vector<double> &xVec,
                      const std::vector<double> &yVec) {
  assert(xVec.size() == yVec.size());
  auto upperIt = std::lower_bound(xVec.begin(), xVec.end(), x);
  if (upperIt == xVec.end() || x < xVec.front()) {
    throw std::runtime_error("Cannot calculate peak width: peak at " +
                             std::to_string(x) + " is outside given range (" +
                             std::to_string(xVec.front()) + " : " +
                             std::to_string(xVec.back()) + ")");
  }
  if (upperIt == xVec.begin()) {
    return yVec.front();
  }
  double lowerX = *(upperIt - 1);
  double upperX = *upperIt;
  auto i = std::distance(xVec.begin(), upperIt) - 1;
  return yVec[i] + (yVec[i + 1] - yVec[i]) / (upperX - lowerX) * (x - lowerX);
}

/// Set a boundary constraint on the appropriate parameter of the peak.
/// @param peak :: A peak function.
/// @param width :: A width of the peak.
/// @param widthVariation :: A value by which the with can vary on both sides.
void setWidthConstraint(API::IPeakFunction& peak, double width, double fwhmVariation) {
  double upperBound = width + fwhmVariation;
  double lowerBound = width - fwhmVariation;
  bool fix = lowerBound == upperBound;
  if (!fix) {
    if (lowerBound < 0.0) {
      lowerBound = 0.0;
    }
    if (lowerBound >= upperBound) {
      lowerBound = upperBound / 2;
    }
  }
  if (peak.name() == "Lorentzian") {
    if (fix) {
      peak.fixParameter("FWHM");
      return;
    }
    auto constraint = new Constraints::BoundaryConstraint(&peak, "FWHM", lowerBound, upperBound);
    peak.addConstraint(constraint);
  } else if (peak.name() == "Gaussian") {
    if (fix) {
      peak.fixParameter("Sigma");
      return;
    }
    const double WIDTH_TO_SIGMA = 2.0 * sqrt(2.0 * M_LN2);
    lowerBound /= WIDTH_TO_SIGMA;
    upperBound /= WIDTH_TO_SIGMA;
    auto constraint = new Constraints::BoundaryConstraint(&peak, "Sigma", lowerBound, upperBound);
    peak.addConstraint(constraint);
  } else {
    throw std::runtime_error("Cannot set constraint on width of " + peak.name());
  }
}


/// Populates a spectrum with peaks of type given by peakShape argument.
/// @param spectrum :: A composite function that is a collection of peaks.
/// @param peakShape :: A shape of each peak as a name of an IPeakFunction.
/// @param centresAndIntensities :: A FunctionValues object containing centres
///        and intensities for the peaks. First nPeaks calculated values are the
///        centres and the following nPeaks values are the intensities.
/// @param xVec :: x-values of a tabulated width function.
/// @param yVec :: y-values of a tabulated width function.
/// @param defaultFWHM :: A default value for the FWHM to use if xVec and yVec
///        are empty.
/// @return :: The number of peaks that will be actually fitted.
size_t buildSpectrumFunction(API::CompositeFunction &spectrum,
                           const std::string &peakShape,
                           const API::FunctionValues &centresAndIntensities,
                           const std::vector<double> &xVec,
                           const std::vector<double> &yVec,
                           double fwhmVariation, double defaultFWHM) {
  if (xVec.size() != yVec.size()) {
    throw std::runtime_error("WidthX and WidthY must have the same size.");
  }
  bool useDefaultFWHM = xVec.empty();
  auto nPeaks = calculateNPeaks(centresAndIntensities);
  auto maxNPeaks = calculateMaxNPeaks(nPeaks);
  for (size_t i = 0; i < maxNPeaks; ++i) {
    auto fun = API::FunctionFactory::Instance().createFunction(peakShape);
    auto peak = boost::dynamic_pointer_cast<API::IPeakFunction>(fun);
    if (!peak) {
      throw std::runtime_error("A peak function is expected.");
    }
    if (i < nPeaks) {
      auto centre = centresAndIntensities.getCalculated(i);
      peak->fixCentre();
      peak->fixIntensity();
      peak->setCentre(centre);
      peak->setIntensity(centresAndIntensities.getCalculated(i + nPeaks));
      if (useDefaultFWHM) {
        peak->setFwhm(defaultFWHM);
      } else {
        auto fwhm = calculateWidth(centre, xVec, yVec);
        peak->setFwhm(fwhm);
        setWidthConstraint(*peak, fwhm, fwhmVariation);
      }
    } else {
      peak->setHeight(0.0);
      peak->fixAll();
      peak->setFwhm(defaultFWHM);
    }
    spectrum.addFunction(peak);
  }
  return nPeaks;
}

/// Calculate the number of visible peaks.
size_t calculateNPeaks(const API::FunctionValues &centresAndIntensities) {
  return centresAndIntensities.size() / 2;
}

/// Calculate the maximum number of peaks a spectrum can have.
size_t calculateMaxNPeaks(size_t nPeaks) {
  return nPeaks + nPeaks / 2 + 1;
}

/// Update the peaks parameters after recalculationof the crystal field.
/// @param spectrum :: A composite function containings the peaks to update.
///                    May contain other functions (background) fix indices < iFirst.
/// @param centresAndIntensities :: A FunctionValues object containing centres
///        and intensities for the peaks. First nPeaks calculated values are the
///        centres and the following nPeaks values are the intensities.
/// @param nOriginalPeaks :: Number of actual peaks the spectrum had before the update.
///                 This update can change the number of actual peaks.
/// @param iFirst :: The first index in the composite function (spectrum) at which the
///         peaks begin.
/// @return :: The new number of fitted peaks.
size_t updateSpectrumFunction(API::CompositeFunction &spectrum,
                            const FunctionValues &centresAndIntensities, size_t nOriginalPeaks,
                            size_t iFirst) {
  size_t nGoodPeaks = calculateNPeaks(centresAndIntensities);
  size_t maxNPeaks = spectrum.nFunctions() - iFirst;

  for (size_t i = 0; i < maxNPeaks; ++i) {
    auto fun = spectrum.getFunction(i + iFirst);
    auto &peak = dynamic_cast<API::IPeakFunction &>(*fun);
    if (i < nGoodPeaks) {
      peak.setCentre(centresAndIntensities.getCalculated(i));
      peak.setIntensity(centresAndIntensities.getCalculated(i + nGoodPeaks));
    } else {
      peak.setHeight(0.0);
      if (i > nOriginalPeaks) {
        peak.fixAll();
      }
    }
  }
  return nGoodPeaks;
}

} // namespace CrystalFieldUtils
} // namespace Functions
} // namespace CurveFitting
} // namespace Mantid
