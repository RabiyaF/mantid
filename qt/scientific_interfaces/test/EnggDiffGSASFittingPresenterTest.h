#ifndef MANTID_CUSTOM_INTERFACES_ENGGDIFFGSASFITTINGPRESENTERTEST_H_
#define MANTID_CUSTOM_INTERFACES_ENGGDIFFGSASFITTINGPRESENTERTEST_H_

#include "../EnggDiffraction/EnggDiffGSASFittingPresenter.h"
#include "EnggDiffGSASFittingModelMock.h"
#include "EnggDiffGSASFittingViewMock.h"

#include "MantidAPI/WorkspaceFactory.h"
#include "MantidKernel/make_unique.h"
#include "MantidTestHelpers/WorkspaceCreationHelper.h"

#include <cxxtest/TestSuite.h>

using namespace MantidQt::CustomInterfaces;
using testing::Return;
using testing::Throw;

class EnggDiffGSASFittingPresenterTest : public CxxTest::TestSuite {

public:
  void test_loadValidFile() {
    auto presenter = setUpPresenter();
    const auto filename = "Valid filename";

    EXPECT_CALL(*m_mockViewPtr, getFocusedFileNames())
        .Times(1)
        .WillOnce(Return(std::vector<std::string>({filename})));
    EXPECT_CALL(*m_mockModelPtr, loadFocusedRun(filename))
        .Times(1)
        .WillOnce(Return(""));

    const std::vector<RunLabel> runLabels({RunLabel(123, 1)});

    EXPECT_CALL(*m_mockModelPtr, getRunLabels())
        .Times(1)
        .WillOnce(Return(runLabels));
    EXPECT_CALL(*m_mockViewPtr, updateRunList(runLabels)).Times(1);

    EXPECT_CALL(*m_mockViewPtr, userWarning(testing::_, testing::_)).Times(0);

    presenter->notify(IEnggDiffGSASFittingPresenter::LoadRun);
    assertMocksUsedCorrectly();
  }

  void test_loadInvalidFile() {
    auto presenter = setUpPresenter();
    const auto filename = "Invalid filename";

    EXPECT_CALL(*m_mockViewPtr, getFocusedFileNames())
        .Times(1)
        .WillOnce(Return(std::vector<std::string>({filename})));

    EXPECT_CALL(*m_mockModelPtr, loadFocusedRun(filename))
        .Times(1)
        .WillOnce(Return("Failure message"));

    EXPECT_CALL(*m_mockModelPtr, getRunLabels()).Times(0);

    EXPECT_CALL(
        *m_mockViewPtr,
        userWarning("Load failed", "Failure message"))
        .Times(1);

    presenter->notify(IEnggDiffGSASFittingPresenter::LoadRun);
    assertMocksUsedCorrectly();
  }

  void test_selectValidRun() {
    auto presenter = setUpPresenter();
    const RunLabel selectedRunLabel(123, 1);
    EXPECT_CALL(*m_mockViewPtr, getSelectedRunLabel())
        .Times(1)
        .WillOnce(Return(selectedRunLabel));

    const boost::optional<Mantid::API::MatrixWorkspace_sptr> sampleWorkspace(
        WorkspaceCreationHelper::create2DWorkspaceBinned(1, 100));

    EXPECT_CALL(*m_mockModelPtr, getFocusedWorkspace(selectedRunLabel))
        .Times(1)
        .WillOnce(Return(sampleWorkspace));

    EXPECT_CALL(*m_mockViewPtr, resetCanvas()).Times(1);
    EXPECT_CALL(*m_mockViewPtr, userWarning(testing::_, testing::_)).Times(0);

    presenter->notify(IEnggDiffGSASFittingPresenter::SelectRun);
    assertMocksUsedCorrectly();
  }

  void test_selectInvalidRun() {
    auto presenter = setUpPresenter();
    const RunLabel selectedRunLabel(123, 1);
    EXPECT_CALL(*m_mockViewPtr, getSelectedRunLabel())
        .Times(1)
        .WillOnce(Return(selectedRunLabel));

    EXPECT_CALL(*m_mockModelPtr, getFocusedWorkspace(selectedRunLabel))
        .Times(1)
        .WillOnce(Return(boost::none));

    EXPECT_CALL(*m_mockViewPtr,
                userError("Invalid run identifier",
                          "Tried to access invalid run, runNumber 123 and "
                          "bank ID 1. Please contact the development team"));

    EXPECT_CALL(*m_mockViewPtr, resetCanvas()).Times(0);

    presenter->notify(IEnggDiffGSASFittingPresenter::SelectRun);
    assertMocksUsedCorrectly();
  }

  void test_selectValidRunPlotFitResults() {
    auto presenter = setUpPresenter();
    const RunLabel selectedRunLabel(123, 1);
    EXPECT_CALL(*m_mockViewPtr, getSelectedRunLabel())
        .Times(1)
        .WillOnce(Return(selectedRunLabel));

    const boost::optional<Mantid::API::MatrixWorkspace_sptr> sampleWorkspace(
        WorkspaceCreationHelper::create2DWorkspaceBinned(1, 100));
    EXPECT_CALL(*m_mockModelPtr, getFocusedWorkspace(selectedRunLabel))
        .Times(1)
        .WillOnce(Return(sampleWorkspace));
    EXPECT_CALL(*m_mockViewPtr, showRefinementResultsSelected())
        .Times(1)
        .WillOnce(Return(true));
    EXPECT_CALL(*m_mockModelPtr, hasFittedPeaksForRun(selectedRunLabel))
        .Times(1)
        .WillOnce(Return(true));

    EXPECT_CALL(*m_mockModelPtr, getFittedPeaks(selectedRunLabel))
        .Times(1)
        .WillOnce(Return(sampleWorkspace));

    const boost::optional<Mantid::API::ITableWorkspace_sptr> emptyTableWS(
        Mantid::API::WorkspaceFactory::Instance().createTable());

    EXPECT_CALL(*m_mockModelPtr, getLatticeParams(selectedRunLabel))
        .Times(1)
        .WillOnce(Return(emptyTableWS));

    const boost::optional<double> rwp = 50.0;
    EXPECT_CALL(*m_mockModelPtr, getRwp(selectedRunLabel))
        .Times(1)
        .WillOnce(Return(rwp));

    EXPECT_CALL(*m_mockViewPtr, resetCanvas()).Times(1);
    EXPECT_CALL(*m_mockViewPtr, plotCurve(testing::_)).Times(2);
    EXPECT_CALL(*m_mockViewPtr, userWarning(testing::_, testing::_)).Times(0);

    presenter->notify(IEnggDiffGSASFittingPresenter::SelectRun);
    assertMocksUsedCorrectly();
  }

  void test_doRietveldRefinement() {
    auto presenter = setUpPresenter();

    const RunLabel runLabel(123, 1);
    const auto refinementMethod = GSASRefinementMethod::RIETVELD;
    const auto instParams = "Instrument file";
    const std::vector<std::string> phaseFiles({"phase1", "phase2"});
    const auto pathToGSASII = "GSASHOME";
    const auto GSASIIProjectFile = "GPX.gpx";

    EXPECT_CALL(*m_mockViewPtr, getSelectedRunLabel())
        .Times(1)
        .WillOnce(Return(runLabel));
    EXPECT_CALL(*m_mockViewPtr, getRefinementMethod())
        .Times(1)
        .WillOnce(Return(refinementMethod));
    EXPECT_CALL(*m_mockViewPtr, getInstrumentFileName())
        .Times(1)
        .WillOnce(Return(instParams));
    EXPECT_CALL(*m_mockViewPtr, getPhaseFileNames())
        .Times(1)
        .WillOnce(Return(phaseFiles));
    EXPECT_CALL(*m_mockViewPtr, getPathToGSASII())
        .Times(1)
        .WillOnce(Return(pathToGSASII));
    EXPECT_CALL(*m_mockViewPtr, getGSASIIProjectPath())
        .Times(1)
        .WillOnce(Return(GSASIIProjectFile));

    EXPECT_CALL(*m_mockModelPtr,
                doRietveldRefinement(runLabel, instParams, phaseFiles,
                                     pathToGSASII, GSASIIProjectFile))
        .Times(1)
        .WillOnce(Return(false));
    EXPECT_CALL(*m_mockViewPtr,
                userWarning("Refinement failed",
                            "Refinement failed, see the log for more details"));

    presenter->notify(IEnggDiffGSASFittingPresenter::DoRefinement);
    assertMocksUsedCorrectly();
  }

  void test_doPawleyRefinement() {
    auto presenter = setUpPresenter();

    const RunLabel runLabel(123, 1);
    const auto refinementMethod = GSASRefinementMethod::PAWLEY;
    const auto instParams = "Instrument file";
    const std::vector<std::string> phaseFiles({"phase1", "phase2"});
    const auto pathToGSASII = "GSASHOME";
    const auto GSASIIProjectFile = "GPX.gpx";
    const auto dmin = 1.0;
    const auto negativeWeight = 2.0;

    EXPECT_CALL(*m_mockViewPtr, getSelectedRunLabel())
        .Times(1)
        .WillOnce(Return(runLabel));
    EXPECT_CALL(*m_mockViewPtr, getRefinementMethod())
        .Times(1)
        .WillOnce(Return(refinementMethod));
    EXPECT_CALL(*m_mockViewPtr, getInstrumentFileName())
        .Times(1)
        .WillOnce(Return(instParams));
    EXPECT_CALL(*m_mockViewPtr, getPhaseFileNames())
        .Times(1)
        .WillOnce(Return(phaseFiles));
    EXPECT_CALL(*m_mockViewPtr, getPathToGSASII())
        .Times(1)
        .WillOnce(Return(pathToGSASII));
    EXPECT_CALL(*m_mockViewPtr, getGSASIIProjectPath())
        .Times(1)
        .WillOnce(Return(GSASIIProjectFile));
    EXPECT_CALL(*m_mockViewPtr, getPawleyDMin())
        .Times(1)
        .WillOnce(Return(dmin));
    EXPECT_CALL(*m_mockViewPtr, getPawleyNegativeWeight())
        .Times(1)
        .WillOnce(Return(negativeWeight));

    EXPECT_CALL(*m_mockModelPtr,
                doPawleyRefinement(runLabel, instParams, phaseFiles,
                                   pathToGSASII, GSASIIProjectFile, dmin,
                                   negativeWeight))
        .Times(1)
        .WillOnce(Return(false));
    EXPECT_CALL(*m_mockViewPtr,
                userWarning("Refinement failed",
                            "Refinement failed, see the log for more details"));

    presenter->notify(IEnggDiffGSASFittingPresenter::DoRefinement);
    assertMocksUsedCorrectly();
  }

private:
  MockEnggDiffGSASFittingModel *m_mockModelPtr;
  MockEnggDiffGSASFittingView *m_mockViewPtr;

  std::unique_ptr<EnggDiffGSASFittingPresenter> setUpPresenter() {
    auto mockModel = Mantid::Kernel::make_unique<
        testing::NiceMock<MockEnggDiffGSASFittingModel>>();
    m_mockModelPtr = mockModel.get();

    m_mockViewPtr = new testing::NiceMock<MockEnggDiffGSASFittingView>();

    std::unique_ptr<EnggDiffGSASFittingPresenter> pres_uptr(
        new EnggDiffGSASFittingPresenter(std::move(mockModel), m_mockViewPtr));
    return pres_uptr;
  }

  void assertMocksUsedCorrectly() {
    TSM_ASSERT("View mock not used as expected: some EXPECT_CALL conditions "
               "not satisfied",
               testing::Mock::VerifyAndClearExpectations(m_mockModelPtr));
    TSM_ASSERT("Model mock not used as expected: some EXPECT_CALL conditions "
               "not satisfied",
               testing::Mock::VerifyAndClearExpectations(m_mockViewPtr));
    if (m_mockViewPtr) {
      delete m_mockViewPtr;
    }
  }
};

#endif // MANTID_CUSTOM_INTERFACES_ENGGDIFFGSASFITTINGPRESENTERTEST_H_
