// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +

#include "MantidAlgorithms/CombineDiffCal.h"
#include "MantidAPI/SpectrumInfo.h"
#include "MantidAPI/TableRow.h"
#include "MantidDataObjects/OffsetsWorkspace.h"
#include "MantidDataObjects/TableWorkspace.h"

namespace Mantid {
namespace Algorithms {
using Mantid::API::WorkspaceProperty;
using Mantid::Kernel::Direction;

// Register the algorithm into the AlgorithmFactory
DECLARE_ALGORITHM(CombineDiffCal)

//----------------------------------------------------------------------------------------------

/// Algorithms name for identification. @see Algorithm::name
const std::string CombineDiffCal::name() const { return "CombineDiffCal"; }

/// Algorithm's version for identification. @see Algorithm::version
int CombineDiffCal::version() const { return 1; }

/// Algorithm's category for identification. @see Algorithm::category
const std::string CombineDiffCal::category() const { return "Diffraction\\Utility"; }

/// Algorithm's summary for use in the GUI and help. @see Algorithm::summary
const std::string CombineDiffCal::summary() const {
  return "Combine a per-pixel calibration with a grouped spectrum calibration";
}

//----------------------------------------------------------------------------------------------
/** Initialize the algorithm's properties.
 */
void CombineDiffCal::init() {
  declareProperty(
      std::make_unique<WorkspaceProperty<DataObjects::TableWorkspace>>("PixelCalibration", "", Direction::Input),
      "OffsetsWorkspace generated from cross-correlation. This is the source of DIFCpixel.");
  declareProperty(
      std::make_unique<WorkspaceProperty<DataObjects::TableWorkspace>>("GroupedCalibration", "", Direction::Input),
      "DiffCal table generated from calibrating grouped spectra. This is the source of DIFCgroup.");
  declareProperty(
      std::make_unique<WorkspaceProperty<DataObjects::Workspace2D>>("CalibrationWorkspace", "", Direction::Input),
      "Workspace where conversion from d-spacing to time-of-flight for each spectrum is determined from. This is the "
      "source of DIFCarb.");
  declareProperty(
      std::make_unique<WorkspaceProperty<DataObjects::TableWorkspace>>("OutputWorkspace", "", Direction::Output),
      "DiffCal table generated from calibrating grouped spectra");
}

std::map<std::string, std::string> CombineDiffCal::validateInputs() {
  std::map<std::string, std::string> results;

  return results;
}
// Per Pixel:
//
// DIFC{eff} = (DIFC{pd}/DIFC{arb}) * DIFC{prev}
//
// DIFC{eff} = Output of this Alg, the combined DIFC
// DIFC{pd} = The DIFC produced by PDCalibration, found in the "GroupedCalibration"
// DIFC{arb} = found in the "CalibrationWorkspace" param
// DIFC{prev} = The previous DIFCs, found in "PixelCalibration", as per description this was the set generated by CC

//----------------------------------------------------------------------------------------------
/** Execute the algorithm.
 */
void CombineDiffCal::exec() {
  const DataObjects::Workspace2D_sptr calibrationWS = getProperty("CalibrationWorkspace");
  const DataObjects::TableWorkspace_sptr groupedCalibrationWS = getProperty("GroupedCalibration");
  const DataObjects::TableWorkspace_sptr pixelCalibrationWS = getProperty("PixelCalibration");

  DataObjects::TableWorkspace_sptr outputWorkspace = std::make_shared<DataObjects::TableWorkspace>();
  outputWorkspace->addColumn("int", "detid");
  outputWorkspace->addColumn("double", "difc");

  Mantid::API::TableRow groupedCalibrationRow = groupedCalibrationWS->getFirstRow();
  Mantid::API::TableRow pixelCalibrationRow = pixelCalibrationWS->getFirstRow();
  int calibrationIndex = 0;
  do {
    double value = (groupedCalibrationRow.Double(1) /
                    calibrationWS->spectrumInfo().diffractometerConstants(calibrationWS->getIndicesFromDetectorIDs(
                        {pixelCalibrationRow.Int(0)})[0])[Kernel::UnitParams::difc]) *
                   pixelCalibrationRow.Double(1);

    Mantid::API::TableRow newRow = outputWorkspace->appendRow();
    newRow << pixelCalibrationRow.Int(0) << value;
    ++calibrationIndex;
  } while (groupedCalibrationRow.next() && pixelCalibrationRow.next());

  setProperty("OutputWorkspace", outputWorkspace);
}

} // namespace Algorithms
} // namespace Mantid
