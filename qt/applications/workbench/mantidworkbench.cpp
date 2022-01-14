// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/path.hpp>
#include <boost/process/detail/traits/wchar_t.hpp>
#include <boost/process/env.hpp>
#include <boost/process/search_path.hpp>
#include <boost/process/system.hpp>

#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

#if !defined(PYTHON_EXECUTABLE_PATH)
#error "PYTHON_EXECUTABLE_PATH preprocessor definition not found."
#endif

// main module for workbench.
static constexpr auto WORKBENCH_MAIN = "workbench.app.main";

// main moduld for errorreports.
static constexpr auto ERRORREPORTS_MAIN = "mantidqt.dialogs.errorreports.main";

// Application name for error reporters.
// Matches current string send to error reporter
static constexpr auto ERRORREPORTS_APP_NAME = "workbench";

// aliases
namespace bp = boost::process;
namespace fs = boost::filesystem;
using ExeArgs = std::vector<std::string>;

// helper functions
namespace {

/**
 * Return the path to the Python executable
 * @param base Directory to serve as base for absolute paths
 */
#if defined(CONDA_ENV)
inline std::string pythonExecutable(const fs::path &) {
  // We assume the conda environement is activated and python will be found
  // on the PATH
  return bp::search_path(PYTHON_EXECUTABLE_PATH).generic_string();
}
#else
/**
 * Check the given path and make it absolute if it is relative. The base
 * is taken as the directory given
 * @param path A filesystem path as a string
 * @param base Directory to serve as base for absolute paths
 */
inline std::string absolutePath(const char *path, const fs::path &base) {
  fs::path abspath(path);
  if (!abspath.is_absolute()) {
    abspath = base / path;
  }
  return abspath.generic_string();
}

inline std::string pythonExecutable(const fs::path &dirOfExe) { return absolutePath(PYTHON_EXECUTABLE_PATH, dirOfExe); }
#endif

/**
 * Given a list of existing executable/arguments append those
 * from the command line given by the standard argv/argv
 * combination
 * @param exeArgs Existing list of executable path + arguments
 * @param argc The number of arguments in the argv array
 * @param argv The argument array of length argc
 */
void appendArguments(ExeArgs *exeArgs, int argc, char **argv) {
  assert(exeArgs);
  if (argc == 1) // just program name
    return;

  const auto startupArgsSize{exeArgs->size()};
#if defined(__APPLE__) && !defined(CONDA_ENV)
  // On first launch of quarantined apps launchd passes a command line parameter
  // of the form -psn_0_XXXXXX to the application. We discard this otherwise
  // workbench's argparse will choke on it.
  // https://stackoverflow.com/questions/10242115/os-x-strange-psn-command-line-parameter-when-launched-from-finder
  const auto acceptedArg = [](const char *arg) -> bool {
    if (std::string(arg).compare(0, 5, "-psn_") == 0)
      return false;
    return true;
  };
  const auto nargs = std::count_if(argv + 1, argv + argc, acceptedArg);
  exeArgs->resize(startupArgsSize + nargs);
  std::copy_if(argv + 1, argv + argc, std::next(exeArgs->begin(), startupArgsSize), acceptedArg);
#else
  exeArgs->resize(startupArgsSize + argc - 1);
  std::copy(argv + 1, argv + argc, std::next(exeArgs->begin(), startupArgsSize));
#endif
}

/**
 * Construct the map of environment variables for the child process.
 * @param dirOfExe Directory of the running executable
 * @return A boost::process::environment type to pass to
 * boost::process::system
 */
decltype(boost::this_process::environment()) childEnvironment([[maybe_unused]] const fs::path &dirOfExe) {
  auto env = boost::this_process::environment();

#if !defined(CONDA_ENV)
  auto insertAtFront = [&env](const auto &name, const auto &value) {
    const auto existingValue = env[name];
    env[name] = value;
    env[name] += existingValue.to_string();
  };
  const auto dirOfExeStr = dirOfExe.string();
  insertAtFront("PATH", dirOfExeStr);
  insertAtFront("PYTHONPATH", dirOfExeStr);

#if defined(QT_PLUGIN_PATH)
  env["QT_PLUGIN_PATH"] = absolutePath(QT_PLUGIN_PATH, dirOfExe);
#endif

#endif

  // It was observed on Qt >= 5.12 that the QtWebEngineProcess would fail to
  // load the icudtl.dat resources due to Chromium sandboxing restrictions. It
  // would appear there is no more fine-grained way to control the restrictions:
  // https://doc.qt.io/qt-5/qtwebengine-platform-notes.html
  env["QTWEBENGINE_DISABLE_SANDBOX"] = "1";
  return env;
}

/**
 * Start the workbench process, wait until it completes and return the
 * exit code.
 * @param dirOfExe Directory of the running executable
 * @param argc The number of arguments passed on the command line
 * @param argv The array of command line arguments
 */
int startWorkbench(const fs::path &dirOfExe, int argc, char **argv) {
  ExeArgs startupWorkbench{"-m", WORKBENCH_MAIN};
  appendArguments(&startupWorkbench, argc, argv);
  try {
    return bp::system(pythonExecutable(dirOfExe), startupWorkbench, childEnvironment(dirOfExe));
  } catch (const bp::process_error &exc) {
    std::cerr << "Running " << pythonExecutable(dirOfExe) << " ";
    for (const auto &arg : startupWorkbench) {
      std::cerr << arg << " ";
    }
    std::cerr << "\nCaught system_error with code " << exc.code() << " meaning " << exc.what() << "\n";
    return 1;
  }
}

/**
 * Show the error reporter, assuming a bad exit status of workbench
 * @param dirOfExe Directory of the running executable
 * @param workbenchExitCode An integer specifying the exit code of the
 * workbench process
 */
void showErrorReporter(const fs::path &dirOfExe, const int workbenchExitCode) {
  // clang-format off
  const ExeArgs startErrorReporter{
      "-m",
      ERRORREPORTS_MAIN,
      "--application", ERRORREPORTS_APP_NAME,
      "--exitcode", std::to_string(workbenchExitCode)};
  // clang-format on
  try {
    bp::system(pythonExecutable(dirOfExe), startErrorReporter);
  } catch (const bp::process_error &exc) {
    std::cerr << "Running " << pythonExecutable(dirOfExe) << " ";
    for (const auto &arg : startErrorReporter) {
      std::cerr << arg << " ";
    }
    std::cerr << "\nCaught system_error with code " << exc.code() << " meaning " << exc.what() << "\n";
  }
}

} // namespace

/**
 * A light wrapper to:
 *
 *   - start workbench as a child process
 *   - if workbench exits with a non-zero exit code then
 *   - start the error reporter application.
 *
 * This could be done with shell scripts but then the logic of starting
 * the error reporter is duplicated across shell, ps1 scripts on the
 * various platforms.
 *
 * This is designed to be a mimimum standalone executable that does nothing
 * but start other applications. Any argument parsing logic should be done
 * in the startup routines for workbench or errorreporter. There is a single
 * exception on macOS that is documented in appendArguments().
 *
 * This is not yet used on Linux as extra logic exists there that macOS/Windows
 * do not have. See buildconfig/CMake/LinuxPackageScripts.cmake
 *
 * @param argc The number of arguments passed on the command line
 * @param argv The array of command line arguments
 */
int main(int argc, char **argv) {
  const auto dirOfExe = [&argv]() { return fs::absolute(fs::path(argv[0]).remove_filename()); }();
  const auto workbenchExitCode = startWorkbench(dirOfExe, argc, argv);
  if (workbenchExitCode != 0) {
    showErrorReporter(dirOfExe, workbenchExitCode);
  }
  return workbenchExitCode;
}
