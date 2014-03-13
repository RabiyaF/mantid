#This is an extension of refl_gui.py as that is a auto-generated script form pyqt and shouldn't be edited
#so this file provides any extra GUI tweaks not easily doable in the designer
#for the time being this also includes non-GUI behaviour
import refl_window
import refl_save
import csv
from PyQt4 import QtCore, QtGui
from mantid.simpleapi import *
from isis_reflectometry.quick import *
from isis_reflectometry import load_live_runs
from isis_reflectometry.combineMulti import *
from latest_isis_runs import *

from mantid.api import Workspace, WorkspaceGroup

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

canMantidPlot = True

try:
    from mantidplot import *
except ImportError:
    canMantidPlot = False

class ReflGui(refl_window.Ui_windowRefl):
    __instrumentRuns = None
    def __del__(self):
        if self.windowRefl.modFlag:
            self.save(true)
    def on_buttonAuto_clicked(self):
        self.autoFill()
    def on_buttonTransfer_clicked(self):
        self.transfer()
    def on_checkTickAll_stateChanged(self,state):
        self.unTickAll(state)
    def on_textRB_editingFinished(self):
        self.populateList()
    def on_buttonClear_clicked(self):
        self.initTable()
    def on_buttonProcess_clicked(self):
        self.process()
    def on_comboInstrument_activated(self, instrument):
        config['default.instrument'] = self.instrument_list[instrument]
        logger.notice( "Instrument is now: " + str(config['default.instrument']))
        self.textRB.clear()
        self.populateList()
        self.current_instrument = self.instrument_list[instrument]
        self.comboPolarCorrect.setEnabled(self.current_instrument  in self.polarisation_instruments) # Enable as appropriate
        self.comboPolarCorrect.setCurrentIndex(self.comboPolarCorrect.findText('None')) # Reset to None    
    def on_actionOpen_Table_triggered(self):
        self.loadTable()
    def on_actionReload_from_Disk_triggered(self):
        self.reloadTable()
    def on_actionSave_triggered(self):
        self.save()
    def on_actionSave_As_triggered(self):
        self.saveAs()
    def on_actionSave_Workspaces_triggered(self):
        self.saveWorkspaces()
    def actionClose_Refl_Gui_triggered(self):
        self.windowRefl.close()
    def on_actionMantid_Help_triggered(self):
        self.showHelp()
    def on_tableMain_modified(self, row, column):
        if not self.loading:
            self.windowRefl.modFlag = True
            plotbutton = self.tableMain.cellWidget(row, 18).children()[1]
            self.resetPlotButton(plotbutton)
    def on_plotButton_clicked(self):
        plotbutton = self.windowRefl.sender()
        self.plot(plotbutton)
    '''
    Event handler for polarisation correction selection.
    '''
    def on_comboPolarCorr_activated(self):
        if self.current_instrument in self.polarisation_instruments:
            chosen_method = self.comboPolarCorrect.currentText()
            self.current_polarisation_method = self.polarisation_options[chosen_method]
        else:
            logger.notice("Polarisation correction is not supported on " + str(self.current_instrument))
    def setupUi(self, windowRefl):
        super(ReflGui,self).setupUi(windowRefl)
        self.loading = False
        
        '''
        Setup instrument options with defaults assigned.
        '''
        self.instrument_list = ['INTER', 'SURF', 'CRISP', 'POLREF']
        self.polarisation_instruments = ['CRISP', 'POLREF'] 
        self.comboInstrument.addItems(self.instrument_list)
        current_instrument = config['default.instrument'].upper()
        if current_instrument in self.instrument_list:
            self.comboInstrument.setCurrentIndex(self.instrument_list.index(current_instrument))
        else:
            self.comboInstrument.setCurrentIndex(0)
            config['default.instrument'] = 'INTER'
        self.current_instrument = config['default.instrument']
        
        '''
        Setup polarisation options with default assigned
        '''
        self.windowRefl = windowRefl
        self.polarisation_options = {'None' : PolarisationCorrection.NONE, '1-PNR' : PolarisationCorrection.PNR, '2-PA' : PolarisationCorrection.PA }
        self.comboPolarCorrect.clear()
        self.comboPolarCorrect.addItems(self.polarisation_options.keys())
        self.comboPolarCorrect.setCurrentIndex(self.comboPolarCorrect.findText('None'))
        self.current_polarisation_method = self.polarisation_options['None']
        self.comboPolarCorrect.setEnabled(self.current_instrument in self.polarisation_instruments)
        self.labelStatus = QtGui.QLabel("Ready")
        self.statusMain.addWidget(self.labelStatus)
        self.initTable()
        self.populateList()
        self.connectSlots()
    def resetTable(self):
        #switches from current to true, to false to make sure stateChanged fires
        self.checkTickAll.setCheckState(2)
        self.checkTickAll.setCheckState(0)
        for row in range(self.tableMain.rowCount()):
            plotbutton = self.tableMain.cellWidget(row, 18).children()[1]
            self.resetPlotButton(plotbutton)
    def resetPlotButton(self, plotbutton):
        plotbutton.setDisabled(True)
        plotbutton.setProperty('runno', None)
        plotbutton.setProperty('overlapLow', None)
        plotbutton.setProperty('overlapHigh', None)
        plotbutton.setProperty('wksp', None)
    def initTable(self):
        #first check if the table has been changed before clearing it
        if self.windowRefl.modFlag:
            ret, saved = self.windowRefl.savecheck()
            if ret == QtGui.QMessageBox.Cancel:
                return
        self.current_table = None
        self.accMethod = None
        
        for column in range(self.tableMain.columnCount()):
            for row in range(self.tableMain.rowCount()):
                if (column == 0) or (column == 5) or (column == 10):
                    item = QtGui.QTableWidgetItem()
                    item.setText('')
                    item.setToolTip('Runs can be colon delimited to coadd them')
                    self.tableMain.setItem(row, column, item)
                elif (column == 1) or (column == 6) or (column == 11):
                    item = QtGui.QTableWidgetItem()
                    item.setText('')
                    item.setToolTip('Angles are in degrees')
                    self.tableMain.setItem(row, column, item)
                elif (column == 17):
                    check = QtGui.QCheckBox()
                    check.setCheckState(False)
                    check.setToolTip('If checked, the runs in this row will be stitched together')
                    item = QtGui.QWidget()
                    layout = QtGui.QHBoxLayout(item)
                    layout.addWidget(check)
                    layout.setAlignment(QtCore.Qt.AlignCenter)
                    layout.setSpacing(0)
                    layout.setContentsMargins(0, 0, 0, 0)
                    item.setLayout(layout)
                    item.setContentsMargins(0, 0, 0, 0)
                    self.tableMain.setCellWidget(row, 17, item)
                elif (column == 18):
                    button = QtGui.QPushButton('Plot')
                    button.setProperty("row", row)
                    self.resetPlotButton(button)
                    button.setToolTip('Plot the workspaces produced by processing this row.')
                    button.clicked.connect(self.on_plotButton_clicked)
                    item = QtGui.QWidget()
                    layout = QtGui.QHBoxLayout(item)
                    layout.addWidget(button)
                    layout.setAlignment(QtCore.Qt.AlignCenter)
                    layout.setSpacing(0)
                    layout.setContentsMargins(0, 0, 0, 0)
                    item.setLayout(layout)
                    item.setContentsMargins(0, 0, 0, 0)
                    self.tableMain.setCellWidget(row, 18, item)
                else:
                    item = QtGui.QTableWidgetItem()
                    item.setText('')
                    self.tableMain.setItem(row, column, item)
        self.tableMain.resizeColumnsToContents()
        self.windowRefl.modFlag = False
    def connectSlots(self):
        self.checkTickAll.stateChanged.connect(self.on_checkTickAll_stateChanged)
        self.comboInstrument.activated.connect(self.on_comboInstrument_activated)
        self.comboPolarCorrect.activated.connect(self.on_comboPolarCorr_activated)
        self.textRB.returnPressed.connect(self.on_textRB_editingFinished)
        self.buttonAuto.clicked.connect(self.on_buttonAuto_clicked)
        self.buttonSearch.clicked.connect(self.on_textRB_editingFinished)
        self.buttonClear.clicked.connect(self.on_buttonClear_clicked)
        self.buttonProcess.clicked.connect(self.on_buttonProcess_clicked)
        self.buttonTransfer.clicked.connect(self.on_buttonTransfer_clicked)
        self.actionOpen_Table.triggered.connect(self.on_actionOpen_Table_triggered)
        self.actionReload_from_Disk.triggered.connect(self.on_actionReload_from_Disk_triggered)
        self.actionSave.triggered.connect(self.on_actionSave_triggered)
        self.actionSave_As.triggered.connect(self.on_actionSave_As_triggered)
        self.actionSave_Workspaces.triggered.connect(self.on_actionSave_Workspaces_triggered)
        self.actionClose_Refl_Gui.triggered.connect(self.windowRefl.close)
        self.actionMantid_Help.triggered.connect(self.on_actionMantid_Help_triggered)
        self.actionAutofill.triggered.connect(self.on_buttonAuto_clicked)
        self.actionSearch_RB.triggered.connect(self.on_textRB_editingFinished)
        self.actionClear_Table.triggered.connect(self.on_buttonClear_clicked)
        self.actionProcess.triggered.connect(self.on_buttonProcess_clicked)
        self.actionTransfer.triggered.connect(self.on_buttonTransfer_clicked)
        self.tableMain.cellChanged.connect(self.on_tableMain_modified)
    def populateList(self):
        # Clear existing
        self.listMain.clear()
        # Fill with ADS workspaces
        self.populateListADSWorkspaces()
        try:
            selectedInstrument = config['default.instrument'].strip().upper()
            if not self.__instrumentRuns:
                self.__instrumentRuns =  LatestISISRuns(instrument=selectedInstrument)
                self.spinDepth.setMaximum(self.__instrumentRuns.getNumCycles())
            elif not self.__instrumentRuns.getInstrument() == selectedInstrument:
                self.__instrumentRuns =  LatestISISRuns(selectedInstrument)
                self.spinDepth.setMaximum(self.__instrumentRuns.getNumCycles())
            if self.textRB.text():
                runs = []
                self.statusMain.showMessage("Searching Journals for RB number: " + self.textRB.text())
                try:
                    runs = self.__instrumentRuns.getJournalRuns(self.textRB.text(),self.spinDepth.value())
                except:
                    logger.error( "Problem encountered when listing archive runs. Please check your network connection and that you have access to the journal archives.")
                    QtGui.QMessageBox.critical(self.tableMain, 'Error Retrieving Archive Runs',"Problem encountered when listing archive runs. Please check your network connection and that you have access to the journal archives.")
                    runs = []
                self.statusMain.clearMessage()
                for run in runs:
                    self.listMain.addItem(run)
        except Exception as ex:
            logger.notice("Could not list archive runs")
            logger.notice(str(ex))
    def populateListADSWorkspaces(self):
        names = mtd.getObjectNames()
        for ws in names:
            self.listMain.addItem(ws)
    def autoFill(self):
        col = 0
        # make sure all selected cells are in the same row
        sum = 0
        howMany = len(self.tableMain.selectedItems())
        for cell in self.tableMain.selectedItems():
            sum = sum + self.tableMain.row(cell)
        if (howMany):
            selectedrow = self.tableMain.row(self.tableMain.selectedItems()[0])
            if (sum / howMany == selectedrow):
                startrow = selectedrow + 1
                filled = 0
                for cell in self.tableMain.selectedItems():
                    row = startrow
                    txt = cell.text()
                    while (self.tableMain.item(row, 0).text() != ''):
                        item = QtGui.QTableWidgetItem()
                        item.setText(txt)
                        self.tableMain.setItem(row, self.tableMain.column(cell), item)
                        row = row + 1
                        filled = filled + 1
                if not filled:
                    QtGui.QMessageBox.critical(self.tableMain, 'Cannot perform Autofill',"No target cells to autofill. Rows to be filled should contain a run number in their first cell, and start from directly below the selected line.")
            else:
                QtGui.QMessageBox.critical(self.tableMain, 'Cannot perform Autofill',"Selected cells must all be in the same row.")
        else:
            QtGui.QMessageBox.critical(self.tableMain, 'Cannot perform Autofill',"There are no source cells selected.")
    '''
    Create a display name from a workspace.
    '''
    def create_workspace_display_name(self, candidate):
        if isinstance(mtd[candidate], WorkspaceGroup):
            todisplay = candidate # No single run number for a group of workspaces.
        else:
            todisplay = groupGet(mtd[candidate], "samp", "run_number")
        return todisplay
    def transfer(self):
        col = 0
        row = 0
        while (self.tableMain.item(row, 0).text() != ''):
            row = row + 1
        for idx in self.listMain.selectedItems():
            contents = str(idx.text()).strip()
            first_contents = contents.split(':')[0]
            runnumber = None
            if mtd.doesExist(first_contents):
                runnumber = self.create_workspace_display_name(first_contents)
            else:
                try:
                    temp = Load(Filename=first_contents, OutputWorkspace="_tempforrunnumber")
                    runnumber = groupGet("_tempforrunnumber", "samp", "run_number")
                    DeleteWorkspace(temp)
                except:
                    logger.error("Unable to load file. Please check your managed user directories.")
                    QtGui.QMessageBox.critical(self.tableMain, 'Error Loading File',"Unable to load file. Please check your managed user directories.")
            item = QtGui.QTableWidgetItem()
            item.setText(runnumber)
            self.tableMain.setItem(row, col, item)
            item = QtGui.QTableWidgetItem()
            item.setText(self.textRuns.text())
            self.tableMain.setItem(row, col + 2, item)
            col = col + 5
            if col >= 11:
                col = 0
                row = row + 1
    def unTickAll(self,state):
        for row in range(self.tableMain.rowCount()):
            self.tableMain.cellWidget(row, 17).children()[1].setCheckState(state)
    def getAccMethod(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("The Data to be processed required that a Live Data service be started. What accumulation method would you like it to use?")
        msgBox.setIcon(QtGui.QMessageBox.Question)
        AddButton = msgBox.addButton("Add", QtGui.QMessageBox.ActionRole | QtGui.QMessageBox.AcceptRole)
        ReplaceButton = msgBox.addButton("Replace", QtGui.QMessageBox.ActionRole | QtGui.QMessageBox.AcceptRole)
        AppendButton = msgBox.addButton("Append", QtGui.QMessageBox.ActionRole | QtGui.QMessageBox.AcceptRole)
        msgBox.setDefaultButton(AddButton)
        msgBox.setEscapeButton(AddButton)
        reply = msgBox.exec_()
        if msgBox.clickedButton() == AppendButton:
            return "Append"
        elif msgBox.clickedButton() == ReplaceButton:
            return "Replace"
        else:
            return "Add"
    def process(self):
#--------- If "Process" button pressed, convert raw files to IvsLam and IvsQ and combine if checkbox ticked -------------
        try:
            willProcess = True
            rows = self.tableMain.selectionModel().selectedRows()
            rowIndexes=[]
            for idx in rows:
                rowIndexes.append(idx.row())
            if not len(rowIndexes):
                reply = QtGui.QMessageBox.question(self.tableMain, 'Process all rows?',"This will process all rows in the table. Continue?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.No:
                    logger.notice("Cancelled!")
                    willProcess = False
                else:
                    rowIndexes = range(self.tableMain.rowCount())
            if willProcess:
                for row in rowIndexes:  # range(self.tableMain.rowCount()):
                    runno = []
                    loadedRuns = []
                    wksp = []
                    overlapLow = []
                    overlapHigh = []
                    theta = [0, 0, 0]
                    if (self.tableMain.item(row, 0).text() != ''):
                        self.statusMain.showMessage("Processing row: " + str(row + 1))
                        logger.debug("Processing row: " + str(row + 1))
                        for i in range(3):
                            r = str(self.tableMain.item(row, i * 5).text())
                            if (r != ''):
                                runno.append(r)
                            ovLow = str(self.tableMain.item(row, i * 5 + 3).text())
                            if (ovLow != ''):
                                overlapLow.append(float(ovLow))
                            ovHigh = str(self.tableMain.item(row, i * 5 + 4).text())
                            if (ovHigh != ''):
                                overlapHigh.append(float(ovHigh))
                        # Determine resolution
                        if (self.tableMain.item(row, 15).text() == ''):
                            loadedRun = None
                            if load_live_runs.is_live_run(runno[0]):
                                if not self.accMethod:
                                    self.accMethod = self.getAccMethod()
                                loadedRun = load_live_runs.get_live_data(config['default.instrument'], Accumulation = self.accMethod)
                            else:
                                Load(Filename=runno[0], OutputWorkspace="run")
                                loadedRun = mtd["run"]
                            try:
                                dqq = calcRes(loadedRun)
                                item = QtGui.QTableWidgetItem()
                                item.setText(str(dqq))
                                self.tableMain.setItem(row, 15, item)
                                logger.notice("Calculated resolution: " + str(dqq))
                            except IndexError:
                                self.statusMain.clearMessage()
                                logger.error("Cannot calculate resolution owing to unknown log properties. dq/q will need to be manually entered.")
                                return
                        else:
                            dqq = float(self.tableMain.item(row, 15).text())
                        # Populate runlist
                        first_wq = None
                        for i in range(len(runno)):
                            theta, qmin, qmax, wlam, wq = self.dorun(runno[i], row, i)
                            if not first_wq:
                                first_wq = wq # Cache the first Q workspace
                            theta = round(theta, 3)
                            qmin = round(qmin, 3)
                            qmax = round(qmax, 3)
                            wksp.append(wq.name())
                            if (self.tableMain.item(row, i * 5 + 1).text() == ''):
                                item = QtGui.QTableWidgetItem()
                                item.setText(str(theta))
                                self.tableMain.setItem(row, i * 5 + 1, item)
                            if (self.tableMain.item(row, i * 5 + 3).text() == ''):
                                item = QtGui.QTableWidgetItem()
                                item.setText(str(qmin))
                                self.tableMain.setItem(row, i * 5 + 3, item)
                                overlapLow.append(qmin)
                            if (self.tableMain.item(row, i * 5 + 4).text() == ''):
                                item = QtGui.QTableWidgetItem()
                                if i == len(runno) - 1:
                                # allow full high q-range for last angle
                                    qmax = 4 * math.pi / ((4 * math.pi / qmax * math.sin(theta * math.pi / 180)) - 0.5) * math.sin(theta * math.pi / 180)
                                item.setText(str(qmax))
                                self.tableMain.setItem(row, i * 5 + 4, item)
                                overlapHigh.append(qmax)
                            if wksp[i].find(',') > 0 or wksp[i].find(':') > 0:
                                wksp[i] = first_wq.name()
                        plotbutton = self.tableMain.cellWidget(row, 18).children()[1]
                        plotbutton.setProperty('runno',runno)
                        plotbutton.setProperty('overlapLow', overlapLow)
                        plotbutton.setProperty('overlapHigh', overlapHigh)
                        plotbutton.setProperty('wksp', wksp)
                        plotbutton.setEnabled(True)
                        self.statusMain.clearMessage()
            self.accMethod = None
            self.statusMain.clearMessage()
        except:
            self.statusMain.clearMessage()
    def plot(self, plotbutton):
        if not isinstance(plotbutton, QtGui.QPushButton):
            logger.error("Problem accessing cached data: Wrong data type passed, expected QtGui.QPushbutton")
            return
        import unicodedata
        
        #make sure the required data can be retrieved properly
        try:
            runno_u = plotbutton.property('runno')
            runno = []
            for uni in runno_u:
                runno.append(unicodedata.normalize('NFKD', uni).encode('ascii','ignore'))
            wksp_u = plotbutton.property('wksp')
            wksp = []
            for uni in wksp_u:
                wksp.append(unicodedata.normalize('NFKD', uni).encode('ascii','ignore'))
            overlapLow = plotbutton.property('overlapLow')
            overlapHigh = plotbutton.property('overlapHigh')
            row = plotbutton.property('row')
            g = ['g1', 'g2', 'g3']
            wkspBinned = []
            w1 = getWorkspace(wksp[0])
            w2 = getWorkspace(wksp[len(wksp) - 1])
            dqq = float(self.tableMain.item(row, 15).text())
        except:
            logger.error("Unable to plot row, required data couldn't be retrieved")
            resetPlotButton(plotbutton)
            return
        for i in range(len(runno)):
            ws_name_binned = wksp[i] + '_binned'
            ws = getWorkspace(wksp[i])
            if len(overlapLow):
                Qmin = overlapLow[0]
            else:
                Qmin = w1.readX(0)[0]
            if len(overlapHigh):
                Qmax = overlapHigh[len(overlapHigh) - 1]
            else:
                Qmax = max(w2.readX(0))
            Rebin(InputWorkspace=str(wksp[i]), Params=str(overlapLow[i]) + ',' + str(-dqq) + ',' + str(overlapHigh[i]), OutputWorkspace=ws_name_binned)
            wkspBinned.append(ws_name_binned)
            wsb = getWorkspace(ws_name_binned)
            Imin = min(wsb.readY(0))
            Imax = max(wsb.readY(0))
            if canMantidPlot:
                g[i] = plotSpectrum(ws_name_binned, 0, True)
                titl = groupGet(ws_name_binned, 'samp', 'run_title')
                if (i > 0):
                    mergePlots(g[0], g[i])
                if (type(titl) == str):
                    g[0].activeLayer().setTitle(titl)
                g[0].activeLayer().setAxisScale(Layer.Left, Imin * 0.1, Imax * 10, Layer.Log10)
                g[0].activeLayer().setAxisScale(Layer.Bottom, Qmin * 0.9, Qmax * 1.1, Layer.Log10)
                g[0].activeLayer().setAutoScale()
        if (self.tableMain.cellWidget(row, 17).children()[1].checkState() > 0):
            if (len(runno) == 1):
                logger.notice("Nothing to combine!")
            elif (len(runno) == 2):
                outputwksp = runno[0] + '_' + runno[1][3:5]
            else:
                outputwksp = runno[0] + '_' + runno[2][3:5]
            begoverlap = w2.readX(0)[0]
            # get Qmax
            if (self.tableMain.item(row, i * 5 + 4).text() == ''):
                overlapHigh = 0.3 * max(w1.readX(0))
            wcomb = combineDataMulti(wkspBinned, outputwksp, overlapLow, overlapHigh, Qmin, Qmax, -dqq, 1)
            if (self.tableMain.item(row, 16).text() != ''):
                Scale(InputWorkspace=outputwksp, OutputWorkspace=outputwksp, Factor=1 / float(self.tableMain.item(row, 16).text()))
            Qmin = getWorkspace(outputwksp).readX(0)[0]
            Qmax = max(getWorkspace(outputwksp).readX(0))
            if canMantidPlot:
                gcomb = plotSpectrum(outputwksp, 0, True)
                titl = groupGet(outputwksp, 'samp', 'run_title')
                gcomb.activeLayer().setTitle(titl)
                gcomb.activeLayer().setAxisScale(Layer.Left, 1e-8, 100.0, Layer.Log10)
                gcomb.activeLayer().setAxisScale(Layer.Bottom, Qmin * 0.9, Qmax * 1.1, Layer.Log10)
    def dorun(self, runno, row, which):
        g = ['g1', 'g2', 'g3']
        transrun = str(self.tableMain.item(row, which * 5 + 2).text())
        angle = str(self.tableMain.item(row, which * 5 + 1).text())
        loadedRun = runno
        if load_live_runs.is_live_run(runno):
            if not self.accMethod:
                self.accMethod = self.getAccMethod()
            loadedRun = load_live_runs.get_live_data(InstrumentName = config['default.instrument'], Accumulation = self.accMethod)
        wlam, wq, th = quick(loadedRun, trans=transrun, theta=angle)
        if ':' in runno:
            runno = runno.split(':')[0]
        if ',' in runno:
            runno = runno.split(',')[0]
        inst = groupGet(wq, 'inst')
        lmin = inst.getNumberParameter('LambdaMin')[0] + 1
        lmax = inst.getNumberParameter('LambdaMax')[0] - 2
        qmin = 4 * math.pi / lmax * math.sin(th * math.pi / 180)
        qmax = 4 * math.pi / lmin * math.sin(th * math.pi / 180)
        return th, qmin, qmax, wlam, wq
    def saveTable(self, filename):
        try:
            writer = csv.writer(open(filename, "wb"))
            for row in range(self.tableMain.rowCount()):
                rowtext = []
                for column in range(self.tableMain.columnCount() - 2):
                    rowtext.append(self.tableMain.item(row, column).text())
                if (len(rowtext) > 0):
                    writer.writerow(rowtext)
            self.current_table = filename
            logger.notice("Saved file to " + filename)
            self.windowRefl.modFlag = False
        except:
            return False
        self.windowRefl.modFlag = False
        return True
    def save(self, failsave = False):
        filename = ''
        if failsave:
            #this is an emergency autosave as the program is failing
            logger.error("The ISIS Reflectonomy GUI has encountered an error, it will now attempt to save a copy of your work.")
            msgBox = QtGui.QMessageBox()
            msgBox.setText("The ISIS Reflectonomy GUI has encountered an error, it will now attempt to save a copy of your work.\nPlease check the log for details.")
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgBox.setIcon(QtGui.QMessageBox.Critical)
            msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
            msgBox.setEscapeButton(QtGui.QMessageBox.Ok)
            msgBox.exec_()
            import datetime
            failtime = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            if self.current_table:
                filename = self.current_table.rsplit('.',1)[0] + "_recovered_" + failtime + ".tbl"
            else:
                mantidDefault = config['defaultsave.directory']
                if os.path.exists(mantidDefault):
                    filename = os.path.join(mantidDefault,"mantid_reflectometry_recovered_" + failtime + ".tbl")
                else:
                    import tempfile
                    tempDir = tempfile.gettempdir()
                    filename = os.path.join(tempDir,"mantid_reflectometry_recovered_" + failtime + ".tbl")
        else:
            #this is a save-on-quit or file->save
            if self.current_table:
                filename = self.current_table
            else:
                saveDialog = QtGui.QFileDialog(self.widgetMainRow.parent(), "Save Table")
                saveDialog.setFileMode(QtGui.QFileDialog.AnyFile)
                saveDialog.setNameFilter("Table Files (*.tbl);;All files (*.*)")
                saveDialog.setDefaultSuffix("tbl")
                saveDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
                if saveDialog.exec_():
                    filename = saveDialog.selectedFiles()[0]
                else:
                    return False
        return self.saveTable(filename)
    def saveAs(self):
        saveDialog = QtGui.QFileDialog(self.widgetMainRow.parent(), "Save Table")
        saveDialog.setFileMode(QtGui.QFileDialog.AnyFile)
        saveDialog.setNameFilter("Table Files (*.tbl);;All files (*.*)")
        saveDialog.setDefaultSuffix("tbl")
        saveDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        if saveDialog.exec_():
            filename = saveDialog.selectedFiles()[0]
            self.saveTable(filename)
    def loadTable(self):
        self.loading = True
        loadDialog = QtGui.QFileDialog(self.widgetMainRow.parent(), "Open Table")
        loadDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        loadDialog.setNameFilter("Table Files (*.tbl);;All files (*.*)")
        if loadDialog.exec_():
            try:
                #before loading make sure you give them a chance to save
                if self.windowRefl.modFlag:
                    ret, saved = self.windowRefl.savecheck()
                    if ret == QtGui.QMessageBox.Cancel:
                        #if they hit cancel abort the load
                        self.loading = False
                        return
                self.resetTable()
                filename = loadDialog.selectedFiles()[0]
                self.current_table = filename
                reader = csv.reader(open(filename, "rb"))
                row = 0
                for line in reader:
                    if (row < 100):
                        for column in range(self.tableMain.columnCount() - 2):
                            item = QtGui.QTableWidgetItem()
                            item.setText(line[column])
                            self.tableMain.setItem(row, column, item)
                        row = row + 1
            except:
                logger.error('Could not load file: ' + str(filename) + '. File not found or unable to read from file.')
        self.loading = False
        self.windowRefl.modFlag = False
    def reloadTable(self):
        self.loading = True
        filename = self.current_table
        if filename:
            if self.windowRefl.modFlag:
                msgBox = QtGui.QMessageBox()
                msgBox.setText("The table has been modified. Are you sure you want to reload the table and lose your changes?")
                msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                msgBox.setIcon(QtGui.QMessageBox.Question)
                msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
                msgBox.setEscapeButton(QtGui.QMessageBox.No)
                ret = msgBox.exec_()
                if ret == QtGui.QMessageBox.No:
                    #if they hit No abort the reload
                    self.loading = False
                    return
            try:
                self.resetTable()
                reader = csv.reader(open(filename, "rb"))
                row = 0
                for line in reader:
                    if (row < 100):
                        for column in range(self.tableMain.columnCount() - 2):
                            item = QtGui.QTableWidgetItem()
                            item.setText(line[column])
                            self.tableMain.setItem(row, column, item)
                        row = row + 1
                self.windowRefl.modFlag = False
            except:
                logger.error('Could not load file: ' + str(filename) + '. File not found or unable to read from file.')
        else:
            logger.notice('No file in table to reload.')
        self.loading = False
    def saveWorkspaces(self):
        try:
            Dialog = QtGui.QDialog()
            u = refl_save.Ui_SaveWindow()
            u.setupUi(Dialog)
            Dialog.exec_()
        except Exception as ex:
            logger.notice("Could not open save workspace dialog")
            logger.notice(str(ex))
    def showHelp(self):
        import webbrowser
        webbrowser.open('http://www.mantidproject.org/ISIS_Reflectometry_GUI')
'''
Get a representative workspace from the input workspace.
'''        
def get_representative_workspace(run):
    if isinstance(run, WorkspaceGroup):
        run_number = groupGet(run[0], "samp", "run_number")
        _runno = Load(Filename=str(run_number))
    elif isinstance(run, Workspace):
        _runno = run
    elif isinstance(run, int):
        _runno = Load(Filename=run, OutputWorkspace=runno)
    elif isinstance(run, str) and mtd.doesExist(run): 
        ws = mtd[run]
        if isinstance(ws, WorkspaceGroup):
            run_number = groupGet(ws[0], "samp", "run_number")
            _runno = Load(Filename=str(run_number))
    elif isinstance(run, str):
        _runno = Load(Filename=run.replace("raw", "nxs", 1), OutputWorkspace=runno)
    else:
        raise TypeError("Must be a workspace, int or str")
    return _runno
'''
Calculate the resolution from the slits.
'''
def calcRes(run):
    runno = get_representative_workspace(run)
    # Get slits and detector angle theta from NeXuS
    th = groupGet(runno, 'samp', 'THETA')
    inst = groupGet(runno, 'inst')
    s1z = inst.getComponentByName('slit1').getPos().getZ() * 1000.0  # distance in mm
    s2z = inst.getComponentByName('slit2').getPos().getZ() * 1000.0  # distance in mm
    s1vg = inst.getComponentByName('slit1')
    s1vg = s1vg.getNumberParameter('vertical gap')[0]
    s2vg = inst.getComponentByName('slit2')
    s2vg = s2vg.getNumberParameter('vertical gap')[0]
    logger.notice( "s1vg=" + str(s1vg) + " s2vg=" + str(s2vg) + " theta=" + str(th))
    #1500.0 is the S1-S2 distance in mm for SURF!!!
    resolution = math.atan((s1vg + s2vg) / (2 * (s2z - s1z))) * 180 / math.pi / th
    logger.notice( "dq/q=" + str(resolution))
    if not type(run) == type(Workspace):
        DeleteWorkspace(runno)
    return resolution
def groupGet(wksp, whattoget, field=''):
    '''
    returns information about instrument or sample details for a given workspace wksp,
    also if the workspace is a group (info from first group element)
    '''
    if (whattoget == 'inst'):
        if isinstance(wksp, str):
            at = getattr(mtd[wksp],'size',None)
            if callable(at):
                return mtd[wksp][0].getInstrument()
            else:
                return mtd[wksp].getInstrument()
        elif isinstance(wksp, Workspace):
            at = getattr(wksp,'size',None)
            if callable(at):
                return wksp[0].getInstrument()
            else:
                return wksp.getInstrument()
        else:
            return 0
    elif (whattoget == 'samp' and field != ''):
        if isinstance(wksp, str):
            at = getattr(mtd[wksp],'size',None)
            if callable(at):
                try:
                    log = mtd[wksp][0].getRun().getLogData(field).value
                    if (type(log) is int or type(log) is str):
                        res = log
                    else:
                        res = log[-1]
                except RuntimeError:
                    res = 0
                    logger.error( "Block " + str(field) + " not found.")
            else:
                try:
                    log = mtd[wksp].getRun().getLogData(field).value
                    if (type(log) is int or type(log) is str):
                        res = log
                    else:
                        res = log[-1]
                except RuntimeError:
                    res = 0
                    logger.error( "Block " + str(field) + " not found.")
        elif isinstance(wksp, Workspace):
            at = getattr(wksp,'size',None)
            if callable(at):
                try:
                    log = wksp[0].getRun().getLogData(field).value
                    if (type(log) is int or type(log) is str):
                        res = log
                    else:
                        res = log[-1]
                except RuntimeError:
                    res = 0
                    logger.error( "Block " + str(field) + " not found.")
            else:
                try:
                    log = wksp.getRun().getLogData(field).value
                    if (type(log) is int or type(log) is str):
                        res = log
                    else:
                        res = log[-1]
                except RuntimeError:
                    res = 0
                    logger.error( "Block " + str(field) + " not found.")
        else:
            res = 0
        return res
    elif (whattoget == 'wksp'):
        if isinstance(wksp, str):
            at = getattr(mtd[wksp],'size',None)
            if callable(at):
                return mtd[wksp][0].getNumberHistograms()
            else:
                return mtd[wksp].getNumberHistograms()
        elif isinstance(wksp, Workspace):
            at = getattr(wksp,'size',None)
            if callable(at):
                return mtd[wksp][0].getNumberHistograms()
            else:
                return wksp.getNumberHistograms()
        else:
            return 0
def getWorkspace(wksp):
    if isinstance(wksp, Workspace):
        return wksp
    elif isinstance(wksp, str):
        if isinstance(mtd[wksp], WorkspaceGroup):
            wout = mtd[wksp][0]
        else:
            wout = mtd[wksp]
        return wout
    else:
        logger.error( "Unable to get workspace: " + str(wksp))
        return 0
