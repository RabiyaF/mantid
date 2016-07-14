#include "MantidQtCustomInterfaces/Muon/MuonAnalysisFitFunctionPresenter.h"
#include "MantidQtCustomInterfaces/MultiDatasetFit/MDFEditLocalParameterDialog.h"
#include "MantidAPI/IFunction.h"

using MantidQt::CustomInterfaces::MDF::EditLocalParameterDialog;
using MantidQt::MantidWidgets::IFunctionBrowser;
using MantidQt::MantidWidgets::IMuonFitFunctionControl;

namespace MantidQt {
namespace CustomInterfaces {

/**
 * Constructor
 * @param parent :: [input] Parent dialog (MuonAnalysis)
 * @param fitBrowser :: [input] Non-owning pointer to muon fit property browser
 * @param funcBrowser :: [input] Non-owning pointer to function browser
 */
MuonAnalysisFitFunctionPresenter::MuonAnalysisFitFunctionPresenter(
    QObject *parent, IMuonFitFunctionControl *fitBrowser,
    IFunctionBrowser *funcBrowser)
    : QObject(parent), m_fitBrowser(fitBrowser), m_funcBrowser(funcBrowser) {
  doConnect();
}

/**
 * Connect up signals and slots
 * Abstract base class is not a QObject, so attempt a cast.
 * (Its derived classes are QObjects).
 */
void MuonAnalysisFitFunctionPresenter::doConnect() {
  if (const QObject *fitBrowser = dynamic_cast<QObject *>(m_fitBrowser)) {
    connect(fitBrowser, SIGNAL(functionUpdateRequested()), this,
            SLOT(updateFunction()));
    connect(fitBrowser, SIGNAL(functionUpdateAndFitRequested(bool)), this,
            SLOT(updateFunctionAndFit(bool)));
    connect(fitBrowser, SIGNAL(fittingDone(const QString &)), this,
            SLOT(handleFitFinished(const QString &)));
    connect(fitBrowser, SIGNAL(functionCleared()), this,
            SLOT(handleModelCleared()));
    connect(fitBrowser, SIGNAL(errorsEnabled(bool)), this,
            SLOT(handleErrorsEnabled(bool)));
    connect(fitBrowser, SIGNAL(fitUndone()), this, SLOT(handleFitFinished()));
    connect(fitBrowser, SIGNAL(functionLoaded(const QString &)), this,
            SLOT(handleFunctionLoaded(const QString &)));
    connect(fitBrowser, SIGNAL(workspacesToFitChanged(int)), this,
            SLOT(updateNumberOfDatasets(int)));
    connect(fitBrowser, SIGNAL(userChangedDatasetIndex(int)), this,
            SLOT(handleDatasetIndexChanged(int)));
  }
  setParameterUpdates(true);
}

/**
 * Switch signals on/off for updating the function browser
 * @param on :: [input] On/off for signals and slots
 */
void MuonAnalysisFitFunctionPresenter::setParameterUpdates(bool on) {
  if (const QObject *funcBrowser = dynamic_cast<QObject *>(m_funcBrowser)) {
    if (on) {
      connect(funcBrowser, SIGNAL(functionStructureChanged()), this,
              SLOT(updateFunction()));
      connect(funcBrowser,
              SIGNAL(parameterChanged(const QString &, const QString &)), this,
              SLOT(handleParameterEdited(const QString &, const QString &)));
      connect(funcBrowser, SIGNAL(localParameterButtonClicked(const QString &)),
              this, SLOT(editLocalParameterClicked(const QString &)));
    } else {
      disconnect(funcBrowser, SIGNAL(functionStructureChanged()), this,
                 SLOT(updateFunction()));
      disconnect(funcBrowser,
                 SIGNAL(parameterChanged(const QString &, const QString &)),
                 this,
                 SLOT(handleParameterEdited(const QString &, const QString &)));
      disconnect(funcBrowser,
                 SIGNAL(localParameterButtonClicked(const QString &)), this,
                 SLOT(editLocalParameterClicked(const QString &)));
    }
  }
}

/**
 * Queries function browser and updates function in fit property browser.
 */
void MuonAnalysisFitFunctionPresenter::updateFunction() {
  // Check there is still a function to update
  const auto funcString = m_funcBrowser->getFunctionString();
  const Mantid::API::IFunction_sptr function =
      funcString.isEmpty() ? nullptr // last function has been removed
                           : m_funcBrowser->getGlobalFunction();
  m_fitBrowser->setFunction(function);
}

/**
 * Called when a fit is requested.
 * Queries function browser and updates function in fit property browser.
 * Then calls fit or sequential fit as controlled by argument.
 * @param sequential :: [input] Whether a regular or sequential fit was
 * requested.
 */
void MuonAnalysisFitFunctionPresenter::updateFunctionAndFit(bool sequential) {
  updateFunction();
  if (sequential) {
    m_fitBrowser->runSequentialFit();
  } else {
    m_fitBrowser->runFit();
  }
}

/**
 * Called when fit finished OR undone.
 * Updates parameters displayed in function browser from the fit results.
 * In the case of "fit undone", this has the effect of resetting them, and also
 * removing the errors.
 * @param wsName :: [input] workspace name - empty if fit undone
 */
void MuonAnalysisFitFunctionPresenter::handleFitFinished(
    const QString &wsName) {
  const auto function = m_fitBrowser->getFunction();
  // We are updating function browser from fit browser, so turn off updates to
  // fit browser when function browser is updated...
  setParameterUpdates(false);
  m_funcBrowser->updateMultiDatasetParameters(*function);
  setParameterUpdates(true); // reset signals and slots
  if (wsName.isEmpty()) {
    // No fitted workspace: a fit was undone so clear the errors
    m_funcBrowser->clearErrors();
  }
}

/**
 * Called when user edits a parameter in the function browser.
 * Updates the parameter value in the fit property browser.
 * @param funcIndex :: [input] index of the function
 * @param paramName :: [input] parameter name
 */
void MuonAnalysisFitFunctionPresenter::handleParameterEdited(
    const QString &funcIndex, const QString &paramName) {
  const double value = m_funcBrowser->getParameter(funcIndex, paramName);
  m_fitBrowser->setParameterValue(funcIndex, paramName, value);
}

/**
 * Called when "Clear model" selected on the fit property browser.
 * Clears the function set in the function browser.
 */
void MuonAnalysisFitFunctionPresenter::handleModelCleared() {
  m_funcBrowser->clear();
}

/**
 * Called when user shows/hides parameter errors.
 * Pass this change on to the function browser.
 * @param enabled :: [input] enabled/disabled state of param errors
 */
void MuonAnalysisFitFunctionPresenter::handleErrorsEnabled(bool enabled) {
  m_funcBrowser->setErrorsEnabled(enabled);
}

/**
 * Called when a saved setup is loaded into the fit property browser.
 * Update the function browser with this loaded function.
 * @param funcString :: [input] Loaded function as a string
 */
void MuonAnalysisFitFunctionPresenter::handleFunctionLoaded(
    const QString &funcString) {
  m_funcBrowser->clear();
  m_funcBrowser->setFunction(funcString);
}

/**
 * Called when the number of datasets to fit is changed in the model.
 * Update the view with the new number of datasets.
 * @param nDatasets :: [input] Number of datasets to fit
 */
void MuonAnalysisFitFunctionPresenter::updateNumberOfDatasets(int nDatasets) {
  m_funcBrowser->setNumberOfDatasets(nDatasets);
}

/**
 * Called when user clicks the "edit local parameter" button in the function
 * browser.
 * Launches the Edit Local Parameter dialog and deals with the input from it.
 * @param parName :: [input] Name of parameter that button was clicked for
 */
void MuonAnalysisFitFunctionPresenter::editLocalParameterClicked(
    const QString &parName) {
  const int nDatasets = m_funcBrowser->getNumberOfDatasets();
  // get names of workspaces
  QStringList wsNames;
  for (const auto &name : m_fitBrowser->getWorkspaceNamesToFit()) {
    wsNames.append(QString::fromStdString(name));
  }
  // spectrum indices are all zero
  std::vector<size_t> wsIndices(nDatasets, 0);

  EditLocalParameterDialog dialog(nullptr, m_funcBrowser, parName, wsNames,
                                  wsIndices);
  if (dialog.exec() == QDialog::Accepted) {
    const auto values = dialog.getValues();
    const auto fixes = dialog.getFixes();
    const auto ties = dialog.getTies();
    for (int i = 0; i < nDatasets; i++) {
      m_funcBrowser->setLocalParameterValue(parName, i, values[i]);
      m_funcBrowser->setLocalParameterFixed(parName, i, fixes[i]);
      m_funcBrowser->setLocalParameterTie(parName, i, ties[i]);
    }
  }
}

/**
 * Called when user changes selected dataset.
 * Update current dataset in function browser.
 * @param index :: [input] Selected dataset index
 */
void MuonAnalysisFitFunctionPresenter::handleDatasetIndexChanged(int index) {
  // Avoid signals being sent to fit browser while this changes
  setParameterUpdates(false);
  m_funcBrowser->setCurrentDataset(index);
  setParameterUpdates(true);
}

} // namespace CustomInterfaces
} // namespace MantidQt
