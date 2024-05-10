// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2022 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include "Common/IndirectDataValidationHelper.h"
#include "DllConfig.h"
#include "MantidGeometry/IComponent.h"
#include "MantidQtWidgets/Common/BatchAlgorithmRunner.h"
#include "MantidQtWidgets/Common/QtPropertyBrowser/QtTreePropertyBrowser"
#include <typeinfo>

using namespace Mantid::API;

namespace MantidQt {
namespace CustomInterfaces {

class MANTIDQT_INELASTIC_DLL ISqwModel {

public:
  virtual ~ISqwModel() = default;
  virtual void setupRebinAlgorithm(MantidQt::API::BatchAlgorithmRunner *batchAlgoRunner) = 0;
  virtual void setupSofQWAlgorithm(MantidQt::API::BatchAlgorithmRunner *batchAlgoRunner) = 0;
  virtual void setupAddSampleLogAlgorithm(MantidQt::API::BatchAlgorithmRunner *batchAlgoRunner) = 0;
  virtual void setInputWorkspace(const std::string &workspace) = 0;
  virtual void setQMin(double qMin) = 0;
  virtual void setQWidth(double qWidth) = 0;
  virtual void setQMax(double qMax) = 0;
  virtual void setEMin(double eMin) = 0;
  virtual void setEWidth(double eWidth) = 0;
  virtual void setEMax(double eMax) = 0;
  virtual void setEFixed(const double eFixed) = 0;
  virtual void setRebinInEnergy(bool scale) = 0;
  virtual std::string getEFixedFromInstrument(std::string const &instrumentName, std::string analyser,
                                              std::string const &reflection) = 0;
  virtual std::string getOutputWorkspace() = 0;
  virtual MatrixWorkspace_sptr getRqwWorkspace() = 0;
  virtual UserInputValidator validate(std::tuple<double, double> const qRange,
                                      std::tuple<double, double> const eRange) = 0;
  virtual MatrixWorkspace_sptr loadInstrumentWorkspace(const std::string &instrumentName, const std::string &analyser,
                                                       const std::string &reflection) = 0;
};

class MANTIDQT_INELASTIC_DLL SqwModel : public ISqwModel {

public:
  SqwModel();
  ~SqwModel() = default;
  void setupRebinAlgorithm(MantidQt::API::BatchAlgorithmRunner *batchAlgoRunner) override;
  void setupSofQWAlgorithm(MantidQt::API::BatchAlgorithmRunner *batchAlgoRunner) override;
  void setupAddSampleLogAlgorithm(MantidQt::API::BatchAlgorithmRunner *batchAlgoRunner) override;
  void setInputWorkspace(const std::string &workspace) override;
  void setQMin(double qMin) override;
  void setQWidth(double qWidth) override;
  void setQMax(double qMax) override;
  void setEMin(double eMin) override;
  void setEWidth(double eWidth) override;
  void setEMax(double eMax) override;
  void setEFixed(const double eFixed) override;
  void setRebinInEnergy(bool scale) override;
  std::string getEFixedFromInstrument(std::string const &instrumentName, std::string analyser,
                                      std::string const &reflection) override;
  std::string getOutputWorkspace() override;
  MatrixWorkspace_sptr getRqwWorkspace() override;
  UserInputValidator validate(std::tuple<double, double> const qRange,
                              std::tuple<double, double> const eRange) override;
  MatrixWorkspace_sptr loadInstrumentWorkspace(const std::string &instrumentName, const std::string &analyser,
                                               const std::string &reflection) override;

private:
  std::string m_inputWorkspace;
  std::string m_baseName;
  double m_eFixed;
  double m_qLow;
  double m_qWidth;
  double m_qHigh;
  double m_eLow;
  double m_eWidth;
  double m_eHigh;
  bool m_rebinInEnergy;
};
} // namespace CustomInterfaces
} // namespace MantidQt