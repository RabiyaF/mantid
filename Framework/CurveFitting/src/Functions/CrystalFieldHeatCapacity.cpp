#include "MantidCurveFitting/Functions/CrystalFieldHeatCapacity.h"
#include "MantidCurveFitting/Functions/CrystalFieldPeaksBase.h"
#include "MantidCurveFitting/FortranDefs.h"
#include "MantidAPI/FunctionFactory.h"
#include "MantidAPI/FunctionValues.h"
#include "MantidAPI/FunctionDomain.h"
#include "MantidAPI/FunctionDomain1D.h"
#include "MantidAPI/IFunction1D.h"
#include "MantidAPI/Jacobian.h"
#include "MantidKernel/Exception.h"
#include "MantidKernel/PhysicalConstants.h"
#include <cmath>

namespace Mantid {
namespace CurveFitting {
namespace Functions {

DECLARE_FUNCTION(CrystalFieldHeatCapacity)

CrystalFieldHeatCapacity::CrystalFieldHeatCapacity()
    : CrystalFieldPeaksBase(), API::IFunction1D(), setDirect(false) {}

// Sets the eigenvectors / values directly
void CrystalFieldHeatCapacity::set_eigensystem(const DoubleFortranVector &en_in,
                                               const ComplexFortranMatrix &wf_in) {
  setDirect = true;
  en = en_in;
  wf = wf_in;
}

// Does the actual calculation of the heat capacity
// Public method so can be called in CrystalFieldMultiSpectrum
void CrystalFieldHeatCapacity::calculate(double *out,
                                         const double *xValues,
                                         const size_t nData,
                                         const ComplexFortranMatrix &,
                                         const DoubleFortranVector &en) const {
  const double k_B = PhysicalConstants::BoltzmannConstant; // in meV/K
  // Want output in J/K/mol
  const double convfact = PhysicalConstants::N_A * PhysicalConstants::meV;
  int nlevels = en.len();
  for (size_t iT = 0; iT < nData; iT++) {
    double expfact; 
    double Z = 0.;
    double U = 0.;
    double U2 = 0.; 
    const double beta = 1 / (k_B * xValues[iT]);
    for (auto iE = 0; iE < nlevels; iE++) {
      expfact = exp(-beta * en(iE));
      Z += expfact;
      U += en(iE) * expfact;
      U2 += en(iE) * en(iE) * expfact;
    }
    U /= Z; 
    U2 /= Z; 
    out[iT] = ( (U2 - U*U) / (k_B * xValues[iT]*xValues[iT]) ) * convfact;
  }
}

void CrystalFieldHeatCapacity::function1D(double *out,
                                          const double *xValues,
                                          const size_t nData) const {
  if (!setDirect) {
    // Because this method is const, we can change the stored en / wf
    // Use temporary variables instead.
    DoubleFortranVector en_;
    ComplexFortranMatrix wf_;
    int nre = 0; 
    calculateEigenSystem(en_, wf_, nre);
    calculate(out, xValues, nData, wf_, en_);
  }
  else {
    // Use stored values
    calculate(out, xValues, nData, wf, en);
  }
}

} // namespace Functions
} // namespace CurveFitting
} // namespace Mantid

