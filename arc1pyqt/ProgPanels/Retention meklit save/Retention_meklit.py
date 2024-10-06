####################################

# (c) Radu Berdan
# ArC Instruments Ltd.

# This code is licensed under GNU v3 license (see LICENSE.txt for details)

#This code acts as a separate form finder that electroform the devices with a reinforcement learning algorithm


#Meklit forming algorithm

####################################

#Meklit imports
import json
import argparse
import logging
import random
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

# other imports
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import time
import numpy as np
import pyqtgraph as pg
from csv import DictWriter
from numpy import asarray

from numpy import savetxt

from arc1pyqt import Graphics
from arc1pyqt import state
HW = state.hardware
APP = state.app
CB = state.crossbar
from arc1pyqt.Globals import styles, fonts
from arc1pyqt.modutils import BaseThreadWrapper, BaseProgPanel, \
        makeDeviceList, ModTag
        
        
#forming input variables
STATES = ["I", "II", "III", "FAIL"]
MAX_VOLTAGE=12
STEP_VOLTAGES=20
MIN_VOLTAGE=-12
MAX_cycles=5
NUM_STATES = len(STATES)
NUM_NON_FAIL_STATES = NUM_STATES-1
PULSE_WIDTH=0.0001
CLASS_MATRIX=["class0.csv", "class1.csv","class2.csv", "class3.csv", "class4.csv" ,"class5.csv", "class6.csv", "class7.csv", "class8.csv"]
CLASS_NUMBER=1
BIT_LINE=15
DEVICE_STATE=0
GAMMA=0.99
REPORT=[]
number_devices=1
#automation variables
rdf=1
tag = "RT"
manual_signal=0

#clear the csv file each time you load the program
f = open("C:/Users/s2440888/OneDrive - University of Edinburgh/Desktop/arc1_pyqt/Log_Data/data_mff_manual.csv", "w")
f.truncate()
f.close()
f = open("C:/Users/s2440888/OneDrive - University of Edinburgh/Desktop/arc1_pyqt/Log_Data/data_mff_%s.csv" % rdf, "w")
f.truncate()
f.close()

print('Loading retention')

#the wrtapper that runs the actual characterization algorithm on the board
#here you can make various functions that can be called in run()
class ThreadWrapper(BaseThreadWrapper):

    def __init__(self, deviceList, Vread):
        super().__init__()
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES, MAX_cycles,GAMMA
        self.deviceList=deviceList
        #self.every=every
        #self.duration=duration
        self.Vread=Vread   #current voltage read
        
        self.read_resistance=0  #the actual read resistance in ohms
        self.current_state=0    #the resistance state that falls in the specified category: e.g. 0: 100k-1M ohms    
        self.voltage=MAX_VOLTAGE
        self.pw= PULSE_WIDTH
        self.max_attempts=int(MAX_cycles)
        self.GAMMA= GAMMA
        
        #runs the algorithm that performs the voltage calculus
        self.arc_tester = EpsilonGreedyCautious(self.max_attempts, self.GAMMA)

    #function that runs the characterization algorithm specific to any module
    @BaseThreadWrapper.runner
    def run(self):
        global BIT_LINE, CLASS_NUMBER, DEVICE_STATE
        #first line of global variables are useful for the automation and taging the correct function
        #the second line of global variables are the actual input given to this forming module
        global manual_signal, tag, rdf #,mff_index
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES, STATES, REPORT,number_devices
        
        self.arc_tester.reset(0)
        #this manual_signal does not have great relevance here, however, it is important in the automation module
        #so you can just keep it as it is
        if manual_signal==0:
            file_name='C:/Users/s2440888/OneDrive - University of Edinburgh/Desktop/arc1_pyqt/Log_Data/data_mff_%s.csv'%rdf
        else:
            file_name='C:/Users/s2440888/OneDrive - University of Edinburgh/Desktop/arc1_pyqt/Log_Data/data_mff_manual.csv'

        #open the csv file that will store the applied puses
        field_names=['Measurement', 'D', 'S', 'W', 'B','Class', 'Res','State', 'V', 'Time', 'success','failed','tested_devices','step_time']
        f_object = open(file_name, 'a', newline='')
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)
        
        #this function deactivates the software interface while the characterization is in progress
        self.disableInterface.emit(True)
        
        report = []
        time_record=[]

        #Initial read
        #takes the selected word line and bit line from the map selector
        #keep track of the current device (appears on the die map)
        for device in self.deviceList:
            w=device[0]
            b=device[1]
            print('Device', w, b)
            self.highlight.emit(w,b)
            BIT_LINE=b

            if BIT_LINE in [15,16,17,18]:
                CLASS_NUMBER=1
            elif BIT_LINE in [13,14,19,20]:
                CLASS_NUMBER=2
            elif BIT_LINE in [11,12, 21,22]:
                CLASS_NUMBER=3
            elif BIT_LINE in [9,10, 23,24]:
                CLASS_NUMBER=4
            elif BIT_LINE in [7,8, 25, 26]:
                CLASS_NUMBER=5
            elif BIT_LINE in [5,6,27, 28]:
                CLASS_NUMBER=6
            elif BIT_LINE in [3,4, 29, 0]:
                CLASS_NUMBER=7
            elif BIT_LINE in [1,2, 31, 32]:
                CLASS_NUMBER=8
                
        

       # _transition_record= np.array(np.zeros([3,4,20]))

            n=0 #time step
            # get current state of device from the hardware
            #the resistance recorded on device is put into self.read_resistance                
            self.read_pulse(1, w, b, dictwriter_object)
            
            #this function allocates an integer value to self.current_state that corresponding to a specific resistance range
            self.resistance_class(self.read_resistance)
            #takes the current state in a local variable
            current_state=self.current_state
            DEVICE_STATE=current_state
            # select the state we want this to be, random but could be read from file
            # and don't choose the current state          
            possible_target_states = set(range(NUM_NON_FAIL_STATES))
            possible_target_states.remove(current_state)
            #print(possible_target_states)
            if current_state==0:
                target_state=1
            else:
                target_state = 2
            
            
            # determine the voltage to apply for the number of max_attempts
            for i in range(self.max_attempts):
                n+=1
                action=self.arc_tester.get_action(current_state, target_state)
                if i >=0.9*self.max_attempts:
                    self.voltage =action['voltage']
                else:
                    self.voltage =action['voltage']
                self.pw = action['pulse_duration']                   
                
                #write a pulse consisting of a voltage and pulse width (pw)
                #the pulse is recorded in a csv file (dictwriter_object)
                self.write_pulse(1, w, b, self.voltage, self.pw, dictwriter_object)
                
                #read a new resistance of the device
                #convert it again to resistance states
                #put that value into a local one 'new_state'
                
                self.read_pulse(1, w, b, dictwriter_object)
                self.resistance_class(self.read_resistance)
                new_state = self.current_state
                
                #update the table
                #if the new state reached the target change, the algorithm stops
                self.arc_tester.update(current_state,target_state,action,new_state)
                if new_state ==target_state or STATES[new_state]=="FAIL":
                    break
                 
                current_state=new_state
            number_devices+=1   
            time_record=n    
            action_index =  int((self.voltage+5)/0.5)
            
           # _transition_record[self.read_resistance][_new_state][_action_index-1]+=1
            report.append(
                {
                    'current_state': STATES[current_state],
                    'target_state': STATES[target_state],
                    'actual_state': STATES[new_state],
                    #'voltage_pulse': self.pw,
                    'time_step':time_record,
                    'success': target_state == new_state
                }
            )
       
                # check to see if we have finished the wafer #no need for another break as this is done out of your code
                #if not hardware.move_to_next_device():
                    #break
                    
            self.arc_tester.q_table()
            
  
            #return report
            print("Report is: %s" %report )
            REPORT= report

        
        #close the csv file
        f_object.close()
     
        
    #read resistance at Vread for n cycles at position w, b
    #saves the data in a csv file
    @BaseThreadWrapper.runner
    def read_pulse(self, cycles, w, b, dictwriter_object):
    
        global tag, DEVICE_STATE, REPORT,number_devices
        
        for i in range(int(cycles)):
            self.read_resistance = HW.ArC.read_one(w, b)
            tag_ = tag+"_s"
            self.sendData.emit(w,b,self.read_resistance,self.Vread,0,tag_)
            self.displayData.emit()
            self.success=sum([d['success'] for d in REPORT])
            self.failed = sum([d['actual_state']=="FAIL" for d in REPORT])
            if number_devices==1:
                self.step_time=0
            else:
                self.step_time=sum([d['time_step'] for d in REPORT])/(number_devices-1)
            data_mff = {'Measurement': "MFF_read", 'D': state.Application.Dice_no, \
                                   'S': state.Application.Subdice_no, \
                                   'W': w, 'B': b,'Class':CLASS_NUMBER, 'Res': self.read_resistance,\
                                   'State' :DEVICE_STATE, 'V': self.Vread, \
                                    'Time': str(time.time()),'success': self.success,'failed':self.failed,\
                                    'tested_devices':number_devices,'step_time':self.step_time }
            dictwriter_object.writerow(data_mff)
           
            
    
    #write a pulse at position w,b for a number of cycles and output the resistance at each pulse
    #saves the data in a csv file
    @BaseThreadWrapper.runner
    def write_pulse(self, cycles, w, b, v, pw, dictwriter_object):
        global tag,DEVICE_STATE,REPORT,number_devices
        #v=2
        #pw=0.0003
        
        #run a few 'cycles' of pulses
        for i in range(int(cycles)):
        
            tag="Pulse"
            
            #acquire the actual resistance from the board
            self.read_resistance=HW.ArC.pulseread_one(w, b, v, pw)
            tag_ = tag
            self.success=sum([d['success'] for d in REPORT])
            self.failed = sum([d['actual_state']=="FAIL" for d in REPORT])
            if number_devices==1:
                self.step_time=0
            else:
                self.step_time=sum([d['time_step'] for d in REPORT])/(number_devices-1)
            #data handing in the board
            self.sendData.emit(w,b,self.read_resistance,v,pw,tag_)
            self.displayData.emit()
            
            #external data storage in the board, including die, subdie positions
            data_mff = {'Measurement': "MFF_write", 'D': state.Application.Dice_no, \
                                   'S': state.Application.Subdice_no, \
                                   'W': w, 'B': b,'Class':CLASS_NUMBER, 'Res': self.read_resistance,\
                                   'State' :DEVICE_STATE, 'V': self.voltage, \
                                    'Time': str(time.time()),'success': self.success,'failed':self.failed,\
                                    'tested_devices':number_devices,'step_time':self.step_time }
            dictwriter_object.writerow(data_mff)
            

    #this function outputs the specific current_state predefined value when the resistance reaches a specific range
    def resistance_class(self, resistance):
        if resistance>100000 and resistance<100000000000: #revert back to <1M now 10^11
            self.current_state=0
        elif resistance>10000 and resistance<100000:
            self.current_state=1
        elif resistance>3000 and resistance<10000:
            self.current_state=2
        else:
            self.current_state=3
            
    #split the die devices into classes with similar electrode series resistance
    #useful for when the electrode series resistance affects the characterization
    #if not used, please use the interface pannel selector 
    def device_classes(self):
        pass

#class that creates the graphical interface of the module
#the module is named 'retention' as this was a template module that was recoded
#you don't really need to look into this one unless you want to add some new input boxes
class Retention(BaseProgPanel):

    def __init__(self, short=False):
        super().__init__(\
                title='FormFinder EpsilonGreedyCautious', \
                description='Find the right forming voltage '
                            'for the maximum limits given below', \
                short=short)
        self.initUI()

    #define the pyqt graphical objects
    def initUI(self):

        vbox1=QtWidgets.QVBoxLayout()

        titleLabel = QtWidgets.QLabel(self.title)
        titleLabel.setFont(fonts.font1)
        descriptionLabel = QtWidgets.QLabel(self.description)
        descriptionLabel.setFont(fonts.font3)
        descriptionLabel.setWordWrap(True)

        isInt=QtGui.QIntValidator()
        isFloat=QtGui.QDoubleValidator()

        leftLabels=['Max voltage:', \
                    'Max cycles:',\
                    'Step voltage:',\
                    'Pulse width:',\
                    'Gamma:']
        leftInit=  ['12',\
                    '20',\
                    '120',\
                    '0.0001',\
                    '0.999']

        self.leftEdits=[]
        rightLabels=[]

        gridLayout=QtWidgets.QGridLayout()
        gridLayout.setColumnStretch(0,3)
        gridLayout.setColumnStretch(1,1)
        gridLayout.setColumnStretch(2,1)
        gridLayout.setColumnStretch(3,1)
        gridLayout.setColumnStretch(4,3)
        gridLayout.setColumnStretch(5,1)
        gridLayout.setColumnStretch(6,1)
        if self.short==False:
            gridLayout.setColumnStretch(7,2)

        lineLeft=QtWidgets.QFrame()
        lineLeft.setFrameShape(QtWidgets.QFrame.VLine)
        lineLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        lineLeft.setLineWidth(1)

        gridLayout.addWidget(lineLeft, 0, 2, 2, 1)


        for i in range(len(leftLabels)):
            lineLabel=QtWidgets.QLabel()
            #lineLabel.setFixedHeight(50)
            lineLabel.setText(leftLabels[i])
            gridLayout.addWidget(lineLabel, i,0)

            lineEdit=QtWidgets.QLineEdit()
            lineEdit.setText(leftInit[i])
            lineEdit.setValidator(isFloat)
            self.leftEdits.append(lineEdit)

        # self.leftEdits[0].setProperty("key", "duration")
        # self.leftEdits[1].setProperty("key", "interval")
        self.registerPropertyWidget(self.leftEdits[0], "duration")
        self.registerPropertyWidget(self.leftEdits[1], "interval")
        self.registerPropertyWidget(self.leftEdits[2], "interval")
        self.registerPropertyWidget(self.leftEdits[3], "duration")
        self.registerPropertyWidget(self.leftEdits[4], "duration")

        # ========== ComboBox ===========
        every_lay=QtWidgets.QHBoxLayout()
        duration_lay=QtWidgets.QHBoxLayout()

        self.every_dropDown=QtWidgets.QComboBox()
        self.every_dropDown.setStyleSheet(styles.comboStylePulse)

        self.unitsFull=[['s',1],['min',60],['hrs',3600]]
        self.units=[e[0] for e in self.unitsFull]
        self.multiply=[e[1] for e in self.unitsFull]

        self.duration_dropDown=QtWidgets.QComboBox()
        self.duration_dropDown.setStyleSheet(styles.comboStylePulse)

        self.every_dropDown.insertItems(1,self.units)
        self.every_dropDown.setCurrentIndex(0)
        # self.every_dropDown.setProperty("key", "interval_multiplier")
        self.registerPropertyWidget(self.every_dropDown, "interval_multiplier")
        self.duration_dropDown.insertItems(1,self.units)
        self.duration_dropDown.setCurrentIndex(1)
        # self.duration_dropDown.setProperty("key", "duration_multiplier")
        self.registerPropertyWidget(self.duration_dropDown, "duration_multiplier")

        gridLayout.addWidget(self.leftEdits[0],0,1)
        #gridLayout.addWidget(self.every_dropDown,0,3)
        gridLayout.addWidget(self.leftEdits[1],1,1)
        #gridLayout.addWidget(self.duration_dropDown,1,3)
        gridLayout.addWidget(self.leftEdits[2],2,1)
        #gridLayout.addWidget(self.duration_dropDown,2,3)
        gridLayout.addWidget(self.leftEdits[3],3,1)
        #gridLayout.addWidget(self.duration_dropDown,3,3)
        gridLayout.addWidget(self.leftEdits[4],4,1)
        #gridLayout.addWidget(self.duration_dropDown,4,3)
        

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

            push_single = self.makeControlButton('Apply to One', \
                    self.programOne)
            push_range = self.makeControlButton('Apply to Range', \
                    self.programRange)
            push_all = self.makeControlButton('Apply to All', \
                    self.programAll)

            self.hboxProg.addWidget(push_single)
            self.hboxProg.addWidget(push_range)
            self.hboxProg.addWidget(push_all)

            vbox1.addLayout(self.hboxProg)

        self.setLayout(vbox1)
        self.gridLayout=gridLayout

    def eventFilter(self, object, event):
        if event.type()==QtCore.QEvent.Resize:
            self.vW.setFixedWidth(event.size().width()-object.verticalScrollBar().width())
        return False

    def disableProgPanel(self,state):
        if state==True:
            self.hboxProg.setEnabled(False)
        else:
            self.hboxProg.setEnabled(True)
    
    #loads variables from the module graphical interface
    #in these variables are not actually used as they belong to the original retention module
    def programDevs(self, devs):
        global MAX_VOLTAGE, MAX_cycles, STEP_VOLTAGES, PULSE_WIDTH,GAMMA
        
        MAX_VOLTAGE=float(self.leftEdits[0].text())
        MAX_cycles=float(self.leftEdits[1].text())
        STEP_VOLTAGES=float(self.leftEdits[2].text())
        PULSE_WIDTH=float(self.leftEdits[3].text())
        GAMMA=float(self.leftEdits[4].text())
        
        

        wrapper = ThreadWrapper(devs, HW.conf.Vread)
        self.execute(wrapper, wrapper.run)

    #apply the characterization to only one device
    def programOne(self):
        self.programDevs([[CB.word, CB.bit]])
    
    #apply the characterization to a range of devices
    def programRange(self):
        rangeDev = makeDeviceList(True)
        self.programDevs(rangeDev)
    
    #apply the characterization to all devices in the die
    def programAll(self):
        rangeDev = makeDeviceList(False)
        self.programDevs(rangeDev)

    #function that displays the measurement results in the arc interface
    @staticmethod
    def display(w, b, data, parent=None):
        timePoints = []
        m = []

        for point in data:
            tag = str(point[3])
            tagCut = tag[4:]
            try:
                timePoint = float(tagCut)
                timePoints.append(timePoint)
                m.append(point[0])
            except ValueError:
                pass

        # subtract the first point from all timepoints
        firstPoint = timePoints[0]
        for i in range(len(timePoints)):
            timePoints[i] = timePoints[i] - firstPoint

        view = pg.GraphicsLayoutWidget()
        label_style = {'color': '#000000', 'font-size': '10pt'}

        retentionPlot = view.addPlot()
        retentionCurve = retentionPlot.plot(symbolPen=None,
                symbolBrush=(0,0,255), symbol='s', symbolSize=5, pxMode=True)
        retentionPlot.getAxis('left').setLabel('Resistance', units='Ω', **label_style)
        retentionPlot.getAxis('bottom').setLabel('Time', units='s', **label_style)
        retentionPlot.getAxis('left').setGrid(50)
        retentionPlot.getAxis('bottom').setGrid(50)

        resLayout = QtWidgets.QVBoxLayout()
        resLayout.addWidget(view)
        resLayout.setContentsMargins(0, 0, 0, 0)
        statsLayout = QtWidgets.QHBoxLayout()
        statsLayout.setContentsMargins(6, 3, 6, 6)
        statsLayout.addWidget(
            QtWidgets.QLabel('Total readings: %d - Average: %s - Std. Deviation: %s' % (
                len(m),
                pg.siFormat(np.average(np.asarray(m)), suffix='Ω'),
                pg.siFormat(np.std(np.asarray(m)), suffix='Ω'))))
        resLayout.addItem(statsLayout)

        resultWindow = QtWidgets.QWidget()
        resultWindow.setGeometry(100,100,int(1000*APP.scalingFactor), 400)
        resultWindow.setWindowTitle("Retention: W="+ str(w) + " | B=" + str(b))
        resultWindow.setWindowIcon(Graphics.getIcon('appicon'))
        resultWindow.show()
        resultWindow.setLayout(resLayout)

        retentionPlot.setYRange(min(m)/1.5, max(m)*1.5)
        retentionCurve.setData(np.asarray(timePoints),np.asarray(m))
        resultWindow.update()

        return resultWindow



#the 'voltage finder' algorithm
class EpsilonGreedyCautious():
    """Update of EpsilonGreedy with a bit more caution made 
    by starting from lower voltages first and then progressing to higher 
    voltages as we explore
    """
    def __init__(self, max_attempts:int, gamma:float):
        super().__init__()
        
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES,CLASS_NUMBER
        self.range_subtractor=5 # used to modifiy the range of voltages to select from 
        self._voltage_inc=(MAX_VOLTAGE - MIN_VOLTAGE)/STEP_VOLTAGES #float voltage increment (0.5)
        self._voltage_step= int(STEP_VOLTAGES)+1 # total number of actions(20)
        self._voltages= [MIN_VOLTAGE+i*self._voltage_inc for i in range(int(self._voltage_step))] #actual value of volatges
       #self._expected_reward_table = np.zeros((NUM_NON_FAIL_STATES,
        #                                        NUM_NON_FAIL_STATES,
         #                                       self._voltage_step))
        
        
        self.loaded_array = np.loadtxt(CLASS_MATRIX[CLASS_NUMBER])

        self._expected_reward_table = np.reshape(self.loaded_array, ((NUM_NON_FAIL_STATES,NUM_NON_FAIL_STATES,
                                                self._voltage_step)))
        # Open the JSON file and load its contents
        with open('Epsilon.json', 'r') as f:
            self.data = json.load(f) 

        self._epsilon = self.data[CLASS_MATRIX[CLASS_NUMBER]]
        self._gamma= gamma
        self._exploitation = 0
        self._exploration = 0
        self._action_value_est= 0
        
    def get_action(self, current_state, target_state) -> dict:
        
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE
        
        _actions= self._voltages
        #for i in range(args.max_attempts):
             
        p = np.random.random()
        if p < self._epsilon+0.2:
            self._exploration += 1
            if current_state == 0:
                _voltage_index = random.randrange(15+1+(self._voltage_step-1)/2,self._voltage_step-self.range_subtractor)
            elif current_state == 1 and target_state ==0:
                _voltage_index= random.randrange(0+self.range_subtractor,-15-1+(self._voltage_step-1)/2)
            elif current_state == 1 and target_state ==2:
                _voltage_index= random.randrange(15+1+(self._voltage_step-1)/2,self._voltage_step-self.range_subtractor)
            elif current_state == 2:
                _voltage_index= random.randrange(0+self.range_subtractor,-15-1+(self._voltage_step-1)/2)
            _voltage=self._voltages[_voltage_index] 
        else:
            self._exploitation+= 1
            _voltage_index = np.argmax([a for a in self._expected_reward_table[current_state][target_state]])
            _voltage=self._voltages[_voltage_index]       
        
        return {'voltage': _voltage,
                'pulse_duration':1,
                'voltage_index':_voltage_index
        }     
        
    def update(self, old_state:int, target_state:int, action:dict, new_state:int ):
        """update the expected reward table
        add 1 to self_exploration every time we explore(take single action)
        """
        
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES
        
       # _index= int(action['voltage']/self._voltage_inc)
        _index= action['voltage_index']
        if new_state==target_state :
            self._expected_reward_table[old_state][target_state][_index]+=20
        elif new_state==3 :#fail
            self._expected_reward_table[old_state][target_state][_index]+=-30
        else:
            self._expected_reward_table[old_state][target_state][_index]+=1
        
        #favour exploitation a little bit more   
        self._epsilon *= self._gamma
        if  self._epsilon < 0.8 and self._epsilon > 0.6:
            self.range_subtractor=5
        elif  self._epsilon < 0.6 and self._epsilon > 0.4:
            self.range_subtractor=2
        elif  self._epsilon < 0.4:
            self.range_subtractor=0
    def q_table(self):
        
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES
        
        Q=self._expected_reward_table
        np.savetxt(CLASS_MATRIX[CLASS_NUMBER], Q.flatten(), delimiter=',')
        # Modify the contents of the JSON object
        self.data[CLASS_MATRIX[CLASS_NUMBER]] =  self._epsilon

        # Write the updated JSON object back to the file
        with open('Epsilon.json', 'w') as f:
            json.dump(self.data,f)
        _mean_voltage=np.zeros((NUM_NON_FAIL_STATES,NUM_NON_FAIL_STATES))
        for i in range(NUM_NON_FAIL_STATES):
            for j in range(NUM_NON_FAIL_STATES):
                _mean_v_index = np.argmax([a for a in Q[i][j]])
                _mean_voltage[i,j]=self._voltages[_mean_v_index]
                if i==j:
                    _mean_voltage[i,j]=0        
        print('Number of exploration=', self._exploration) 
        print('Number of exploitation=', self._exploitation) 
        print('Final epsilon=', self._epsilon)
        print(Q)
        print('class=',CLASS_NUMBER)
        print(_mean_voltage)
    def reset(self,class_number):
        a=np.zeros((NUM_NON_FAIL_STATES, NUM_NON_FAIL_STATES,self._voltage_step))
        if class_number==0:
            for i in range(8):
                self.data[CLASS_MATRIX[i+1]] =  1
                # Write the updated JSON object back to the file
                with open('Epsilon.json', 'w') as f:
                    json.dump(self.data,f)
            for filename in CLASS_MATRIX:
                np.savetxt(filename, a.flatten(), delimiter=',')
        else:
            np.savetxt(CLASS_MATRIX[class_number], a.flatten(), delimiter=',')
            
        
    

        

#defining the global and local tags of the module
tags = { 'top': ModTag(tag, "Retention", Retention.display) }
