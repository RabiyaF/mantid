// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2022 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include "ALFInstrumentModel.h"
#include "DllConfig.h"

#include <optional>
#include <string>
#include <vector>

#include <QWidget>

namespace MantidQt::CustomInterfaces {

class ALFInstrumentWidget;
class IALFInstrumentView;
class IALFAnalysisPresenter;

class MANTIDQT_DIRECT_DLL IALFInstrumentPresenter {

public:
  virtual QWidget *getLoadWidget() = 0;
  virtual ALFInstrumentWidget *getInstrumentView() = 0;

  virtual void subscribeAnalysisPresenter(IALFAnalysisPresenter *presenter) = 0;

  virtual void loadRunNumber() = 0;

  virtual void notifyShapeChanged(bool updateFromView = true) = 0;
  virtual void notifyTubesSelected(std::vector<std::size_t> const &detectorIndices) = 0;
};

class MANTIDQT_DIRECT_DLL ALFInstrumentPresenter final : public IALFInstrumentPresenter {

public:
  ALFInstrumentPresenter(IALFInstrumentView *view, std::unique_ptr<IALFInstrumentModel> model);

  QWidget *getLoadWidget() override;
  ALFInstrumentWidget *getInstrumentView() override;

  void subscribeAnalysisPresenter(IALFAnalysisPresenter *presenter) override;

  void loadRunNumber() override;

  void notifyShapeChanged(bool updateFromView = true) override;
  void notifyTubesSelected(std::vector<std::size_t> const &detectorIndices) override;

private:
  std::optional<std::string> loadAndTransform(const std::string &run);

  IALFAnalysisPresenter *m_analysisPresenter;

  IALFInstrumentView *m_view;
  std::unique_ptr<IALFInstrumentModel> m_model;
  bool m_redrawShapes{true};
};

} // namespace MantidQt::CustomInterfaces
