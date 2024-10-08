####################################

# (c) Radu Berdan
# ArC Instruments Ltd.

# This code is licensed under GNU v3 license (see LICENSE.txt for details)

####################################

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import time

from arc1pyqt import state
HW = state.hardware
APP = state.app
CB = state.crossbar
from arc1pyqt.Globals import fonts
from arc1pyqt.modutils import BaseThreadWrapper, BaseProgPanel, \
        makeDeviceList, ModTag

from arc1pyqt.database_methods import inserting_data_into_database_singleRead_MultiBias_setParameters
from arc1pyqt.database_methods import inserting_data_into_database_allOrRangeRead_MultiBias_setParameters
from arc1pyqt.database_methods import inserting_data_into_database_allFunction_experimentalDetail
from arc1pyqt.database_methods import inserting_data_into_database_setFirstLocation

tag = "MB"


class ThreadWrapper(BaseThreadWrapper):

    updateCurrentRead=QtCore.pyqtSignal(float)

    def __init__(self, wLines, bLine, RW, V, pw):
        super().__init__()
        self.wLines=wLines
        self.bLine=bLine
        self.RW=RW
        self.V=V
        self.pw=pw

    @BaseThreadWrapper.runner
    def run(self):

        # new
        storeLocation = 0
        arrayForStoreData = []  # Array to store the final result
        db_file = 'Database.db'
        # new

        global tag

        if (self.RW==1): # READ operation
            valuesNew=HW.ArC.read_floats(3)
            current=valuesNew[1]/valuesNew[0]
            self.updateCurrentRead.emit(current)

        if (self.RW==2):
            for device in range(1,HW.conf.words+1):
                print("first write"+ str(device))
                # new
                # get the start position of the cycle
                start_for_wb = len(CB.history[device][self.bLine])
                end_for_wb   = start_for_wb + 1
                print("the local position of the wordline and bitline for start")
                print(device, self.bLine)
                print(start_for_wb)
                arrayForStoreData.append((device, self.bLine, start_for_wb,end_for_wb))
                print(arrayForStoreData)
                # new
                valuesNew=HW.ArC.read_floats(3)
                self.sendData.emit(device,self.bLine,valuesNew[0],valuesNew[1],valuesNew[2],"MB")

            for device in range(1,HW.conf.words+1):
                print("second write"+ str(device))
                valuesNew=HW.ArC.read_floats(3)
                if device in self.wLines:
                    self.sendData.emit(device,self.bLine,valuesNew[0],self.V,self.pw,"P")
                else:
                    self.sendData.emit(device,self.bLine,valuesNew[0],self.V/2,self.pw,"P")
                self.updateTree.emit(device,self.bLine)
                print("updateTree  "+ str(device) +"  "+ str(self.bLine))

            for w, b, start_for_wb, end_for_wb in arrayForStoreData:
                print("Lai Gan")
                wafer = '6F01'
                insulator = 'TiOx'
                cross_sectional_area = 'SA10'
                die = 'D119'

                # for the whole parameters that are moved to the newest position
                if (storeLocation == 1):
                    inserting_data_into_database_allOrRangeRead_MultiBias_setParameters(db_file, wafer, insulator,
                                                                                        cross_sectional_area, die, w, b)
                    print("this is the allorRangeRead set parameters")
                else:  # for the start location
                    inserting_data_into_database_setFirstLocation(db_file, wafer, die, w, b)
                    print("this is the set first location")
                # this is not the first time set the location, so storeLocation = 1
                storeLocation = 1

                # Inner loop, modifying start_for_wb and end_for_wb
                for i in range(start_for_wb, end_for_wb + 1):
                    # Call the function to insert data into the database, using values from CB.history
                    inserting_data_into_database_allFunction_experimentalDetail(
                        db_file,
                        CB.history[w][b][i][0],  # Assume history is a nested list/dictionary
                        CB.history[w][b][i][1],
                        CB.history[w][b][i][2],
                        CB.history[w][b][i][3],
                        CB.history[w][b][i][4],
                        CB.history[w][b][i][5]
                    )


class MultiBias(BaseProgPanel):

    def __init__(self, short=False):
        super().__init__(title="MultiBias", \
                description="Apply WRITE or READ pulses to multiple active "
                "wordlines. Read from one bitline.", short=short)
        self.initUI()

    def initUI(self):

        vbox1=QtWidgets.QVBoxLayout()

        titleLabel = QtWidgets.QLabel(self.title)
        titleLabel.setFont(fonts.font1)
        descriptionLabel = QtWidgets.QLabel(self.description)
        descriptionLabel.setFont(fonts.font3)
        descriptionLabel.setWordWrap(True)

        isInt=QtGui.QIntValidator()
        isFloat=QtGui.QDoubleValidator()

        leftLabels=['WRITE amplitude (V)', \
                    'WRITE pulse width (us)',\
                    'READ voltage (V)']

        leftInit=  ['1',\
                    '100', \
                    '0.5']

        self.leftEdits=[]

        gridLayout=QtWidgets.QGridLayout()
        gridLayout.setColumnStretch(0,3)
        gridLayout.setColumnStretch(1,3)
        gridLayout.setColumnStretch(3,5)

        if self.short==False:
            gridLayout.setColumnStretch(7,2)

        lineLeft=QtWidgets.QFrame()
        lineLeft.setFrameShape(QtWidgets.QFrame.VLine)
        lineLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        lineLeft.setLineWidth(1)

        gridLayout.addWidget(lineLeft, 0, 2, 6, 1)

        label_wlines=QtWidgets.QLabel("Active Wordlines")
        self.edit_wlines=QtWidgets.QLineEdit("1 2")

        label_blines=QtWidgets.QLabel("Active Bitline")
        self.edit_blines=QtWidgets.QSpinBox()
        self.edit_blines.setRange(1,32)
        self.edit_blines.setSingleStep(1)
        self.edit_blines.setValue(1)

        label_current=QtWidgets.QLabel("Current on Active Bitline:")
        label_suffix=QtWidgets.QLabel("uA")

        self.edit_current=QtWidgets.QLineEdit("0")
        self.edit_current.setReadOnly(True)

        gridLayout.addWidget(label_wlines,0,0)
        gridLayout.addWidget(self.edit_wlines,0,1)
        gridLayout.addWidget(label_blines,1,0)
        gridLayout.addWidget(self.edit_blines,1,1)

        gridLayout.addWidget(label_current,0,3)
        gridLayout.addWidget(self.edit_current,1,3)
        gridLayout.addWidget(label_suffix,1,4)

        for i in range(len(leftLabels)):
            lineLabel=QtWidgets.QLabel()
            #lineLabel.setFixedHeight(50)
            lineLabel.setText(leftLabels[i])
            gridLayout.addWidget(lineLabel, i+2,0)

            lineEdit=QtWidgets.QLineEdit()
            lineEdit.setText(leftInit[i])
            lineEdit.setValidator(isFloat)
            self.leftEdits.append(lineEdit)
            gridLayout.addWidget(lineEdit, i+2,1)

        vbox1.addWidget(titleLabel)
        vbox1.addWidget(descriptionLabel)

        self.vW=QtWidgets.QWidget()
        self.vW.setLayout(gridLayout)
        self.vW.setContentsMargins(0,0,0,0)

        scrlArea=QtWidgets.QScrollArea()
        scrlArea.setWidget(self.vW)
        scrlArea.setContentsMargins(0,0,0,0)
        scrlArea.setWidgetResizable(False)
        scrlArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        scrlArea.installEventFilter(self)

        vbox1.addWidget(scrlArea)
        vbox1.addStretch()

        if self.short==False:

            self.hboxProg=QtWidgets.QHBoxLayout()

            push_write = self.makeControlButton('WRITE', self.apply_write)
            push_read = self.makeControlButton('READ', self.apply_read)

            self.hboxProg.addWidget(push_write)
            self.hboxProg.addWidget(push_read)

            vbox1.addLayout(self.hboxProg)

        self.setLayout(vbox1)
        self.gridLayout=gridLayout

        self.registerPropertyWidget(self.leftEdits[0], "vwrite")
        self.registerPropertyWidget(self.leftEdits[1], "pwwrite")
        self.registerPropertyWidget(self.leftEdits[2], "vread")

    def apply_multiBias(self, RW):
        wLines=self.extract_wordlines()
        if wLines==False:
            self.throwError()
        else:
            if HW.ArC is not None:
                job="50"

                # new
                print("set parameter")
                db_file = 'Database.db'
                insulator = 'TiOx'
                cross_sectional_area = 'SA10'
                # valuesNew = HW.ArC.read_floats(3)
                # current = valuesNew[1] / valuesNew[0]
                # print(current)

                # multibias set parameters
                inserting_data_into_database_singleRead_MultiBias_setParameters(
                    db_file, insulator, cross_sectional_area, str(wLines), self.edit_blines.value(), self.leftEdits[0].text(),
                    self.leftEdits[1].text(), self.leftEdits[2].text(), None, str(RW)
                )
                # new

                HW.ArC.write_b(job+"\n")

                self.sendParams()

                HW.ArC.write_b(str(len(wLines))+"\n")
                HW.ArC.write_b(str(self.edit_blines.value())+"\n")
                HW.ArC.write_b(str(RW)+"\n")
                print("THIS IS :"+str(wLines))                      # Active wordline
                print("THIS IS :"+str(self.edit_blines.value()))    # Active bitline
                print("THIS IS :"+str(self.leftEdits[0].text()))    # Write amplitude
                print("THIS IS :"+str(self.leftEdits[1].text()))    # Write pulse width
                print("THIS IS :"+str(self.leftEdits[2].text()))    # Read voltage
                print("THIS IS :"+str(RW))                          # whether you type read or write

                for nr in wLines:
                    HW.ArC.write_b(str(nr)+"\n")

                wrapper = ThreadWrapper(wLines, \
                        int(self.edit_blines.value()), RW, \
                        float(self.leftEdits[0].text()), \
                        float(self.leftEdits[1].text())/1000000)

                # Another signal to connect. As the thread created by the
                # execute method takes ownership of the wrapper it does not
                # get destroyed when the var goes out of scope. It will only
                # happen when it goes out of scope later when the tread
                # is finished.
                wrapper.updateCurrentRead.connect(self.updateCurrentRead)
                self.execute(wrapper, wrapper.run)

    def sendParams(self):
        HW.ArC.write_b(str(float(self.leftEdits[0].text()))+"\n")
        HW.ArC.write_b(str(float(self.leftEdits[1].text())/1000000)+"\n")
        HW.ArC.write_b(str(float(self.leftEdits[2].text()))+"\n")

    def apply_write(self):
        self.apply_multiBias(2)

    def apply_read(self):
        self.apply_multiBias(1)

    def extract_wordlines(self):
        wlines=[]
        try:
            wlines_txt=list(self.edit_wlines.text().split(" "))
            for nr in wlines_txt:
                w=int(nr)
                if w<1 or w>32:
                    return False
                else:
                    wlines.append(w)
            return wlines
        except:
            return False

    def updateCurrentRead(self, value):
        self.edit_current.setText(str(value*1000000))

    def eventFilter(self, object, event):
        if event.type()==QtCore.QEvent.Resize:
            self.vW.setFixedWidth(event.size().width()-object.verticalScrollBar().width())
        return False

    def disableProgPanel(self,state):
        if state==True:
            self.hboxProg.setEnabled(False)
        else:
            self.hboxProg.setEnabled(True)

    def throwError(self):
        reply = QtWidgets.QMessageBox.question(self, "Error",
            "Formatting of active worlines input box is wrong. " +
            "Check for double spaces, trailing spaces, " +
            "and addresses larger than 32 or smaller than 1.",
            QtWidgets.QMessageBox.Ok)
        event.ignore()


tags = { 'top': ModTag(tag, "MultiBias", None) }
