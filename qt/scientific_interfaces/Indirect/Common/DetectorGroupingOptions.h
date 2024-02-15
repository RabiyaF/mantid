// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2024 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include "MantidAPI/AlgorithmRuntimeProps.h"
#include "ui_DetectorGroupingOptions.h"

#include <string>

#include <QObject>
#include <QString>
#include <QWidget>

namespace MantidQt {
namespace CustomInterfaces {

class DetectorGroupingOptions : public QWidget {
  Q_OBJECT

public:
  DetectorGroupingOptions(QWidget *parent);

  void includeOption(QString const &option, bool include);

  std::string groupingMethod() const;
  std::string mapFile() const;
  std::string customGrouping() const;
  int nGroups() const;

  std::unique_ptr<Mantid::API::AlgorithmRuntimeProps> groupingProperties() const;

signals:
  void saveCustomGrouping(std::string const &customGrouping);

private slots:
  void handleGroupingMethodChanged(QString const &method);
  void emitSaveCustomGrouping();

private:
  int optionIndex(QString const &option) const;
  bool isOptionHidden(QString const &option) const;

  Ui::DetectorGroupingWidget m_uiForm;
};

} // namespace CustomInterfaces
} // namespace MantidQt