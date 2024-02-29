// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2024 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include <cxxtest/TestSuite.h>

#include "MantidAlgorithms/CreateSampleWorkspace.h"
#include "MantidAlgorithms/PolarizationCorrections/DepolarizedAnalyserTransmission.h"

namespace {
constexpr double T_E_VALUE = 82593.9;
constexpr double PXD_VALUE = 14.9860;
constexpr double T_E_ERROR = 26088049.0;
constexpr double PXD_ERROR = 467.994241;
constexpr double T_E_DELTA = 1e-1;
constexpr double PXD_DELTA = 1e-5;
constexpr double COST_FUNC_MAX = 5e-15;
} // namespace

using Mantid::Algorithms::CreateSampleWorkspace;
using Mantid::Algorithms::DepolarizedAnalyserTransmission;
using Mantid::API::MatrixWorkspace_sptr;

class DepolarizedAnalyserTransmissionTest : public CxxTest::TestSuite {
public:
  void test_name() {
    DepolarizedAnalyserTransmission const alg;
    TS_ASSERT_EQUALS(alg.name(), "DepolarizedAnalyserTransmission");
  }

  void test_version() {
    DepolarizedAnalyserTransmission const alg;
    TS_ASSERT_EQUALS(alg.version(), 1);
  }

  void test_normal_exec() {
    MatrixWorkspace_sptr const &mtWs = createTestingWorkspace("__mt", "1.465e-07*exp(0.0733*4.76*x)");
    auto const &depWs = createTestingWorkspace("__dep", "0.0121*exp(-0.0733*10.226*x)");
    DepolarizedAnalyserTransmission alg;
    alg.setChild(true);
    alg.initialize();
    TS_ASSERT(alg.isInitialized());
    alg.setProperty("DepolarisedWorkspace", depWs);
    alg.setProperty("EmptyCellWorkspace", mtWs);
    alg.setPropertyValue("OutputWorkspace", "__unused_for_child");
    alg.execute();
    TS_ASSERT(alg.isExecuted());
    Mantid::API::ITableWorkspace_sptr const &outputWs = alg.getProperty("OutputWorkspace");
    TS_ASSERT_DELTA(outputWs->getColumn("Value")->toDouble(0), T_E_VALUE, T_E_DELTA);
    TS_ASSERT_DELTA(outputWs->getColumn("Value")->toDouble(1), PXD_VALUE, PXD_DELTA);
    TS_ASSERT_DELTA(outputWs->getColumn("Error")->toDouble(0), T_E_ERROR, T_E_DELTA);
    TS_ASSERT_DELTA(outputWs->getColumn("Error")->toDouble(1), PXD_ERROR, PXD_DELTA);
    TS_ASSERT_LESS_THAN(outputWs->getColumn("Value")->toDouble(2), COST_FUNC_MAX);
  }

  void test_failed_fit() {
    MatrixWorkspace_sptr const &mtWs = createTestingWorkspace("__mt", "1.465e-07*exp(0.0733*4.76*x)");
    auto const &depWs = createTestingWorkspace("__dep", "0.0121*exp(-0.0733*10.226*x)");
    DepolarizedAnalyserTransmission alg;
    alg.setChild(true);
    alg.initialize();
    TS_ASSERT(alg.isInitialized());
    alg.setProperty("DepolarisedWorkspace", depWs);
    alg.setProperty("EmptyCellWorkspace", mtWs);
    alg.setProperty("TEStartingValue", 1e50);
    alg.setProperty("PxDStartingValue", 1e50);
    alg.setPropertyValue("OutputWorkspace", "__unused_for_child");
    TS_ASSERT_THROWS_EQUALS(alg.execute(), std::runtime_error const &e, std::string(e.what()),
                            "Failed to fit to transmission workspace, : Changes in function value are too small");
    TS_ASSERT(!alg.isExecuted());
  }

  void test_apparently_successful_fit() {
    MatrixWorkspace_sptr const &mtWs = createTestingWorkspace("__mt", "0*x");
    auto const &depWs = createTestingWorkspace("__dep", "0.0121*exp(-0.0733*10.226*x)");
    DepolarizedAnalyserTransmission alg;
    alg.setChild(true);
    alg.initialize();
    TS_ASSERT(alg.isInitialized());
    alg.setProperty("DepolarisedWorkspace", depWs);
    alg.setProperty("EmptyCellWorkspace", mtWs);
    alg.setPropertyValue("OutputWorkspace", "__unused_for_child");
    TS_ASSERT_THROWS_EQUALS(alg.execute(), std::runtime_error const &e, std::string(e.what()),
                            "Failed to fit to transmission workspace, : Fit quality is too low (0.000000). You may "
                            "want to check that the correct monitor spectrum was provided.");
    alg.isExecuted();
    Mantid::API::ITableWorkspace_sptr const &outputWs = alg.getProperty("OutputWorkspace");
  }

  void test_invalid_workspace_lengths() {
    MatrixWorkspace_sptr const &mtWs = createTestingWorkspace("__mt", "1.465e-07*exp(0.0733*4.76*x)", 102);
    auto const &depWs = createTestingWorkspace("__dep", "0.0121*exp(-0.0733*10.226*x)", 2);
    DepolarizedAnalyserTransmission alg;
    alg.setChild(true);
    alg.initialize();
    TS_ASSERT(alg.isInitialized());
    alg.setProperty("DepolarisedWorkspace", depWs);
    alg.setProperty("EmptyCellWorkspace", mtWs);
    alg.setPropertyValue("OutputWorkspace", "__unused_for_child");
    TS_ASSERT_THROWS_EQUALS(alg.execute(), std::runtime_error const &e, std::string(e.what()),
                            "Some invalid Properties found: \n DepolarisedWorkspace: The depolarised workspace must "
                            "contain a single spectrum. Contains 4 spectra.\n EmptyCellWorkspace: The empty cell "
                            "workspace must contain a single spectrum. Contains 10404 spectra.");
    TS_ASSERT(!alg.isExecuted());
  }

private:
  MatrixWorkspace_sptr createTestingWorkspace(std::string const &outName, std::string const &formula,
                                              int const numSpectra = 1) {
    CreateSampleWorkspace makeWsAlg;
    makeWsAlg.initialize();
    makeWsAlg.setChild(true);
    makeWsAlg.setPropertyValue("OutputWorkspace", outName);
    makeWsAlg.setPropertyValue("Function", "User Defined");
    makeWsAlg.setPropertyValue("UserDefinedFunction", "name=UserFunction, Formula=" + formula);
    makeWsAlg.setPropertyValue("XUnit", "wavelength");
    makeWsAlg.setProperty("NumBanks", 1);
    makeWsAlg.setProperty("BankPixelWidth", numSpectra);
    makeWsAlg.setProperty("XMin", 3.5);
    makeWsAlg.setProperty("XMax", 16.5);
    makeWsAlg.setProperty("BinWidth", 0.1);
    makeWsAlg.execute();
    return makeWsAlg.getProperty("OutputWorkspace");
  }
};
