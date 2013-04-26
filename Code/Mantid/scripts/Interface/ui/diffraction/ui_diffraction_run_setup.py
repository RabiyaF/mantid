# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'diffraction_run_setup.ui'
#
# Created: Wed Apr 17 13:41:11 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName(_fromUtf8("Frame"))
        Frame.resize(1026, 1273)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Frame.sizePolicy().hasHeightForWidth())
        Frame.setSizePolicy(sizePolicy)
        Frame.setFrameShape(QtGui.QFrame.NoFrame)
        Frame.setFrameShadow(QtGui.QFrame.Plain)
        Frame.setLineWidth(8)
        self.verticalLayout = QtGui.QVBoxLayout(Frame)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(Frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 0))
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1026, 1273))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.instr_name_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.instr_name_label.sizePolicy().hasHeightForWidth())
        self.instr_name_label.setSizePolicy(sizePolicy)
        self.instr_name_label.setMinimumSize(QtCore.QSize(160, 30))
        self.instr_name_label.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.instr_name_label.setFont(font)
        self.instr_name_label.setObjectName(_fromUtf8("instr_name_label"))
        self.horizontalLayout_13.addWidget(self.instr_name_label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem)
        self.help_button = QtGui.QCommandLinkButton(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.help_button.sizePolicy().hasHeightForWidth())
        self.help_button.setSizePolicy(sizePolicy)
        self.help_button.setMinimumSize(QtCore.QSize(73, 30))
        self.help_button.setMaximumSize(QtCore.QSize(73, 33))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.help_button.setFont(font)
        self.help_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.help_button.setIconSize(QtCore.QSize(15, 15))
        self.help_button.setObjectName(_fromUtf8("help_button"))
        self.horizontalLayout_13.addWidget(self.help_button)
        self.verticalLayout_4.addLayout(self.horizontalLayout_13)
        self.reduction_options_group = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reduction_options_group.sizePolicy().hasHeightForWidth())
        self.reduction_options_group.setSizePolicy(sizePolicy)
        self.reduction_options_group.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.reduction_options_group.setObjectName(_fromUtf8("reduction_options_group"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.reduction_options_group)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.run_number_label = QtGui.QLabel(self.reduction_options_group)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_number_label.sizePolicy().hasHeightForWidth())
        self.run_number_label.setSizePolicy(sizePolicy)
        self.run_number_label.setMinimumSize(QtCore.QSize(160, 0))
        self.run_number_label.setMaximumSize(QtCore.QSize(160, 16777215))
        self.run_number_label.setObjectName(_fromUtf8("run_number_label"))
        self.horizontalLayout_4.addWidget(self.run_number_label)
        self.runnumbers_edit = QtGui.QLineEdit(self.reduction_options_group)
        self.runnumbers_edit.setMinimumSize(QtCore.QSize(160, 0))
        self.runnumbers_edit.setMaximumSize(QtCore.QSize(160, 16777215))
        self.runnumbers_edit.setObjectName(_fromUtf8("runnumbers_edit"))
        self.horizontalLayout_4.addWidget(self.runnumbers_edit)
        spacerItem1 = QtGui.QSpacerItem(160, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.sum_checkbox = QtGui.QCheckBox(self.reduction_options_group)
        self.sum_checkbox.setMinimumSize(QtCore.QSize(80, 0))
        self.sum_checkbox.setMaximumSize(QtCore.QSize(80, 16777215))
        self.sum_checkbox.setObjectName(_fromUtf8("sum_checkbox"))
        self.horizontalLayout_4.addWidget(self.sum_checkbox)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.verticalLayout_6.addLayout(self.horizontalLayout_4)
        self.monitor_layout = QtGui.QHBoxLayout()
        self.monitor_layout.setObjectName(_fromUtf8("monitor_layout"))
        self.calfile_label = QtGui.QLabel(self.reduction_options_group)
        self.calfile_label.setMinimumSize(QtCore.QSize(160, 0))
        self.calfile_label.setMaximumSize(QtCore.QSize(160, 16777215))
        self.calfile_label.setObjectName(_fromUtf8("calfile_label"))
        self.monitor_layout.addWidget(self.calfile_label)
        self.calfile_edit = QtGui.QLineEdit(self.reduction_options_group)
        self.calfile_edit.setObjectName(_fromUtf8("calfile_edit"))
        self.monitor_layout.addWidget(self.calfile_edit)
        self.calfile_browse = QtGui.QPushButton(self.reduction_options_group)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calfile_browse.sizePolicy().hasHeightForWidth())
        self.calfile_browse.setSizePolicy(sizePolicy)
        self.calfile_browse.setObjectName(_fromUtf8("calfile_browse"))
        self.monitor_layout.addWidget(self.calfile_browse)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.monitor_layout.addItem(spacerItem3)
        self.verticalLayout_6.addLayout(self.monitor_layout)
        self.abs_scale_direct_beam_layout = QtGui.QHBoxLayout()
        self.abs_scale_direct_beam_layout.setObjectName(_fromUtf8("abs_scale_direct_beam_layout"))
        self.characterfile_label = QtGui.QLabel(self.reduction_options_group)
        self.characterfile_label.setMinimumSize(QtCore.QSize(160, 0))
        self.characterfile_label.setMaximumSize(QtCore.QSize(160, 16777215))
        self.characterfile_label.setObjectName(_fromUtf8("characterfile_label"))
        self.abs_scale_direct_beam_layout.addWidget(self.characterfile_label)
        self.charfile_edit = QtGui.QLineEdit(self.reduction_options_group)
        self.charfile_edit.setMinimumSize(QtCore.QSize(300, 0))
        self.charfile_edit.setObjectName(_fromUtf8("charfile_edit"))
        self.abs_scale_direct_beam_layout.addWidget(self.charfile_edit)
        self.charfile_browse = QtGui.QPushButton(self.reduction_options_group)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.charfile_browse.sizePolicy().hasHeightForWidth())
        self.charfile_browse.setSizePolicy(sizePolicy)
        self.charfile_browse.setObjectName(_fromUtf8("charfile_browse"))
        self.abs_scale_direct_beam_layout.addWidget(self.charfile_browse)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.abs_scale_direct_beam_layout.addItem(spacerItem4)
        self.verticalLayout_6.addLayout(self.abs_scale_direct_beam_layout)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.outputdir_label = QtGui.QLabel(self.reduction_options_group)
        self.outputdir_label.setMinimumSize(QtCore.QSize(160, 0))
        self.outputdir_label.setMaximumSize(QtCore.QSize(160, 16777215))
        self.outputdir_label.setObjectName(_fromUtf8("outputdir_label"))
        self.horizontalLayout_7.addWidget(self.outputdir_label)
        self.outputdir_edit = QtGui.QLineEdit(self.reduction_options_group)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.outputdir_edit.sizePolicy().hasHeightForWidth())
        self.outputdir_edit.setSizePolicy(sizePolicy)
        self.outputdir_edit.setMinimumSize(QtCore.QSize(300, 0))
        self.outputdir_edit.setBaseSize(QtCore.QSize(0, 0))
        self.outputdir_edit.setObjectName(_fromUtf8("outputdir_edit"))
        self.horizontalLayout_7.addWidget(self.outputdir_edit)
        self.outputdir_browse = QtGui.QPushButton(self.reduction_options_group)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.outputdir_browse.sizePolicy().hasHeightForWidth())
        self.outputdir_browse.setSizePolicy(sizePolicy)
        self.outputdir_browse.setObjectName(_fromUtf8("outputdir_browse"))
        self.horizontalLayout_7.addWidget(self.outputdir_browse)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem5)
        self.verticalLayout_6.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_2 = QtGui.QLabel(self.reduction_options_group)
        self.label_2.setMinimumSize(QtCore.QSize(160, 0))
        self.label_2.setMaximumSize(QtCore.QSize(160, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_8.addWidget(self.label_2)
        self.saveas_combo = QtGui.QComboBox(self.reduction_options_group)
        self.saveas_combo.setMinimumSize(QtCore.QSize(240, 0))
        self.saveas_combo.setMaximumSize(QtCore.QSize(240, 16777215))
        self.saveas_combo.setObjectName(_fromUtf8("saveas_combo"))
        self.saveas_combo.addItem(_fromUtf8(""))
        self.saveas_combo.addItem(_fromUtf8(""))
        self.saveas_combo.addItem(_fromUtf8(""))
        self.saveas_combo.addItem(_fromUtf8(""))
        self.horizontalLayout_8.addWidget(self.saveas_combo)
        spacerItem6 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem6)
        self.label_6 = QtGui.QLabel(self.reduction_options_group)
        self.label_6.setMinimumSize(QtCore.QSize(80, 0))
        self.label_6.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_8.addWidget(self.label_6)
        self.unit_combo = QtGui.QComboBox(self.reduction_options_group)
        self.unit_combo.setMinimumSize(QtCore.QSize(100, 0))
        self.unit_combo.setObjectName(_fromUtf8("unit_combo"))
        self.unit_combo.addItem(_fromUtf8(""))
        self.unit_combo.addItem(_fromUtf8(""))
        self.horizontalLayout_8.addWidget(self.unit_combo)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem7)
        self.verticalLayout_6.addLayout(self.horizontalLayout_8)
        self.verticalLayout_4.addWidget(self.reduction_options_group)
        self.geometry_options_groupbox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.geometry_options_groupbox.sizePolicy().hasHeightForWidth())
        self.geometry_options_groupbox.setSizePolicy(sizePolicy)
        self.geometry_options_groupbox.setMinimumSize(QtCore.QSize(0, 0))
        self.geometry_options_groupbox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.geometry_options_groupbox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.geometry_options_groupbox.setObjectName(_fromUtf8("geometry_options_groupbox"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.geometry_options_groupbox)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.mask_template_horiz_layout = QtGui.QHBoxLayout()
        self.mask_template_horiz_layout.setSpacing(0)
        self.mask_template_horiz_layout.setObjectName(_fromUtf8("mask_template_horiz_layout"))
        self.experiment_parameter_help = QtGui.QLabel(self.geometry_options_groupbox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.experiment_parameter_help.sizePolicy().hasHeightForWidth())
        self.experiment_parameter_help.setSizePolicy(sizePolicy)
        self.experiment_parameter_help.setMinimumSize(QtCore.QSize(150, 0))
        self.experiment_parameter_help.setStyleSheet(_fromUtf8("font: italic 10pt \"Bitstream Charter\";"))
        self.experiment_parameter_help.setObjectName(_fromUtf8("experiment_parameter_help"))
        self.mask_template_horiz_layout.addWidget(self.experiment_parameter_help)
        self.verticalLayout_5.addLayout(self.mask_template_horiz_layout)
        self.correction_gridlayout = QtGui.QGridLayout()
        self.correction_gridlayout.setObjectName(_fromUtf8("correction_gridlayout"))
        self.disablebkgdcorr_chkbox = QtGui.QCheckBox(self.geometry_options_groupbox)
        self.disablebkgdcorr_chkbox.setWhatsThis(_fromUtf8(""))
        self.disablebkgdcorr_chkbox.setObjectName(_fromUtf8("disablebkgdcorr_chkbox"))
        self.correction_gridlayout.addWidget(self.disablebkgdcorr_chkbox, 0, 3, 1, 1)
        self.disablevancorr_chkbox = QtGui.QCheckBox(self.geometry_options_groupbox)
        self.disablevancorr_chkbox.setObjectName(_fromUtf8("disablevancorr_chkbox"))
        self.correction_gridlayout.addWidget(self.disablevancorr_chkbox, 1, 3, 1, 1)
        self.disablevanbkgdcorr_chkbox = QtGui.QCheckBox(self.geometry_options_groupbox)
        self.disablevanbkgdcorr_chkbox.setObjectName(_fromUtf8("disablevanbkgdcorr_chkbox"))
        self.correction_gridlayout.addWidget(self.disablevanbkgdcorr_chkbox, 2, 3, 1, 1)
        self.vanrun_edit = QtGui.QLineEdit(self.geometry_options_groupbox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vanrun_edit.sizePolicy().hasHeightForWidth())
        self.vanrun_edit.setSizePolicy(sizePolicy)
        self.vanrun_edit.setMinimumSize(QtCore.QSize(80, 0))
        self.vanrun_edit.setMaximumSize(QtCore.QSize(200, 16777215))
        self.vanrun_edit.setObjectName(_fromUtf8("vanrun_edit"))
        self.correction_gridlayout.addWidget(self.vanrun_edit, 1, 1, 1, 1)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.correction_gridlayout.addItem(spacerItem8, 0, 4, 1, 1)
        self.emptyrun_edit = QtGui.QLineEdit(self.geometry_options_groupbox)
        self.emptyrun_edit.setMinimumSize(QtCore.QSize(80, 0))
        self.emptyrun_edit.setMaximumSize(QtCore.QSize(200, 16777215))
        self.emptyrun_edit.setObjectName(_fromUtf8("emptyrun_edit"))
        self.correction_gridlayout.addWidget(self.emptyrun_edit, 0, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.geometry_options_groupbox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.correction_gridlayout.addWidget(self.label_5, 0, 0, 1, 1)
        self.label_11 = QtGui.QLabel(self.geometry_options_groupbox)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.correction_gridlayout.addWidget(self.label_11, 2, 0, 1, 1)
        self.label_10 = QtGui.QLabel(self.geometry_options_groupbox)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.correction_gridlayout.addWidget(self.label_10, 1, 0, 1, 1)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.correction_gridlayout.addItem(spacerItem9, 0, 2, 1, 1)
        self.vanbkgdrun_edit = QtGui.QLineEdit(self.geometry_options_groupbox)
        self.vanbkgdrun_edit.setMaximumSize(QtCore.QSize(200, 16777215))
        self.vanbkgdrun_edit.setObjectName(_fromUtf8("vanbkgdrun_edit"))
        self.correction_gridlayout.addWidget(self.vanbkgdrun_edit, 2, 1, 1, 1)
        self.verticalLayout_5.addLayout(self.correction_gridlayout)
        self.verticalLayout_4.addWidget(self.geometry_options_groupbox)
        self.mask_groupbox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mask_groupbox.sizePolicy().hasHeightForWidth())
        self.mask_groupbox.setSizePolicy(sizePolicy)
        self.mask_groupbox.setObjectName(_fromUtf8("mask_groupbox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.mask_groupbox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.mask_help_label = QtGui.QLabel(self.mask_groupbox)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Bitstream Charter"))
        font.setItalic(True)
        self.mask_help_label.setFont(font)
        self.mask_help_label.setObjectName(_fromUtf8("mask_help_label"))
        self.verticalLayout_2.addWidget(self.mask_help_label)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_9 = QtGui.QLabel(self.mask_groupbox)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 2, 5, 1, 1)
        self.resamplex_edit = QtGui.QLineEdit(self.mask_groupbox)
        self.resamplex_edit.setObjectName(_fromUtf8("resamplex_edit"))
        self.gridLayout.addWidget(self.resamplex_edit, 2, 1, 1, 1)
        self.bintype_combo = QtGui.QComboBox(self.mask_groupbox)
        self.bintype_combo.setMinimumSize(QtCore.QSize(160, 0))
        self.bintype_combo.setMaximumSize(QtCore.QSize(200, 16777215))
        self.bintype_combo.setObjectName(_fromUtf8("bintype_combo"))
        self.bintype_combo.addItem(_fromUtf8(""))
        self.bintype_combo.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.bintype_combo, 2, 3, 1, 1)
        self.label_8 = QtGui.QLabel(self.mask_groupbox)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 0, 5, 1, 1)
        self.usebin_button = QtGui.QRadioButton(self.mask_groupbox)
        self.usebin_button.setObjectName(_fromUtf8("usebin_button"))
        self.gridLayout.addWidget(self.usebin_button, 0, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.mask_groupbox)
        self.label_7.setText(_fromUtf8(""))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 0, 2, 1, 1)
        self.binind_checkbox = QtGui.QCheckBox(self.mask_groupbox)
        self.binind_checkbox.setObjectName(_fromUtf8("binind_checkbox"))
        self.gridLayout.addWidget(self.binind_checkbox, 0, 3, 1, 1)
        self.resamplex_button = QtGui.QRadioButton(self.mask_groupbox)
        self.resamplex_button.setObjectName(_fromUtf8("resamplex_button"))
        self.gridLayout.addWidget(self.resamplex_button, 2, 0, 1, 1)
        self.tofmax_edit = QtGui.QLineEdit(self.mask_groupbox)
        self.tofmax_edit.setObjectName(_fromUtf8("tofmax_edit"))
        self.gridLayout.addWidget(self.tofmax_edit, 2, 6, 1, 1)
        self.binning_edit = QtGui.QLineEdit(self.mask_groupbox)
        self.binning_edit.setObjectName(_fromUtf8("binning_edit"))
        self.gridLayout.addWidget(self.binning_edit, 0, 1, 1, 1)
        self.tofmin_edit = QtGui.QLineEdit(self.mask_groupbox)
        self.tofmin_edit.setObjectName(_fromUtf8("tofmin_edit"))
        self.gridLayout.addWidget(self.tofmin_edit, 0, 6, 1, 1)
        spacerItem10 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem10, 2, 2, 1, 1)
        spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem11, 2, 4, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        spacerItem12 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem12)
        self.verticalLayout_4.addWidget(self.mask_groupbox)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QtGui.QApplication.translate("Frame", "Frame", None, QtGui.QApplication.UnicodeUTF8))
        Frame.setToolTip(QtGui.QApplication.translate("Frame", "Click to browse.", None, QtGui.QApplication.UnicodeUTF8))
        self.instr_name_label.setText(QtGui.QApplication.translate("Frame", "SNS Powder Reduction", None, QtGui.QApplication.UnicodeUTF8))
        self.help_button.setText(QtGui.QApplication.translate("Frame", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.reduction_options_group.setTitle(QtGui.QApplication.translate("Frame", "Reduction Options", None, QtGui.QApplication.UnicodeUTF8))
        self.run_number_label.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Run number of the data to reduce</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.run_number_label.setText(QtGui.QApplication.translate("Frame", "Run Numbers", None, QtGui.QApplication.UnicodeUTF8))
        self.runnumbers_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter one or several run numbers.  </p><p>Example 1: 1234</p><p>Example 2: 1234, 2345</p><p>Example 3: 1234-2345</p><p>Example 4: 1234, 2345-3456, 4567</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.runnumbers_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Enter a scaling factor to be multiplied to I(Q).", None, QtGui.QApplication.UnicodeUTF8))
        self.sum_checkbox.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Select to sum several runs to same file</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.sum_checkbox.setStatusTip(QtGui.QApplication.translate("Frame", "Select to normalize to the beam monitor data", None, QtGui.QApplication.UnicodeUTF8))
        self.sum_checkbox.setText(QtGui.QApplication.translate("Frame", "Sum", None, QtGui.QApplication.UnicodeUTF8))
        self.calfile_label.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Instrument calibration file to time focus diffraction data</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.calfile_label.setText(QtGui.QApplication.translate("Frame", "Calibration File", None, QtGui.QApplication.UnicodeUTF8))
        self.calfile_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter a valid path for the instrument calibration file.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.calfile_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Enter a valid path for the beam monitor reference file.", None, QtGui.QApplication.UnicodeUTF8))
        self.calfile_browse.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Click to browse the instrument calibration file.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.calfile_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.characterfile_label.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Characterization file containing specific run information.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.characterfile_label.setText(QtGui.QApplication.translate("Frame", "Characterizaton File", None, QtGui.QApplication.UnicodeUTF8))
        self.charfile_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter a valid file name for characterization file.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.charfile_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Enter a valid file path for a direct beam data file.", None, QtGui.QApplication.UnicodeUTF8))
        self.charfile_browse.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Click to browse the characterization file.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.charfile_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.outputdir_label.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>File directory to save output reduced file.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.outputdir_label.setText(QtGui.QApplication.translate("Frame", "Output Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.outputdir_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter a valid file directory to save output reduced file.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.outputdir_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Enter a valid file path to be used for the dark current data.", None, QtGui.QApplication.UnicodeUTF8))
        self.outputdir_browse.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Click to browse the output directory.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.outputdir_browse.setText(QtGui.QApplication.translate("Frame", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>File format(s) to save. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Frame", "Save As", None, QtGui.QApplication.UnicodeUTF8))
        self.saveas_combo.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Choose the file formats to save the reduced data as. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.saveas_combo.setItemText(0, QtGui.QApplication.translate("Frame", "gsas", None, QtGui.QApplication.UnicodeUTF8))
        self.saveas_combo.setItemText(1, QtGui.QApplication.translate("Frame", "fullprof", None, QtGui.QApplication.UnicodeUTF8))
        self.saveas_combo.setItemText(2, QtGui.QApplication.translate("Frame", "gsas and fullprof", None, QtGui.QApplication.UnicodeUTF8))
        self.saveas_combo.setItemText(3, QtGui.QApplication.translate("Frame", "gsas and fullprof and pdfgetn", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Final unit of the output workspace. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Frame", "Final Unit", None, QtGui.QApplication.UnicodeUTF8))
        self.unit_combo.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Choose the final unit of output workspace.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.unit_combo.setItemText(0, QtGui.QApplication.translate("Frame", "dSpacing", None, QtGui.QApplication.UnicodeUTF8))
        self.unit_combo.setItemText(1, QtGui.QApplication.translate("Frame", "MomentumTransfer", None, QtGui.QApplication.UnicodeUTF8))
        self.geometry_options_groupbox.setTitle(QtGui.QApplication.translate("Frame", "Overriding Characterization File", None, QtGui.QApplication.UnicodeUTF8))
        self.experiment_parameter_help.setText(QtGui.QApplication.translate("Frame", "If characterization file is given, the correction run numbers are given by the file. \n"
"The corrections can be overriden and disabled though.", None, QtGui.QApplication.UnicodeUTF8))
        self.disablebkgdcorr_chkbox.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Disable emptry/background correction.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.disablebkgdcorr_chkbox.setStatusTip(QtGui.QApplication.translate("Frame", "Select to set the detector distance offset.", None, QtGui.QApplication.UnicodeUTF8))
        self.disablebkgdcorr_chkbox.setText(QtGui.QApplication.translate("Frame", "Disable", None, QtGui.QApplication.UnicodeUTF8))
        self.disablevancorr_chkbox.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Disable vanadium correction.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.disablevancorr_chkbox.setStatusTip(QtGui.QApplication.translate("Frame", "Select to force the sample-detector distance.", None, QtGui.QApplication.UnicodeUTF8))
        self.disablevancorr_chkbox.setText(QtGui.QApplication.translate("Frame", "Disable", None, QtGui.QApplication.UnicodeUTF8))
        self.disablevanbkgdcorr_chkbox.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Disable vanadium background correction.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.disablevanbkgdcorr_chkbox.setText(QtGui.QApplication.translate("Frame", "Disable ", None, QtGui.QApplication.UnicodeUTF8))
        self.vanrun_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter vanadium run number.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.vanrun_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Enter the value of the sample-to-detector distance in mm.", None, QtGui.QApplication.UnicodeUTF8))
        self.emptyrun_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter empty (background) run number.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.emptyrun_edit.setStatusTip(QtGui.QApplication.translate("Frame", "Enter the detector distance offset in mm.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Empty (background) run to correct diffraction data. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Frame", "Empty Run Correction", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Vanadium background run to correct diffraction data. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Frame", "Vandium Background Run Correction", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Vanadium run to correct diffraction data. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Frame", "Vanadium Run Correction", None, QtGui.QApplication.UnicodeUTF8))
        self.vanbkgdrun_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter vanadium background run number.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.mask_groupbox.setTitle(QtGui.QApplication.translate("Frame", "Binning", None, QtGui.QApplication.UnicodeUTF8))
        self.mask_help_label.setText(QtGui.QApplication.translate("Frame", "Choose a file to set your mask. Note that only the mask information, not the data, will be used in the reduction.\n"
"The data is only used to help you setting the mask.\n"
"The mask information is saved separately so that your data file will NOT be modified.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>User specified maximum TOF of the data. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Frame", "TOF Max", None, QtGui.QApplication.UnicodeUTF8))
        self.resamplex_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter value as ResampleX parameter. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.bintype_combo.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Select type of binning, linear or logarithmic.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.bintype_combo.setItemText(0, QtGui.QApplication.translate("Frame", "Linear Binning", None, QtGui.QApplication.UnicodeUTF8))
        self.bintype_combo.setItemText(1, QtGui.QApplication.translate("Frame", "Logarithmic Binning", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>User specified minimum TOF of the data. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Frame", "TOF Min", None, QtGui.QApplication.UnicodeUTF8))
        self.usebin_button.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Choose to use binning parameter other than resampling. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.usebin_button.setText(QtGui.QApplication.translate("Frame", "Binning", None, QtGui.QApplication.UnicodeUTF8))
        self.binind_checkbox.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Bin data in d-space.  Otherwise in TOF</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.binind_checkbox.setText(QtGui.QApplication.translate("Frame", "Bin In d-spacing", None, QtGui.QApplication.UnicodeUTF8))
        self.resamplex_button.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Choose to resample on X-axis. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.resamplex_button.setText(QtGui.QApplication.translate("Frame", "ResampleX", None, QtGui.QApplication.UnicodeUTF8))
        self.tofmax_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter a value as the allowed maximum TOF. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.binning_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter value as binning parameter.  Negative number is for logarithmic binning.  Positive number is for linear binning. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tofmin_edit.setToolTip(QtGui.QApplication.translate("Frame", "<html><head/><body><p>Enter a value as allowed minimum TOF. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

