// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2023 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include "Common/InterfaceUtils.h"
#include "Common/WorkspaceUtils.h"
#include "MantidAPI/AlgorithmManager.h"
#include "MantidAPI/MatrixWorkspace.h"
#include "MantidFrameworkTestHelpers/IndirectFitDataCreationHelper.h"

#include <QPair>
#include <cxxtest/TestSuite.h>

using namespace Mantid::API;
using namespace MantidQt::CustomInterfaces::InterfaceUtils;
using namespace Mantid::IndirectFitDataCreationHelper;

class InterfaceUtilsTest : public CxxTest::TestSuite {
public:
  InterfaceUtilsTest() = default;

  void test_interface_property_empty_if_no_interface_found() {
    TS_ASSERT_EQUALS(getInterfaceProperty("Empty", "EXTENSIONS", "all"), "");
  }

  void test_get_FB_WS_suffixes_function_returns_proper_interface_suffixes() {
    // There are many similar functions in the interface, this test will try only one pair of such functions
    TS_ASSERT_EQUALS(getResolutionWSSuffixes("Iqt"), QStringList({"_res", "_red", "_sqw"}));
    TS_ASSERT_EQUALS(getResolutionFBSuffixes("Iqt"), QStringList({"_res.nxs", "_red.nxs", "_sqw.nxs"}));
  }
};