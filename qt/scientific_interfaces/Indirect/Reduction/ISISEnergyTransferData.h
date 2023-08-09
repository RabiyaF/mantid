// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2023 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include <boost/algorithm/string.hpp>

/*
  This file contains immutable data classes and constants that facilitate communication among the view, presenter, and
  model components for the ISIS Energy Transfer tab. The classes only provide getters to prevent data modification,
  ensuring the stability and integrity of the communication process.
*/

namespace MantidQt::CustomInterfaces {

class IETInputData {
public:
  IETInputData(const std::string &inputFiles = "", const bool &sumFiles = false, const bool &loadLogFiles = false,
               const bool &useCalibration = false, const std::string &calibrationWorkspace = "")
      : m_inputFiles(inputFiles), m_sumFiles(sumFiles), m_loadLogFiles(loadLogFiles), m_useCalibration(useCalibration),
        m_calibrationWorkspace(calibrationWorkspace) {}

  std::string getInputFiles() const { return m_inputFiles; }
  bool getSumFiles() const { return m_sumFiles; }
  bool getLoadLogFiles() const { return m_loadLogFiles; }
  bool getUseCalibration() const { return m_useCalibration; }
  std::string getCalibrationWorkspace() const { return m_calibrationWorkspace; }

private:
  std::string m_inputFiles;
  bool m_sumFiles;
  bool m_loadLogFiles;

  bool m_useCalibration;
  std::string m_calibrationWorkspace;
};

class IETConversionData {
public:
  IETConversionData(const double &efixed = 0.0, const int &spectraMin = 0, const int &spectraMax = 0)
      : m_efixed(efixed), m_spectraMin(spectraMin), m_spectraMax(spectraMax) {}

  double getEfixed() const { return m_efixed; }
  int getSpectraMin() const { return m_spectraMin; }
  int getSpectraMax() const { return m_spectraMax; }

private:
  double m_efixed;
  int m_spectraMin;
  int m_spectraMax;
};

class IETGroupingType {
public:
  static inline const std::string DEFAULT = "Default";
  static inline const std::string FILE = "File";
  static inline const std::string GROUPS = "Groups";
  static inline const std::string CUSTOM = "Custom";
  static inline const std::string IPF = "IPF";
  static inline const std::string ALL = "All";
  static inline const std::string INDIVIDUAL = "Individual";
};

class IETGroupingData {
public:
  IETGroupingData(const std::string &groupingType = IETGroupingType::DEFAULT, const int &nGroups = 0,
                  const std::string &groupingMapFile = "", const std::string &customGroups = "")
      : m_groupingType(groupingType), m_nGroups(nGroups), m_groupingMapFile(groupingMapFile),
        m_customGroups(customGroups) {}

  std::string getGroupingType() const { return m_groupingType; }
  int getNGroups() const { return m_nGroups; }
  std::string getGroupingMapFile() const { return m_groupingMapFile; }
  std::string getCustomGroups() const { return m_customGroups; }

private:
  std::string m_groupingType;
  int m_nGroups;
  std::string m_groupingMapFile;
  std::string m_customGroups;
};

class IETBackgroundData {
public:
  IETBackgroundData(const bool &removeBackground = false, const int &backgroundStart = 0, const int &backgroundEnd = 0)
      : m_removeBackground(removeBackground), m_backgroundStart(backgroundStart), m_backgroundEnd(backgroundEnd) {}

  bool getRemoveBackground() const { return m_removeBackground; }
  int getBackgroundStart() const { return m_backgroundStart; }
  int getBackgroundEnd() const { return m_backgroundEnd; }

private:
  bool m_removeBackground;
  int m_backgroundStart;
  int m_backgroundEnd;
};

class IETAnalysisData {
public:
  IETAnalysisData(const bool &useDetailedBalance = false, const double &detailedBalance = 0.0,
                  const bool &useScaleFactor = false, const double &scaleFactor = 0.0)
      : m_useDetailedBalance(useDetailedBalance), m_detailedBalance(detailedBalance), m_useScaleFactor(useScaleFactor),
        m_scaleFactor(scaleFactor) {}

  bool getUseDetailedBalance() const { return m_useDetailedBalance; }
  double getDetailedBalance() const { return m_detailedBalance; }
  bool getUseScaleFactor() const { return m_useScaleFactor; }
  double getScaleFactor() const { return m_scaleFactor; }

private:
  bool m_useDetailedBalance;
  double m_detailedBalance;
  bool m_useScaleFactor;
  double m_scaleFactor;
};

class IETRebinData {
public:
  IETRebinData(const bool &doNotRebin = false, const std::string &rebinType = "", const double &rebinLow = 0.0,
               const double &rebinHigh = 0.0, const double &rebinWidth = 0.0, const std::string &rebinString = "")
      : m_doNotRebin(doNotRebin), m_rebinType(rebinType), m_rebinLow(rebinLow), m_rebinHigh(rebinHigh),
        m_rebinWidth(rebinWidth), m_rebinString(rebinString) {}

  bool getDoNotRebin() const { return m_doNotRebin; }
  std::string getRebinType() const { return m_rebinType; }
  double getRebinLow() const { return m_rebinLow; }
  double getRebinHigh() const { return m_rebinHigh; }
  double getRebinWidth() const { return m_rebinWidth; }
  std::string getRebinString() const { return m_rebinString; }

private:
  bool m_doNotRebin;
  std::string m_rebinType;
  double m_rebinLow;
  double m_rebinWidth;
  double m_rebinHigh;
  std::string m_rebinString;
};

class IETOutputData {
public:
  IETOutputData(const bool &useDeltaEInWavenumber = false, const bool &foldMultipleFrames = false)
      : m_useDeltaEInWavenumber(useDeltaEInWavenumber), m_foldMultipleFrames(foldMultipleFrames) {}

  bool getUseDeltaEInWavenumber() const { return m_useDeltaEInWavenumber; }
  bool getFoldMultipleFrames() const { return m_foldMultipleFrames; }

private:
  bool m_useDeltaEInWavenumber;
  bool m_foldMultipleFrames;
};

class InstrumentData {
public:
  InstrumentData(const std::string &instrument = "", const std::string &analyser = "",
                 const std::string &reflection = "", const int &spectraMin = 0, const int &spectraMax = 0,
                 const double &efixed = 0.0, const std::string &rebin = "", const bool &useDeltaEInWavenumber = false,
                 const bool &saveNexus = false, const bool &saveASCII = false, const bool &foldMultipleFrames = false)
      : m_instrument(instrument), m_analyser(analyser), m_reflection(reflection), m_defaultSpectraMin(spectraMin),
        m_defaultSpectraMax(spectraMax), m_defaultEfixed(efixed), m_defaultRebin(rebin),
        m_defaultUseDeltaEInWavenumber(useDeltaEInWavenumber), m_defaultSaveNexus(saveNexus),
        m_defaultSaveASCII(saveASCII), m_defaultFoldMultipleFrames(foldMultipleFrames) {}

  std::string getInstrument() const { return m_instrument; }
  std::string getAnalyser() const { return m_analyser; }
  std::string getReflection() const { return m_reflection; }

  int getDefaultSpectraMin() const { return m_defaultSpectraMin; }
  int getDefaultSpectraMax() const { return m_defaultSpectraMax; }

  double getDefaultEfixed() const { return m_defaultEfixed; }

  std::string getDefaultRebin() const { return m_defaultRebin; }

  bool getDefaultUseDeltaEInWavenumber() const { return m_defaultUseDeltaEInWavenumber; }
  bool getDefaultSaveNexus() const { return m_defaultSaveNexus; }
  bool getDefaultSaveASCII() const { return m_defaultSaveASCII; }
  bool getDefaultFoldMultipleFrames() const { return m_defaultFoldMultipleFrames; }

private:
  std::string m_instrument;
  std::string m_analyser;
  std::string m_reflection;

  int m_defaultSpectraMin;
  int m_defaultSpectraMax;

  double m_defaultEfixed;

  std::string m_defaultRebin;

  bool m_defaultUseDeltaEInWavenumber;
  bool m_defaultSaveNexus;
  bool m_defaultSaveASCII;
  bool m_defaultFoldMultipleFrames;
};

class IETRunData {
public:
  IETRunData(const IETInputData &inputData, const IETConversionData &conversionData,
             const IETGroupingData &groupingData, const IETBackgroundData &backgroundData,
             const IETAnalysisData &analysisData, const IETRebinData &rebinData, const IETOutputData &outputData)
      : m_inputData(inputData), m_conversionData(conversionData), m_groupingData(groupingData),
        m_backgroundData(backgroundData), m_analysisData(analysisData), m_rebinData(rebinData),
        m_outputData(outputData) {}

  IETInputData getInputData() const { return m_inputData; }
  IETConversionData getConversionData() const { return m_conversionData; }
  IETGroupingData getGroupingData() const { return m_groupingData; }
  IETBackgroundData getBackgroundData() const { return m_backgroundData; }
  IETAnalysisData getAnalysisData() const { return m_analysisData; }
  IETRebinData getRebinData() const { return m_rebinData; }
  IETOutputData getOutputData() const { return m_outputData; }

private:
  IETInputData m_inputData;
  IETConversionData m_conversionData;
  IETGroupingData m_groupingData;
  IETBackgroundData m_backgroundData;
  IETAnalysisData m_analysisData;
  IETRebinData m_rebinData;
  IETOutputData m_outputData;
};

class IETPlotData {
public:
  IETPlotData(const IETInputData &inputData, const IETConversionData &conversionData,
              const IETBackgroundData &backgroundData)
      : m_inputData(inputData), m_conversionData(conversionData), m_backgroundData(backgroundData) {}

  IETInputData getInputData() const { return m_inputData; }
  IETConversionData getConversionData() const { return m_conversionData; }
  IETBackgroundData getBackgroundData() const { return m_backgroundData; }

private:
  IETInputData m_inputData;
  IETConversionData m_conversionData;
  IETBackgroundData m_backgroundData;
};

class IETSaveData {
public:
  IETSaveData(const bool &nexus = false, const bool &spe = false, const bool &nxspe = false, const bool &ascii = false,
              const bool &aclimax = false, const bool &daveGrp = false)
      : m_nexus(nexus), m_spe(spe), m_nxspe(nxspe), m_ascii(ascii), m_aclimax(aclimax), m_daveGrp(daveGrp) {}

  bool getNexus() const { return m_nexus; }
  bool getSPE() const { return m_spe; }
  bool getNXSPE() const { return m_nxspe; }
  bool getASCII() const { return m_ascii; }
  bool getAclimax() const { return m_aclimax; }
  bool getDaveGrp() const { return m_daveGrp; }

private:
  bool m_nexus;
  bool m_spe;
  bool m_nxspe;
  bool m_ascii;
  bool m_aclimax;
  bool m_daveGrp;
};

class IETGroupOption {
public:
  static inline const std::string UNGROUPED = "Ungrouped";
  static inline const std::string GROUP = "Grouped";
  static inline const std::string SAMPLECHANGERGROUPED = "Sample changer grouped";
};

class IETRebinType {
public:
  static inline const std::string SINGLE = "Single";
  static inline const std::string MULTIPLE = "Multiple";
};

class IETGroupingConstants {
public:
  static inline const std::string DEFAULT_GROUPING_FILENAME = "custom_detector_grouping.xml";
  static inline const std::string GROUPING_WS_NAME = "Custom_grouping_workspace";
};

} // namespace MantidQt::CustomInterfaces