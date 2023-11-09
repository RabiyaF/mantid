# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2017 ISIS Rutherford Appleton Laboratory UKRI,
#   NScD Oak Ridge National Laboratory, European Spallation Source,
#   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
# SPDX - License - Identifier: GPL - 3.0 +
#    This file is part of the mantid workbench.
#
#
import os.path
import tempfile
import unittest

from qtpy.QtWidgets import QApplication
from unittest import mock
from unittest.mock import patch
from mantidqt.utils.qt.testing import start_qapplication
from mantidqt.utils.qt.testing.qt_widget_finder import QtWidgetFinder
from mantidqt.widgets.codeeditor.multifileinterpreter import MultiPythonFileInterpreter

MANTID_API_IMPORT = "from mantid.simpleapi import *\n"
PERMISSION_BOX_FUNC = "mantidqt.widgets.codeeditor.scriptcompatibility.permission_box_to_prepend_import"


@start_qapplication
class MultiPythonFileInterpreterTest(unittest.TestCase, QtWidgetFinder):
    def test_default_contains_single_editor(self):
        widget = MultiPythonFileInterpreter()
        self.assertEqual(1, widget.editor_count)

    def test_add_editor(self):
        widget = MultiPythonFileInterpreter()
        self.assertEqual(1, widget.editor_count)
        widget.append_new_editor()
        self.assertEqual(2, widget.editor_count)

    def test_open_file_in_new_tab_import_added(self):
        test_string = "Test file\nConvertUnits()"
        widget = MultiPythonFileInterpreter()
        mock_open_func = mock.mock_open(read_data=test_string)
        with mock.patch(widget.__module__ + ".open", mock_open_func, create=True):
            with mock.patch(PERMISSION_BOX_FUNC, lambda: True):
                widget.open_file_in_new_tab(test_string)
        self.assertEqual(widget.current_editor().editor.isModified(), True, msg="Script not marked as modified.")
        self.assertIn(MANTID_API_IMPORT, widget.current_editor().editor.text(), msg="'simpleapi' import not added to script.")

    def test_open_file_in_new_tab_no_import_added(self):
        test_string = "Test file\n"
        widget = MultiPythonFileInterpreter()
        mock_open_func = mock.mock_open(read_data=test_string)
        with mock.patch(widget.__module__ + ".open", mock_open_func, create=True):
            with mock.patch(PERMISSION_BOX_FUNC, lambda: True):
                widget.open_file_in_new_tab(test_string)
        self.assertNotIn(MANTID_API_IMPORT, widget.current_editor().editor.text())

    def test_open_same_file_twice_no_extra_tab(self):
        widget = MultiPythonFileInterpreter()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "test_open_same_file_twice_no_extra_tab")
            with open(filename, "w") as f:
                f.write("Test")
            with mock.patch("mantidqt.widgets.codeeditor.interpreter.EditorIO.ask_for_filename", lambda s: filename):
                widget.open_file_in_new_tab(filename)
                widget.open_file_in_new_tab(filename)
        self.assertEqual(2, widget.editor_count, msg="Should be the original tab, plus one (not two) tabs for the file")

    def test_open_same_file_twice_no_tab_even_if_modified(self):
        widget = MultiPythonFileInterpreter()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "test_open_same_file_twice_no_tab_even_if_modified")
            with open(filename, "w") as f:
                f.write("Test")
            with mock.patch("mantidqt.widgets.codeeditor.interpreter.EditorIO.ask_for_filename", lambda s: filename):
                widget.open_file_in_new_tab(filename)
                widget.current_editor().editor.append("Some text")
                widget.open_file_in_new_tab(filename)
        self.assertEqual(2, widget.editor_count, msg="Should be the original tab, plus one (not two) tabs for the file")
        # File should still be modified after attempted reopening because it was modified before reopening and we don't want to lose changes
        self.assertTrue(widget.current_editor().editor.isModified(), msg="File should still be modified after attempted reopening")

    def test_save_as_closes_the_original_tab(self):
        test_string = "Test file\n"
        widget = MultiPythonFileInterpreter()
        mock_open_func = mock.mock_open(read_data=test_string)
        ask_for_filename = "mantidqt.widgets.codeeditor.interpreter.EditorIO.ask_for_filename"
        test_file_name = "test_save_as_leaves_original_marked_unmodified"
        # fmt: off
        with mock.patch(widget.__module__ + ".open", mock_open_func, create=True), \
                mock.patch(PERMISSION_BOX_FUNC, lambda: True), \
                tempfile.TemporaryDirectory() as temp_dir, \
                mock.patch(ask_for_filename, lambda s: os.path.join(temp_dir, test_file_name)):
            widget.open_file_in_new_tab(test_string)
            widget.save_current_file_as()
        # fmt: on
        # There's one tab when you create the editor, then another one was added when opening the mock file. Clicking
        # 'Save Script as' should close the original tab with the old name, and leave you with a tab with the new name.
        self.assertEqual(2, widget.editor_count)
        self.assertFalse(widget.current_editor().editor.isModified(), msg="Tab should be marked as not modified")

    @patch("mantidqt.widgets.codeeditor.multifileinterpreter.MultiPythonFileInterpreter.file_changed_event", autospec=True)
    def test_file_modified_externally_generates_event(self, file_changed_event_mock):
        widget = MultiPythonFileInterpreter()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "test_file_modified_externally")
            with open(filename, "w") as f:
                f.write("Test")
            with mock.patch("mantidqt.widgets.codeeditor.interpreter.EditorIO.ask_for_filename", lambda s: filename):
                widget.open_file_in_new_tab(filename)
            with open(filename, "w") as f:
                f.write("File changed")
            QApplication.instance().processEvents()
        file_changed_event_mock.assert_called_once()

    @patch("mantidqt.widgets.codeeditor.multifileinterpreter.MultiPythonFileInterpreter.file_changed_event", autospec=True)
    def test_saving_file_adds_events_to_ignore_list(self, file_changed_event_mock):
        widget = MultiPythonFileInterpreter()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = os.path.join(temp_dir, "test_saving_file_adds_events_to_ignore_list")
            with open(filename, "w") as f:
                f.write("Test")
            with mock.patch("mantidqt.widgets.codeeditor.interpreter.EditorIO.ask_for_filename", lambda s: filename):
                widget.open_file_in_new_tab(filename)
            editor = widget.current_editor()
            editor.editor.setText("New text")
            widget.save_current_file()
            QApplication.instance().processEvents()
            self.assertEqual(1, widget.file_watcher_events_to_ignore, "Saving the file should generate some events to ignore")


if __name__ == "__main__":
    unittest.main()
