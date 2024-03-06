// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2023 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include "DllConfig.h"
#include "ISISEnergyTransferData.h"
#include "ISISEnergyTransferValidator.h"
#include "MantidAPI/Algorithm.h"
#include "MantidQtWidgets/Common/BatchAlgorithmRunner.h"
#include <typeinfo>

using namespace Mantid::API;

namespace MantidQt {
namespace CustomInterfaces {
class MANTIDQT_INDIRECT_DLL IETModel {
public:
  IETModel();
  ~IETModel() = default;

  void setInstrumentProperties(IAlgorithmRuntimeProps &properties, InstrumentData const &instData);
  void setInputProperties(IAlgorithmRuntimeProps &properties, IETInputData const &inputData);
  void setConversionProperties(IAlgorithmRuntimeProps &properties, IETConversionData const &conversionData,
                               std::string const &instrument);
  void setBackgroundProperties(IAlgorithmRuntimeProps &properties, IETBackgroundData const &backgroundData);
  void setRebinProperties(IAlgorithmRuntimeProps &properties, IETRebinData const &rebinData);
  void setAnalysisProperties(IAlgorithmRuntimeProps &properties, IETAnalysisData const &analysisData);
  void setOutputProperties(IAlgorithmRuntimeProps &properties, IETOutputData const &outputData,
                           std::string const &outputGroupName);
  std::string getOuputGroupName(InstrumentData const &instData, std::string const &inputFiles);

  std::vector<std::string> validateRunData(IETRunData const &runData, std::size_t const &defaultSpectraMin,
                                           std::size_t const &defaultSpectraMax);
  std::vector<std::string> validatePlotData(IETPlotData const &plotData);

  std::string runIETAlgorithm(MantidQt::API::BatchAlgorithmRunner *batchAlgoRunner, InstrumentData const &instData,
                              IETRunData &runParams);
  std::deque<MantidQt::API::IConfiguredAlgorithm_sptr> plotRawAlgorithmQueue(InstrumentData const &instData,
                                                                             IETPlotData const &plotData) const;

  void saveWorkspace(std::string const &workspaceName, IETSaveData const &saveData);
  void saveDaveGroup(std::string const &workspaceName, std::string const &outputName);
  void saveAclimax(std::string const &workspaceName, std::string const &outputName,
                   std::string const &xUnits = "DeltaE_inWavenumber");
  void save(std::string const &algorithmName, std::string const &workspaceName, std::string const &outputName,
            int const version = -1, std::string const &separator = "");

  void createGroupingWorkspace(std::string const &instrumentName, std::string const &analyser,
                               std::string const &customGrouping, std::string const &outputName);
  double loadDetailedBalance(std::string const &filename);

  std::vector<std::string> groupWorkspaces(std::string const &groupName, std::string const &instrument,
                                           std::string const &groupOption, bool const shouldGroup);
  void ungroupWorkspace(std::string const &workspaceName);
  void groupWorkspaceBySampleChanger(std::string const &workspaceName);

private:
  std::deque<MantidQt::API::IConfiguredAlgorithm_sptr>
  plotRawAlgorithmQueue(std::string const &rawFile, std::string const &basename, std::string const &instrumentName,
                        std::vector<int> const &detectorList, IETBackgroundData const &backgroundData) const;
};
} // namespace CustomInterfaces
} // namespace MantidQt