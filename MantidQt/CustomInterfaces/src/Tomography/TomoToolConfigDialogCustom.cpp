#include "MantidQtCustomInterfaces/Tomography/TomoToolConfigDialogCustom.h"
#include "MantidQtCustomInterfaces/Tomography/ToolConfigCustom.h"

namespace MantidQt {
namespace CustomInterfaces {

const std::string TomoToolConfigDialogCustom::DEFAULT_TOOL_NAME =
    "Custom command";

// custom tool doesn't have a default method
const std::string TomoToolConfigDialogCustom::DEFAULT_TOOL_METHOD = "";

std::string TomoToolConfigDialogCustom::m_backupCommandLine = "";

void TomoToolConfigDialogCustom::setupToolSettingsFromPaths() {

  if (m_isInitialised) {
    // None of the other paths matter, because the user could've changed
    // them, so ignore them and load the current ones on the dialogue
    QString run = m_customUi.lineEdit_runnable->text(); // current path
    QString opts =
        m_customUi.textEdit_cl_opts->toPlainText(); // current commands

    // update the settings with the newest information
    m_toolSettings = std::make_shared<ToolConfigCustom>(run.toStdString(),
                                                        opts.toStdString());
  } else {
    // create settings with the default values
    m_toolSettings = std::make_shared<ToolConfigCustom>(m_runPath, "--help");
  }
}

void TomoToolConfigDialogCustom::setupMethodSelected() {

  // sets the current runnable path, overriding the default one
  m_customUi.lineEdit_runnable->setText(QString::fromStdString(m_runPath));
}

void TomoToolConfigDialogCustom::setupDialogUi() {
  m_customUi.setupUi(m_dialog);

  if (m_backupCommandLine != "") {
    m_customUi.textEdit_cl_opts->setText(
        QString::fromStdString(m_backupCommandLine));
  }

  // get default options from command line
  QString opts = m_customUi.textEdit_cl_opts->toPlainText();

  // create the default settings
  m_toolSettings = std::shared_ptr<ToolConfigCustom>(
      new ToolConfigCustom(m_runPath, opts.toStdString()));
}

void TomoToolConfigDialogCustom::initialiseDialog() { m_dialog = new QDialog; }

void TomoToolConfigDialogCustom::handleDialogResult(int result) {
  if (QDialog::Accepted == result) {
    // if accepted we want to save the information
    m_backupCommandLine =
        m_customUi.textEdit_cl_opts->toPlainText().toStdString();
    setupToolSettingsFromPaths();
  }
}
int TomoToolConfigDialogCustom::executeQt() { return m_dialog->exec(); }
} // CustomInterfaces
} // MantidQt