#ifndef MANTIDQTCUSTOMINTERFACES_STRETCH_H_
#define MANTIDQTCUSTOMINTERFACES_STRETCH_H_

#include "ui_Stretch.h"
#include "IndirectBayesTab.h"

namespace MantidQt {
namespace CustomInterfaces {
class DLLExport Stretch : public IndirectBayesTab {
  Q_OBJECT

public:
  Stretch(QWidget *parent = 0);

  // Inherited methods from IndirectBayesTab
  void setup() override;
  bool validate() override;
  void run() override;
  /// Load default settings into the interface
  void loadSettings(const QSettings &settings) override;


private slots:
  /// Slot for when the min range on the range selector changes
  void minValueChanged(double min);
  /// Slot for when the min range on the range selector changes
  void maxValueChanged(double max);
  /// Slot to update the guides when the range properties change
  void updateProperties(QtProperty *prop, double val) override;
  /// Slot to handle when a new sample file is available
  void handleSampleInputReady(const QString &filename);

private:
  // The ui form
  Ui::Stretch m_uiForm;
  // Algorithm
  Mantid::API::IAlgorithm_sptr m_StretchAlg;
};
} // namespace CustomInterfaces
} // namespace MantidQt

#endif
