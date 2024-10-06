from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import numpy as np
import json
import re
import imp
import pkgutil
import time
from functools import partial
import pyqtgraph as pg
sys.path.append('C:\\Users\\Alin\\Desktop\\arc1_pyqt')
import config
#import probelibrary

from probelibrary import ProbeStation
from controller import make_controller
from controller import CNTRL_TYPE

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore, QtGui, QtWidgets


import arc1pyqt.Globals.fonts as fonts
import arc1pyqt.Globals.styles as styles
from arc1pyqt.Globals import functions
from arc1pyqt import state
HW = state.hardware
APP = state.app
CB = state.crossbar
from arc1pyqt import modutils
from arc1pyqt.modutils import BaseThreadWrapper, BaseProgPanel, \
        makeDeviceList, ModTag

THIS_DIR = os.path.dirname(__file__)

def _log(*args, **kwargs):
    if bool(os.environ.get('TMMDBG', False)):
        print(*args, file=sys.stderr, **kwargs)


class InitChuckProcess(BaseThreadWrapper):

    def __init__(self, probe):
        super().__init__()
        self.probestation = probe
        
    @BaseThreadWrapper.runner
    def init(self):
        print('Running initialisation')
        self.probestation.initchuck()
    
    @BaseThreadWrapper.runner
    def citire_rram(self):
        for i in range (5):
            print("astept ampulea")
            time.sleep(1)
        print("Reading rram")
        time.sleep(5)
        print("Reading rram done")

    @BaseThreadWrapper.runner
    def miscare(self):
        print("Probe ul se muta unde are nevoie")
        time.sleep(5)
        print("Incepe citirea-trimit semnal se asteapta perioada definita")
        time.sleep(5)
        print("Ma mut de aici")

    @BaseThreadWrapper.runner
    def send_signal(self):
        self.miscare()
        self.citire_rram()

    @BaseThreadWrapper.runner
    def move_relative(self, dx, dy, xy_velocity):
	#move relatively in x-y direction in um units
        self.probestation.move_relative(dx,dy,xy_velocity)
		#time.sleep(time_move_fast)
        #print('Another process', number)
        #self.probestation.move_relative()

    @BaseThreadWrapper.runner
    def set_chuck_heights(self, type, value):
        self.probestation.set_chuck_heights(type, value)

    @BaseThreadWrapper.runner
    def read_chuck_heights(self):
        self.probestation.read_chuck_heights()

    @BaseThreadWrapper.runner
    def move_separation(self):
        self.probestation.move_separation()

    @BaseThreadWrapper.runner
    def move_contact(self):
        self.probestation.move_contact()

    @BaseThreadWrapper.runner
    def set_chuck_index(self, dx, dy):
        self.probestation.set_chuck_index(dx, dy)

    @BaseThreadWrapper.runner
    def read_chuck_index(self):
        self.probestation.read_chuck_index()

    @BaseThreadWrapper.runner
    def read_index_position(self):
        self.probestation.read_index_position()

    @BaseThreadWrapper.runner
    def move_chuck_index(self, ix, iy):
        self.probestation.move_chuck_index(ix, iy)

    @BaseThreadWrapper.runner
    def read_subdice(self):
        self.probestation.read_subdice()

    @BaseThreadWrapper.runner
    def read_any_row(self, r):
        self.probestation.read_any_row(r)
        
    @BaseThreadWrapper.runner
    def read_row_range(self,ix,iy):
        self.probestation.read_row_range(ix, iy)

    @BaseThreadWrapper.runner
    def read_full_wafer(self):
        self.probestation.read_full_wafer()

    @BaseThreadWrapper.runner
    def read_defined(self):
        self.probestation.read_defined()


class Process(BaseThreadWrapper):

    def __init__(self, deviceList, params = {}):
        super().__init__()
        self.deviceList = deviceList
        self.params = params


    @BaseThreadWrapper.runner
    def run(self):
        print('Starting run')

        # self.sendParams()

        for device in self.deviceList:
            w = device[0]
            b = device[1]
            self.highlight.emit(w, b)

            for _ in range(10):
                time.sleep(0.25)
                print('Doing things on %d %d' % (w, b))

            self.updateTree.emit(w, b)

        self.log("TestModule finished")

    def readDevice(self, w, b):
        pass

class TestModule(BaseProgPanel):

    def __init__(self, short=False):
        super().__init__(title="TestModule",
            description="Demo module for ArC1", short=short)   
        self.short = short
        self.initUI()
        self.button.clicked.connect(self.MoveWafer)
        self.doOne.clicked.connect(self.applyToOne)
        self.doRange.clicked.connect(self.applyToRange)
        self.doAll.clicked.connect(self.applyToAll)
        self.move_up.clicked.connect(self.manual_control)
        self.move_down.clicked.connect(self.manual_control)
        self.move_left.clicked.connect(self.manual_control)
        self.move_right.clicked.connect(self.manual_control)
        self.move_separation.clicked.connect(self.manual_control)
        self.move_contact.clicked.connect(self.manual_control)
        self.set_index_dice.clicked.connect(self.manual_control)
        self.set_index_subdice.clicked.connect(self.manual_control)
        #self.controller=make_controller(CNTRL_TYPE.PROLOGIX,20, ['COM4'])
        self.probestation =  ProbeStation(22, CNTRL_TYPE.PROLOGIX, ['COM4'])

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        #push button "Move Probe"
        self.button = QtWidgets.QPushButton('Move Probe!')
        layout.addWidget(self.button)

        # "apply" push bottons for readings
        hbox = QtWidgets.QHBoxLayout()
        self.doOne = QtWidgets.QPushButton('Apply to One')
        self.doRange = QtWidgets.QPushButton('Apply to Range')
        self.doAll = QtWidgets.QPushButton('Apply to All')
        hbox.addWidget(self.doOne)
        hbox.addWidget(self.doRange)
        hbox.addWidget(self.doAll)
        hbox.addWidget(self.doAll)


        #Spinbox read row number
            #spinbox label
        self.spinBox_anyrow_label = QLabel('Read One Row', self)
        self.spinBox_anyrow_label.setGeometry(0, 30, 80, 20)
            #spinbox row
        self.spinBox_anyrow = QtWidgets.QSpinBox(self)
        self.spinBox_anyrow.setGeometry(QtCore.QRect(20, 50, 42, 22))
        self.spinBox_anyrow.setMaximum(16)
        self.spinBox_anyrow.setSingleStep(1)
        self.spinBox_anyrow.setObjectName("spinBox")
        #Spinboxes read row range
            #spinbox label
        self.spinBox_rowrange_label = QLabel('Read Row Range', self)
        self.spinBox_rowrange_label.setGeometry(0, 75, 90, 20)
            #spinbox "from" label
        self.spinBox_rowrange_label = QLabel('from', self)
        self.spinBox_rowrange_label.setGeometry(20, 90, 90, 20)
            #spinbox "to" label
        self.spinBox_rowrange_label = QLabel('to', self)
        self.spinBox_rowrange_label.setGeometry(70, 90, 90, 20)
            #spinbox "from"
        self.spinBox_rowrangeto = QtWidgets.QSpinBox(self)
        self.spinBox_rowrangeto.setGeometry(QtCore.QRect(20, 110, 42, 22))
        self.spinBox_rowrangeto.setMaximum(16)
        self.spinBox_rowrangeto.setSingleStep(1)
        self.spinBox_rowrangeto.setObjectName("rowrangeto")
            #spinbox "to"
        self.spinBox_rowrangefrom = QtWidgets.QSpinBox(self)
        self.spinBox_rowrangefrom.setGeometry(QtCore.QRect(70, 110, 42, 22))
        self.spinBox_rowrangefrom.setMaximum(16)
        self.spinBox_rowrangefrom.setSingleStep(1)
        self.spinBox_rowrangefrom.setObjectName("rowrangefrom")

        #Radio Buttons
        self.RB_anyrow = QtWidgets.QRadioButton(self)
        self.RB_anyrow.setChecked(True)
        self.RB_anyrow.setGeometry(QtCore.QRect(0, 50, 15, 15))
        self.RB_rowrange = QtWidgets.QRadioButton(self)
        self.RB_rowrange.setGeometry(QtCore.QRect(0, 102, 15, 15))
        self.RB_fullwafer = QLabel('Read Full Wafer', self)
        self.RB_fullwafer.setGeometry(0, 135, 80, 20)
        self.RB_fullwafer = QtWidgets.QRadioButton(self)
        self.RB_fullwafer.setGeometry(QtCore.QRect(0, 155, 15, 15))
        self.RB_desired = QLabel('Read Selected Dice', self)
        self.RB_desired.setGeometry(0, 170, 100, 20)
        self.RB_desired = QtWidgets.QRadioButton(self)
        self.RB_desired.setGeometry(QtCore.QRect(0, 190, 15, 15))
        self.manual = QtWidgets.QRadioButton(self)
        self.manual.setGeometry(QtCore.QRect(120, 102, 15, 15))

        #subdice checkboxes
        self.subdice_label = QLabel('Subdice Map', self)
        self.subdice_label.setGeometry(QtCore.QRect(130, 33, 100, 15))
        self.CB_00= QtWidgets.QCheckBox(self)
        self.CB_00.setChecked(True)
        self.CB_00.setGeometry(QtCore.QRect(130, 50, 15, 15))
        self.CB_00_label = QLabel('00', self)
        self.CB_00_label.setGeometry(145, 50, 15, 15)
        self.CB_01 = QtWidgets.QCheckBox(self)
        self.CB_01.setGeometry(QtCore.QRect(160, 50, 15, 15))
        self.CB_01_label = QLabel('01', self)
        self.CB_01_label.setGeometry(175, 50, 15, 15)
        self.CB_02 = QtWidgets.QCheckBox(self)
        self.CB_02.setGeometry(QtCore.QRect(190, 50, 15, 15))
        self.CB_02_label = QLabel('02', self)
        self.CB_02_label.setGeometry(205, 50, 15, 15)
        self.CB_10 = QtWidgets.QCheckBox(self)
        self.CB_10.setGeometry(QtCore.QRect(130, 65, 15, 15))
        self.CB_10_label = QLabel('10', self)
        self.CB_10_label.setGeometry(145, 65, 15, 15)
        self.CB_11 = QtWidgets.QCheckBox(self)
        self.CB_11.setGeometry(QtCore.QRect(160, 65, 15, 15))
        self.CB_11_label = QLabel('11', self)
        self.CB_11_label.setGeometry(175, 65, 15, 15)
        self.CB_12 = QtWidgets.QCheckBox(self)
        self.CB_12.setGeometry(QtCore.QRect(190, 65, 15, 15))
        self.CB_12_label = QLabel('12', self)
        self.CB_12_label.setGeometry(205, 65, 15, 15)
        self.CB_20 = QtWidgets.QCheckBox(self)
        self.CB_20.setGeometry(QtCore.QRect(130, 80, 15, 15))
        self.CB_20_label = QLabel('20', self)
        self.CB_20_label.setGeometry(145, 80, 15, 15)
        self.CB_21 = QtWidgets.QCheckBox(self)
        self.CB_21.setGeometry(QtCore.QRect(160, 80, 15, 15))
        self.CB_21_label = QLabel('21', self)
        self.CB_21_label.setGeometry(175, 80, 15, 15)
        self.CB_22 = QtWidgets.QCheckBox(self)
        self.CB_22.setGeometry(QtCore.QRect(190, 80, 15, 15))
        self.CB_22_label = QLabel('22', self)
        self.CB_22_label.setGeometry(205, 80, 15, 15)

        #manual control push buttons
        self.move_up_label=QtWidgets.QLabel('Manual Control', self)
        self.move_up_label.setGeometry(140, 100, 80, 20)
        self.move_up = QtWidgets.QPushButton('up',self)
        self.move_up.setGeometry(150, 120, 40, 20)
        self.move_down = QtWidgets.QPushButton('down',self)
        self.move_down.setGeometry(150, 160, 40, 20)
        self.move_left = QtWidgets.QPushButton('L',self)
        self.move_left.setGeometry(130, 140, 30, 20)
        self.move_right = QtWidgets.QPushButton('R',self)
        self.move_right.setGeometry(180, 140, 30, 20)
        self.move_contact = QtWidgets.QPushButton('C',self)
        self.move_contact.setGeometry(130, 185, 20, 20)
        self.move_separation = QtWidgets.QPushButton('S',self)
        self.move_separation.setGeometry(150, 185, 20, 20)
        self.set_index_dice = QtWidgets.QPushButton('Di',self)
        self.set_index_dice.setGeometry(170, 185, 20, 20)
        self.set_index_subdice = QtWidgets.QPushButton('di',self)
        self.set_index_subdice.setGeometry(190, 185, 20, 20)

        layout.addItem(QtWidgets.QSpacerItem(40, 10, \
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        layout.addLayout(hbox)
        self.setLayout(layout)

    def gather_data(self):
        return 1

    def check(self):
        #returns the subdice ticked cell's coordinate to a global variable
        (i,j,k,l,n)=(0,0,0,0,3)
        size = n * n
        list=[self.CB_00.isChecked(), self.CB_01.isChecked(), \
              self.CB_02.isChecked(), self.CB_10.isChecked(), \
              self.CB_11.isChecked(), self.CB_12.isChecked(), \
              self.CB_20.isChecked(), self.CB_21.isChecked(), \
              self.CB_22.isChecked()]
        for i in range(len(list)):
            if list[i]==True:
                l=l+1
        print("no of checked boxes is: %s" %l)
        config.col_sub
        config.row_sub
        config.col_sub = np.array([])
        config.row_sub = np.array([])
        if l==0:
            config.col_sub = np.array([0])
            config.row_sub = np.array([0])
        else:
            for i in range(size):
                if list[i]==True:
                    config.col_sub=np.append(config.col_sub,i%n)
                    config.row_sub=np.append(config.row_sub,\
                    ((i-config.col_sub[config.col_sub.size-1])/n))
        return config.col_sub, config.row_sub

    def MoveWafer(self):
        #defines what "Move Probe!" button does
        if self.RB_anyrow.isChecked():
            #print("anyrow")
            self.check()
            self.execute(wrapper, wrapper.send_signal)
            #self.probestation.read()
            #print("col is: %s" % config.col_sub)
            #print("row is: %s" % config.row_sub)
            #r = self.spinBox_anyrow.value()
            #wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.read_any_row, r)
            #self.execute(wrapper, func)

        elif self.RB_rowrange.isChecked():
            print("rowrange")
            ix = self.spinBox_rowrange.value()
            iy = self.spinBox_rowrange.value()
            wrapper = InitChuckProcess(self.probestation)
            func = partial(wrapper.read_row_range, ix, iy)
            self.execute(wrapper, func)
        elif self.RB_fullwafer.isChecked():
            print("fullwafer")
            wrapper = InitChuckProcess(self.probestation)
            self.execute(wrapper, wrapper.read_full_wafer)
        elif self.manual.isChecked():
            print("Manual Control: Click the directional buttons to move probe")
        else:
            print("Defined")
            wrapper = InitChuckProcess(self.probestation)
            self.execute(wrapper, wrapper.read_defined)

    def manual_control(self):
        sender = self.sender()
        if sender.text()=='up':
            print("Move up")
           # wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, 0, 1)
            #self.execute(wrapper, wrapper.func)

        elif sender.text()=='down':
            print("Move down")
            wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, 0, -1)
            self.execute(wrapper, wrapper.send_signal)

        elif sender.text()=='L':
            print("Move left")
            #wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, -1, 0)
            #self.execute(wrapper, wrapper.func)

        elif sender.text()=='L':
            print("Move right")
            #wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, -1, 0)
            #self.execute(wrapper, wrapper.func)


        elif sender.text()=='C':
            print("Move Contact")
            #wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, -1, 0)
            #self.execute(wrapper, wrapper.func)

        elif sender.text()=='S':
            print("Move separation")
            #wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, -1, 0)
            #self.execute(wrapper, wrapper.func)

        elif sender.text()=='Di':
            print("Index set to Dice")
            #wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, -1, 0)
            #self.execute(wrapper, wrapper.func)

        else:
            print("Index set to Subdice")
            #wrapper = InitChuckProcess(self.probestation)
            #func = partial(wrapper.move_chuck_index, 1, 0)
            #self.execute(wrapper, wrapper.func)

    def applyToOne(self, *args):
        devs = [[CB.word, CB.bit]]
        wrapper = Process(devs, self.gather_data())
        self.execute(wrapper, wrapper.run) #what does this function do?
        
    def applyToRange(self, *args):
        devs = makeDeviceList(True)
        
        print(devs)
        
    def applyToAll(self, *args):
        devs = makeDeviceList(False)
        print(devs)

    def eventFilter(self, object, event):
        if event.type()==QtCore.QEvent.Resize:
            self.vW.setFixedWidth(event.size().width() - \
                object.verticalScrollBar().width())
        return False

    def disableProgPanel(self,state):
        self.hboxProg.setEnabled(not state)


tags = { 'top': modutils.ModTag("TMM", "TestModule", None) }
