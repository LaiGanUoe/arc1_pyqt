from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import numpy as np
import pandas as pd
import json
import re
import imp
import pkgutil
import time
from functools import partial
import pyqtgraph as pg
sys.path.append('C:\\Users\\s2440888\\OneDrive - University of Edinburgh\\Desktop\\arc1_pyqt')
import config
import itertools

from probelibrary import ProbeStation
from controller import make_controller
from controller import CNTRL_TYPE

from PyQt5.QtWidgets import *
from PyQt5.QtGui import*
from PyQt5.QtCore import*

from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTime, QTimer, QModelIndex

import arc1pyqt.Globals.fonts as fonts
import arc1pyqt.Globals.styles as styles
from arc1pyqt.Globals import functions

from arc1pyqt import Graphics
from arc1pyqt import state
import csv
from csv import DictWriter

HW = state.hardware
APP = state.app
CB = state.crossbar

from arc1pyqt import modutils
from arc1pyqt.modutils import BaseThreadWrapper, BaseProgPanel, \
        makeDeviceList, ModTag

THIS_DIR = os.path.dirname(__file__)
tag = "TMM"

#set current directory path of the project
arcpyqt = os.getcwd()

#Navigate to the other_folder from parent_folder
Log_Data = os.path.abspath(os.path.join(arcpyqt, "Log_Data"))

#position correction
Positing_Error = os.path.abspath(os.path.join(arcpyqt, "Positioning Error"))


heading="Measurement,Die, Subdie, Word, Bit, Resistance (Ohms),\
# Read Voltage (V), PW (ms), Time (s)"
heading_signal="Yes/No, Dice, Subdice, W,B, Rate, Vnew, Rnew, Vold, Rold, Time (s)"

#clear the files containing the manual measurement data
f = open(os.path.join(Log_Data, "manual_data.csv"), "w")
f.truncate()
f.close()


ss_index=0 #keeps track of the experiment number for switch seeker
ff_index=0 # same for all below for their corresponding functions
ct_index=0
cts_index=0
rt_index=0
pf_index=0
rilf_index=0
no_errors=0

process_finished=0 #outputs 1 when the experiment finished
rdf=1 #used to increment the experiment number for the csv files

Dx_local=0
sx_local=0
manual_signal=0 #when 1, it writes in the designed manual csv fine, when 0 it writes in the automation csv files
pf_signal=0 #when there is a switch seeker before parameter fit it sets to 1

map_show=0 #when 1 it outputs the wafer map
goto_dies_val=0 
goto_subdies_val=0


#inputs for RIL Forming module
import json
import argparse
import logging
import random
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from numpy import asarray
from numpy import savetxt
STATES = ["I", "II", "III", "FAIL"]
NUM_STATES = len(STATES)
NUM_NON_FAIL_STATES = NUM_STATES-1
PULSE_WIDTH=0.0001
CLASS_MATRIX=["class0.csv", "class1.csv","class2.csv", "class3.csv", "class4.csv" ,"class5.csv", "class6.csv", "class7.csv", "class8.csv"]
CLASS_NUMBER=1
BIT_LINE=15
DEVICE_STATE=0
REPORT=[]
number_devices=1
MAX_VOLTAGE=state.Application.RILForming1
MIN_VOLTAGE=-state.Application.RILForming1
MAX_cycles=int(state.Application.RILForming2)
STEP_VOLTAGES=state.Application.RILForming3
PULSE_WIDTH=state.Application.RILForming4
GAMMA=state.Application.RILForming5


def _log(*args, **kwargs):
    if bool(os.environ.get('TMMDBG', False)):
        print(*args, file=sys.stderr, **kwargs)

class InitChuckProcess(BaseThreadWrapper):

    def __init__(self, probe, deviceList, rps, every, duration, Vread):
        super().__init__()
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES, MAX_cycles, GAMMA
        self.probestation = probe
        self.deviceList=deviceList
        self.rps = rps
        self.every=every
        self.duration=duration
        self.Vread=Vread
        self.load_prev_reference()#set condition for csvreader>0
        self.DBG = False

        #RILForming variables
        self.read_resistance=0  #the actual read resistance in ohms for RILForming only
        self.current_state=0    #the resistance state that falls in the specified category: e.g. 0: 100k-1M ohms for RILForming 
        self.voltage=MAX_VOLTAGE
        self.pw= PULSE_WIDTH
        self.max_attempts=MAX_cycles
        self.GAMMA= GAMMA
        
        #runs the algorithm that performs the voltage calculus
        self.arc_tester = EpsilonGreedyCautious(self.max_attempts, self.GAMMA)
        
        #self.pop = waferMap("wafer map", self)

    sendData = QtCore.pyqtSignal(int, int, float, float, float, str, float)

#Thread
#select the reading protocol according to the order in the fct combo boxes
    @BaseThreadWrapper.runner
    def read_protocol(self):
        ban=0 #calculate estimate time at the first occurence, then ban=1
        start=0#start local time
        end=0#end local time
       
        global reading, pf_signal, no_errors, manual_signal
        self.find_index_position()
        list_var = ['Retention', 'Form Finder', 'Switch Seeker', 'Converge', 'CurveTracer', 'ParameterFit', 'RILForming', 'Uniformity']
        start=time.time()
        
        exec("self.run_readall()")#run a readall to display the resistance values before the function chain
        
        for k in range(state.Application.repeat_chain):
            works=1 #check if a function has worked or not
            for i in range(len(self.rps)):
                for j in range(len(list_var)):
                    if self.rps[i] == list_var[j]:
                        rps_split = self.rps[i].split(' ')                   
                        fct_name = ("self.run_%s()" % rps_split[0])
                        if self.rps[i]=="Switch Seeker" and self.rps[i+1]=="ParameterFit":
                            pf_signal=1
                        time.sleep(0.1)
                        #else:
                            #pf_signal=0
                        #print("pf signal is: %s" %pf_signal)
                        #print("rps is: %s" %self.rps)
                        #print("rps i is: %s" % self.rps[i])
                        #print("rps i+1 is: %s" %self.rps[i+1])
                        #print(fct_name)
                        
                        #try:
                        
                        exec(fct_name)                            
                        #except:
                            #print("Function Error")
                            #no_errors=no_errors+1
                            #works=0 #do not calculate estimate time
                        #else:         
                            #print("Function Worked!")
            
            if ban==0 and works==1:
                end=time.time()
                state.Application.time_est=(end-start)*state.Application.repeat_chain*config.col_sub.size*config.col.size
                if manual_signal==0:
                    state.Application.time_est=state.Application.time_est-(time.time()-state.Application.time_start)
                    print("Time Estimate Remaining: %.2f s" %state.Application.time_est)
                ban=1

#find threshold voltage for switch seeker
#takes the difference in voltage between an initial voltage read and all the next individual voltage reads
#when the difference exceeds a defined target ratio, it saves that first voltage found and then stops the search
#and it does to the next device and repeats the search                   
    @BaseThreadWrapper.runner
    def find_rate_ss(self):
        global rdf, ss_index

        if "Switch Seeker" in self.rps:
            indice=0
            rows=np.array([])
            field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']
            print("1")
            with open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), 'r') as file:
                csvreader=list(csv.reader(file, delimiter=","))
            csvreader=np.array(csvreader)
            size_csv=csvreader.shape
            size_csv=size_csv[0]
            print("size_csv=%s" %size_csv)
            print(csvreader[0])
            target=int(size_csv/(ss_index*len(self.deviceList)))
            print("2")
            with open(os.path.join(Log_Data, "signal_ss_%s.csv" % rdf), 'a', newline='') as f_object:
                print("3")
                for k in range(size_csv - 1):
                    if k % target == 0:
                        local_init = csvreader[k][5]
                        if float(local_init)==0 and k>=size_csv:
                            local_init=csvreader[k-target][5]
                        indice = 0

                    rate = abs((float(csvreader[k][5]) - float(csvreader[k+1][5])) / float(local_init))*100

                    if rate > config.rate:
                        if indice == 0:
                            data = {'Measurement': csvreader[k][0], 'D': csvreader[k][1], 'S': csvreader[k][2], \
                                    'W': csvreader[k][3], 'B': csvreader[k][4], 'Res': csvreader[k][5], 'V': csvreader[k][6], \
                                    'PW': csvreader[k][7], 'Time': csvreader[k][8], 'Rate':rate}
                            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                            dictwriter_object.writerow(data)
                            indice = 1
                ss_index = 0
                print("6")

#find voltage threshold for form finder functions
#similarly to the switch seeker voltage finder, this function saves the voltage pulse exceeding a
#a defined ratio and then it stops until and goes to the next device
    @BaseThreadWrapper.runner
    def find_rate_ff(self):

        global rdf, ff_index

        if "Form Finder" in self.rps:
            indice=0
            print(time.time())
            rows=np.array([])
            field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']
            print("1")
            
            with open(os.path.join(Log_Data, "automation_%s_T%s.csv"%(rdf, state.Application.time_start)), 'r') as file:
                csvreader=list(csv.reader(file, delimiter=","))
                
            csvreader=np.array(csvreader)
            size_csv=csvreader.shape
            size_csv=size_csv[0]
            print(csvreader[0])
            target = int(size_csv / (ff_index * len(self.deviceList)))
 
            with open(os.path.join(Log_Data, "signal_ff_%s.csv" % rdf), 'a', newline='') as f_object:
                print("3")
                for k in range(size_csv - 1):
                    if k % target == 0:
                        local_init = csvreader[k][5]
                        if float(local_init) == 0 and k >= size_csv:
                            local_init=csvreader[k-target][5]
                        indice = 0

                    rate = abs((float(csvreader[k][5]) - float(csvreader[k+1][5])) / float(local_init))*100

                    if rate > config.rate:
                        if indice == 0:
                            data = {'Measurement': csvreader[k][0], 'D': csvreader[k][1], 'S': csvreader[k][2], \
                                    'W': csvreader[k][3], 'B': csvreader[k][4], 'Res': csvreader[k][5], 'V': csvreader[k][6], \
                                    'PW': csvreader[k][7], 'Time': csvreader[k][8], 'Rate':rate}
                            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                            dictwriter_object.writerow(data)
                            indice = 1
                ff_index = 0

#find input voltage from ss to input into parameter finder automatically
    @BaseThreadWrapper.runner
    def find_voltage_pf(self):
        global pass_pf_data, pass_pf_data2, pass_pf_data_neg, pass_pf_data2_neg
        res_index=5
        Vread = 0.5
        switch = 0
        signal = 0
        local_init = 0.001
        rate = 0
        suma = 0
        idx = 0
        ban = 0
        back = int(state.Application.switch_seek1)+1  # size of the read pulses (or slightly larger up to programming pulses)
        indice = 1
        indice2=1
        indice_neg = 1
        indice2_neg = 1
        z=0
        rate_target=config.rate
        rate_target2=config.rate2 #please decide on that and on the available range
        pass_pf_data=np.array([]) #this data is passed to the formfit as Vmin after SS
        pass_pf_data2 = np.array([]) #this data is passed to the formfit as Vmax after SS
        pass_pf_data_neg = np.array([])  # this data is passed to the formfit as -Vmin after SS
        pass_pf_data2_neg = np.array([])  # this data is passed to the formfit as -Vmax after SS
        rows = np.array([])
        
        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']

        with open(os.path.join(arcpyqt,"data_ss_pf.csv"), 'r') as file:
            csvreader = list(csv.reader(file, delimiter=","))
            
        csvreader = np.array(csvreader)
        size_csv = csvreader.shape
        size_csv = size_csv[0]
        print("size_csv=%s" % size_csv)

        for k in range(size_csv):

            if float(csvreader[k][5]) < 0.1 and signal == 0:
                res_index = 6
                switch = -3
                signal = 1
                print("Inversed at: %s" % csvreader[k])
###################################identifies 00's######################################################
            if float(csvreader[k][res_index + 2 + switch]) == 0\
                and float(csvreader[k][res_index + 1]) == 0:

                suma = suma + float(csvreader[k][res_index])
                idx = idx + 1
                ban = 0
###################################calculates average 00s R and sets indices# for later#################
            elif float(csvreader[k][res_index + 2 + switch]) != 0\
                    and float(csvreader[k][res_index + 1]) != 0\
                    and ban == 0:

                local_init = suma / idx
                idx = 0
                suma = 0
                indice = 0
                indice2=0
                indice_neg = 0
                indice2_neg = 0
                ban = 1
                position=0
###################################calculates the rate at the current pos###############################
            if float(csvreader[k][res_index + 1]) != 0:
                rate = (abs(local_init - float(csvreader[k][res_index])) / local_init) * 100

############################################find voltages +/- max##########2nd##########################
            # if the rate is reached, we are in the reading pulses, the previous corresponding
             # pulses are +ve, and we are at the first occurence after finding the Vmin, save data.
            if rate>rate_target2 and float(csvreader[k][res_index + 1])==Vread and\
            float(csvreader[k][res_index + 2 + switch])==0:
                if indice2 == 0 and indice ==1 and float(csvreader[k-back][res_index + 1])>0:

                    pass_pf_data2 = np.append(pass_pf_data2, float(csvreader[k - back][res_index + 1]))
                    print("rate2 is: %s" % rate)
                    print("pf data2 is %s" %pass_pf_data2)
                    indice2 = 1

            # if the rate is reached, we are in the reading pulses, the previous corresponding
             # pulses are +ve, and we are at the first occurence after finding the Vmin, save data.
            if rate > rate_target2 and float(csvreader[k][res_index + 1])==Vread and\
            float(csvreader[k][res_index + 2 + switch])==0:
                if indice2_neg == 0 and indice_neg ==1 and float(csvreader[k-back][res_index + 1])<0:

                    pass_pf_data2_neg = np.append(pass_pf_data2_neg, float(csvreader[k - back][res_index + 1]))
                    print("rate2- is: %s" %rate)
                    print("pf data2 neg is %s" %pass_pf_data2_neg)
                    indice2_neg = 1

########################################################################################################
############################################find voltage +/- min##########1st###########################
           #if the rate is reached, we are in the reading pulses, the previous corresponding
            #pulses are +ve, and we are at the first occurence, save data.

            if rate > rate_target and float(csvreader[k][res_index + 1])==Vread and\
            float(csvreader[k][res_index + 2 + switch])==0:
                if indice == 0 and float(csvreader[k-back][res_index + 1])>0:

                    pass_pf_data = np.append(pass_pf_data, float(csvreader[k - back][res_index + 1]))
                    print("rate1 is: %s" %rate)
                    print("pf data is %s" %pass_pf_data)
                    indice = 1


            # if the rate is reached, we are in the reading pulses, the previous corresponding
             # pulses are -ve, and we are at the first occurence, save data.

            if rate > rate_target and float(csvreader[k][res_index + 1])==Vread and\
            float(csvreader[k][res_index + 2 + switch])==0:
                if indice_neg == 0 and float(csvreader[k-back][res_index + 1])<0:

                    pass_pf_data_neg = np.append(pass_pf_data_neg, float(csvreader[k - back][res_index + 1]))
                    print("rate1- is: %s" %rate)
                    print("pf data neg is %s" %pass_pf_data_neg)
                    indice_neg = 1
#####################################add a '0' if threshold was not reached##############################
            #if the threshold is not reached at the end of all data add 0
            if indice==0:
                if k+1==int(size_csv):
                    pass_pf_data = np.append(pass_pf_data, 0)
                    print("compensated pf data is %s" % pass_pf_data)
                #if the threshold is not reached after each device add 0

                elif k+1<int(size_csv) and (float(csvreader[k+1][res_index + 2 + switch]) == 0\
                and float(csvreader[k+1][res_index + 1]) == 0\
                and float(csvreader[k-1][res_index + 1]) == Vread):

                    pass_pf_data = np.append(pass_pf_data, 0)
                    print("compensated pf data is %s" % pass_pf_data)
                    indice=1

            #same for +Vmax
            if indice2==0:
                if k+1==int(size_csv):
                    pass_pf_data2 = np.append(pass_pf_data2, 0)
                    print("compensated pf data is %s" % pass_pf_data2)

                elif k+1<int(size_csv) and (float(csvreader[k+1][res_index + 2 + switch]) == 0\
                and float(csvreader[k+1][res_index + 1]) == 0\
                and float(csvreader[k-1][res_index + 1]) == Vread):

                    pass_pf_data2 = np.append(pass_pf_data2, 0)
                    print("compensated pf data is %s" % pass_pf_data2)
                    indice2=1

            # same for -Vmin
            if indice_neg==0:
                if k+1==int(size_csv):
                    pass_pf_data_neg = np.append(pass_pf_data_neg, 0)
                    print("compensated pf data is %s" % pass_pf_data_neg)

                elif k+1<int(size_csv) and (float(csvreader[k+1][res_index + 2 + switch]) == 0\
                and float(csvreader[k+1][res_index + 1]) == 0\
                and float(csvreader[k-1][res_index + 1]) == Vread):

                    pass_pf_data_neg = np.append(pass_pf_data_neg, 0)
                    print("compensated pf data is %s" % pass_pf_data_neg)
                    indice_neg=1

            # same for -Vmax
            if indice2_neg==0:
                if k+1==int(size_csv):
                    pass_pf_data2_neg = np.append(pass_pf_data2_neg, 0)
                    print("compensated pf data is %s" % pass_pf_data)

                elif k+1<int(size_csv) and (float(csvreader[k+1][res_index + 2 + switch]) == 0\
                and float(csvreader[k+1][res_index + 1]) == 0\
                and float(csvreader[k-1][res_index + 1]) == Vread):

                    pass_pf_data2_neg = np.append(pass_pf_data2_neg, 0)
                    print("compensated pf data is %s" % pass_pf_data2_neg)
                    indice2_neg=1

        print("k is: %s" %k)
        print("Indice: %s" %indice)
        print("fin compensated pf data is %s" % pass_pf_data)
        print("fin compensated pf data neg is %s" % pass_pf_data_neg)
        print("fin compensated pf data2 is %s" % pass_pf_data2)
        print("fin compensated pf data2 neg is %s" % pass_pf_data2_neg)
########################################################################################################
############################################if any Vmax are 0s########################################
        for z in range(pass_pf_data2.size):
            # daca Vmin e gasit si e ok, dar Vmax e cat Vmin sau 0(compensat)
            #folosim Vmax din SS
            if pass_pf_data[z]!=0 and (pass_pf_data2[z]==pass_pf_data[z] or pass_pf_data2[z]==0):
                pass_pf_data2=np.delete(pass_pf_data2, [z])
                print("+Vmax deleted: %s" %pass_pf_data2)
                pass_pf_data2=np.insert(pass_pf_data2, z, state.Application.switch_seek6)
                print("+Vmax recreated: %s" % pass_pf_data2)

            #la fel se intampla si pentru partea negativa din SS
        for z in range(pass_pf_data2_neg.size):
            if pass_pf_data_neg[z] != 0 and (pass_pf_data2_neg[z] == pass_pf_data_neg[z] or pass_pf_data2_neg[z] == 0):
                pass_pf_data2_neg = np.delete(pass_pf_data2_neg, [z])
                print("-Vmax deleted: %s" % pass_pf_data2_neg)
                pass_pf_data2_neg = np.insert(pass_pf_data2_neg, z, -float(state.Application.switch_seek6))
                print("-Vmax recreated: %s" % pass_pf_data2_neg)



    @BaseThreadWrapper.runner
    def run_RILForming(self):
        global BIT_LINE, CLASS_NUMBER, DEVICE_STATE
        global manual_signal, tag, rdf ,rilf_index
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES, STATES, REPORT,number_devices
        
        self.arc_tester.reset(0)
        #this manual_signal does not have great relevance here, however, it is important in the automation module
        #so you can just keep it as it is
        if manual_signal==0:
            file_name=os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, state.Application.time_start))
        else:
            file_name=os.path.join(Log_Data, "manual_data.csv")

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
            print("1")
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
            print("read delay")
            print(time.time())
            self.read_pulse(1, w, b, dictwriter_object)
            print(time.time())
            
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
            
            print("2")
            # determine the voltage to apply for the number of max_attempts
            for i in range(self.max_attempts):
                print("2.5")
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
                #self.read_pulse(1, w, b, dictwriter_object)
                self.resistance_class(self.read_resistance)
                new_state = self.current_state
                print("5")
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
     
    
    #comensate for series resistance     
    def uniform_reading(self, w, b, Vin, compensate_Vm):
        
        #extract function values from module panel
        Rs_bottom = state.Application.Rs_bottom
        Rs_top = state.Application.Rs_top
        subdie = state.Application.Subdice_no
        
        #extract the correct L and W ratios accoring to the w/b lines
        L_ratio = config.L_ratios[w-1]
        W_ratio = config.W_ratios[subdie-1]
        
        
        #print("Length %s has ratio: %s"%(w, L_ratio))
        #print("Width %s has ratio: %s"%(subdie, W_ratio))
        
        ##########find correct memristor Rm and Vm #########
        
        R_tot = HW.ArC.read_one(w, b)
        #print(R_tot)
        
        #Save current Vread in Vd
        Vd=Vin
        
        #extract I total circuit
        I_tot = Vd / R_tot
        
        #compute Memristor resistance by length, width and initial Rs
        Rm = R_tot - (Rs_bottom*L_ratio*W_ratio)- (Rs_top*L_ratio*W_ratio)
        
        #Voltage drop across memristor
        Vm = I_tot * Rm
        
        
        print("Rm calibrated is: %s" %Rm)
        #print("Rs is : %s" %((Rs_bottom*L_ratio*W_ratio)+ (Rs_top*L_ratio*W_ratio)))
        #print("R tot is: %s" %R_tot)
        #print("I tot is: %s" %I_tot) 
        
        ##########find correction Vadjust to be equal with Vd###########
        
        #adjust Itot to have Vm drop at memeristor the quantity we want
        #here I can try a polynomial fit instead to reduce error
        I_adjust = Vd / Rm
        #print("I adjust is: %s" %I_adjust)
        
        #adjust input voltage to provide Vd across memristor
        V_adjust = I_adjust * R_tot
        #print("Vadjust is: %s" %V_adjust) 
        
        #if the checkbox is ticked, the Vm is adjusted to reach Vd
        if compensate_Vm == 1:
        
            #take V_adjust as the new reading voltage
            self.Vread=V_adjust     
            #apply reading again with the calibrated voltage
            R_tot_new = HW.ArC.read_one(w, b)
            #restore Vread to its original value
            self.Vread = Vd
            
            #print("Rtot new: %s" %R_tot_new)
            
            #find Itot_new of the adjusted Voltage
            I_tot_new = V_adjust / R_tot_new
            print("I tot new is: %s" %I_tot_new) 
            
            
            #find the corrected memristor resistance without Rs for the new voltage
            Rm_new = R_tot - (Rs_bottom*L_ratio*W_ratio)- (Rs_top*L_ratio*W_ratio)
            
            #print("Rm new is: %s" %Rm_new) 
            
            #find corrected memristor drop voltage Vm
            Vm_new = I_tot_new * Rm_new
            
            #print("Vm_new is: %s" %Vm_new) 
            
            #if Vm_new is not equal to Vd as intended, perform an improved calculus
            #either by error subtraction or polynomial fit
            #print("Vm new is: %s" %Vm_new)
            #print("Rm compensated is: %s" %Rm_new)
            
            if (R_tot_new and Vm_new) is not None:
                Vm = Vm_new
                Rm = Rm_new
        
        print("Vm is: %s" %Vm)
        return float(Rm), float(Vm)
    
    
    #read resistance at Vread for n cycles at position w, b
    #saves the data in a csv file
    @BaseThreadWrapper.runner
    def read_pulse(self, cycles, w, b, dictwriter_object):
    
        global tag, DEVICE_STATE, REPORT, number_devices
        
        #for i in range(int(cycles)):
        #self.highlight.emit(w,b)
        self.read_resistance = HW.ArC.read_one(w, b)
        tag_ = tag+"_s"
        #self.sendData.emit(w,b,self.read_resistance,self.Vread,0,tag_, 0)
        #self.displayData.emit()
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
        #for i in range(int(cycles)):
        
        tag="Retention"
        time.sleep(0.1)
        #acquire the actual resistance from the board
        HW.ArC.pulse_one(w, b, v, pw)
        self.read_resistance=HW.ArC.read_one(w, b)
        time.sleep(0.1)
        
        tag_ = tag
        self.success=sum([d['success'] for d in REPORT])
        self.failed = sum([d['actual_state']=="FAIL" for d in REPORT])
        if number_devices==1:
            self.step_time=0
        else:
            self.step_time=sum([d['time_step'] for d in REPORT])/(number_devices-1)
        
        #data handing in the board
        self.sendData.emit(w,b,self.read_resistance,v,pw,tag_,0)
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


    @BaseThreadWrapper.runner
    def run_ParameterFit(self):
        global tag, pf_signal, manual_signal, pass_pf_data, pass_pf_data2, pass_pf_data_neg, pass_pf_data2_neg, rdf


        #voltages = []
        k=0

        if manual_signal == 0:
            file_name = os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, state.Application.time_start))
        else:
            file_name = os.path.join(Log_Data, "manual_data.csv")

        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']

        f_object = open(file_name, 'a', newline='')
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)

        print("pf signal is: %s" % pf_signal)
        if pf_signal == 0:
            vpos = np.arange(state.Application.parameterfit1, \
                             state.Application.parameterfit3, \
                             state.Application.parameterfit2)
            vneg = np.arange(state.Application.parameterfit7, \
                             state.Application.parameterfit9, \
                             state.Application.parameterfit8)

        midTag = "%s6_i" % tag

        DBG = bool(os.environ.get('PFDBG', False))

        for device in self.deviceList:
            voltages = []
            w = device[0]
            b = device[1]
            self.highlight.emit(w, b)


            #if there is a Switch Seeker before, extract the voltages and use them no matter what input is fed into PF
            #if no Vmin is found, the PF is skiped for those devices.
            #if there is Vmin but no Vmax found, it will use the Vmax from the Switch Seeker input
            if pf_signal== 1:
                
                print("pfdata 1: %s" %pass_pf_data)
                print("pfdata 1: %s" %pass_pf_data2)
                
                pf_step=(float(pass_pf_data2[k])-float(pass_pf_data[k]))/10
                pf_step_neg=(float(pass_pf_data2_neg[k])-float(pass_pf_data_neg[k]))/10

                #print("vpos step is: %s" % pf_step)
                #print("vneg step is: %s" % pf_step_neg)

                if abs(pf_step)<0.0001 or abs(pf_step_neg)<0.0001:
                    pf_step=1
                    pf_step_neg=1 # this will skip the device

                vpos = np.arange(float(pass_pf_data[k]), \
                                 float(pass_pf_data2[k]), \
                                 pf_step)
                vneg = np.arange(float(pass_pf_data_neg[k]), \
                                 float(pass_pf_data2_neg[k]), \
                                 pf_step_neg)

            #print("vpos is: %s" % vpos)
            #print("vneg is: %s" % vneg)

            numVoltages = min(len(vpos), len(vneg))
            print("numVoltages: %s" % numVoltages)
            for i in range(numVoltages):
                voltages.append(vpos[i])
                voltages.append(vneg[i])

            print("voltajele sunt: %s" %voltages)

            for (i, voltage) in enumerate(voltages):

                if i == 0:
                    startTag = "%s6_s" % tag
                else:
                    startTag = "%s6_i" % tag
                    print(startTag)

                if i == (len(voltages) - 1):
                    endTag = "%s6_e" % tag
                else:
                    endTag = "%s6_i" % tag

                self.run_FormFit(w, b, voltage, state.Application.parameterfit5,\
                        state.Application.parameterfit6, state.Application.parameterfit4,\
                        startTag, midTag, endTag, dictwriter_object)
                
                if state.Application.parameterfit10!=0:
                    self.run_FormFit(w, b, 0.2, 0.0000001, state.Application.parameterfit6, state.Application.parameterfit10, startTag, midTag, endTag, dictwriter_object)\
                        #HW.conf.Vread
                
            k=k+1

            self.updateTree.emit(w, b)
        pf_signal = 0
        f_object.close()

    # form finder Parameter fit; it provides a series of 'nrPulses' at a specific voltage 'V'
    #it can provide either a series of positive or negative pulses per function call
    @BaseThreadWrapper.runner
    def run_FormFit(self, w, b, V, pw, interpulse, nrPulses, startTag, midTag,\
                    endTag, dictwriter):

        #time.sleep(0.1)

        HW.ArC.write_b(str(14) + "\n")  # job number, form finder

        HW.ArC.write_b(str(V) + "\n")  # Vmin == Vmax
        if V > 0:
            HW.ArC.write_b(str(0.1) + "\n")  # no step, single voltage
        else:
            HW.ArC.write_b(str(-0.1) + "\n")

        HW.ArC.write_b(str(V) + "\n")  # Vmax == Vmin
        time.sleep(0.05)
        HW.ArC.write_b(str(pw) + "\n")  # pw_min == pw_max
        HW.ArC.write_b(str(100.0) + "\n")  # no pulse step
        HW.ArC.write_b(str(pw) + "\n")  # pw_max == pw_min
        HW.ArC.write_b(str(interpulse) + "\n")  # interpulse time
        time.sleep(0.05)
        # HW.ArC.write_b(str(nrPulses) + "\n") # number of pulses
        HW.ArC.write_b(str(10.0) + "\n")  # 10 Ohms R threshold (ie no threshold)
        HW.ArC.write_b(str(0.0) + "\n")  # 0% R threshold (ie no threshold)
        HW.ArC.write_b(str(7) + "\n")  # 7 -> no series resistance
        HW.ArC.write_b(str(nrPulses) + "\n")  # number of pulses
        time.sleep(0.05)
        HW.ArC.write_b(str(1) + "\n")  # single device always
        time.sleep(0.05)
        HW.ArC.queue_select(w, b)

        end = False

        # data = []
        buffer = []
        aTag = ""

        while (not end):

            curValues = list(HW.ArC.read_floats(3))

            if (curValues[2] < 99e-9) and (curValues[0] > 0.0):
                continue

            #if curValues[0]==

            if curValues[0] == 0 and curValues[1] == 0 and curValues[2] == 0:
                end = True
                aTag = endTag

            if (not end):
                if len(buffer) == 0:  # first point!
                    buffer = np.zeros(3)
                    buffer[0] = curValues[0]
                    buffer[1] = curValues[1]
                    buffer[2] = curValues[2]
                    aTag = startTag
                    continue

                #check here to see if the 0s are skipped
                #aso check to see where it includes the start readings
                data_pf = {'Measurement': "FF", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                           'W': w, 'B': b, 'Res': str(curValues[0]), 'V': str(curValues[1]), \
                           'PW': str(curValues[2]), 'Time': str(time.time())}
                dictwriter.writerow(data_pf)

            # flush buffer values
            self.sendData.emit(w, b, buffer[0], buffer[1], buffer[2], aTag, 0)
            buffer[0] = curValues[0]
            buffer[1] = curValues[1]
            buffer[2] = curValues[2]
            aTag = midTag
            self.displayData.emit()

        #self.reading_Resistancefit(state.Application.parameterfit10, w, b, dictwriter)

    @BaseThreadWrapper.runner     
    def reading_Resistancefit(self, cycles, w, b, dictwriter):#extracts several resistance readings from the board
                                                  #in the same parameterFit external csv log file
                                                  #at the end of each formfit run                                                                      
        global tag
        
        for i in range(int(cycles)):
            
            #Mnow = HW.ArC.read_one(w, b)
            #Mnow = HW.ArC.pulseread_one(w, b, 0.25, 0.000001)
            #Mnow = HW.ArC.read_floats(3)
            time.sleep(0.01)
            tag_ = tag+"_s"
            self.sendData.emit(w,b, Mnow[0],self.Vread,0,tag_, 0)
            self.displayData.emit()
            
            data_pf = {'Measurement': "MFF_read", 'D': state.Application.Dice_no, \
                                   'S': state.Application.Subdice_no, \
                                   'W': w, 'B': b, 'Res': Mnow, 'V': self.Vread, \
                                   'PW': 0, 'Time': str(time.time())}
            dictwriter.writerow(data_pf)
    
#curve tracer
    @BaseThreadWrapper.runner
    def run_CurveTracer(self):
        global tag, ct_index, manual_signal
        repeat=0

        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']

        if manual_signal==0:
            file_name=os.path.join(Log_Data, "automation_%s_T%s.csv"%(rdf, state.Application.time_start))

        else:
            file_name=os.path.join(Log_Data, "manual_data.csv")

        f_object = open(file_name, 'a', newline='')
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)
        
        #enable the CT Looping with CB_curvtracer2 True
        #step derives the no of steps for the loop from the CT step(V)
        #calculate the list of voltages in between v min and v max, where vmax is not inc typically

        if state.Application.CB_curvetracer2==True and\
                int(state.Application.curvetracer1)!=int(state.Application.curvetracer2):
                    
            #step=(float(state.Application.curvetracer2)-float(state.Application.curvetracer1))/float(state.Application.curvetracer10)
            positive_list=np.arange(float(state.Application.curvetracer1),float(state.Application.curvetracer2),float(state.Application.curvetracer10))
            negative_list=positive_list
            print(state.Application.curvetracer10)  
        else:
            positive_list=np.array([state.Application.curvetracer1])
            negative_list=np.array([state.Application.curvetracer2])
       
        #loads the curve tracer inputs to the uC       
        
            
        #loads the devices from the selected map
        for device in self.deviceList:
            
            #run the curve tracer n-times as per size of positive_list
            #every time increase the Vmax and Vmin by Vstep
            #stops in the reading after each run is above the resistance threshold
            #defined in the Forming Resistance Threshold box.
            for i in range(positive_list.size):
             
                HW.ArC.write_b(state.Application.job_ct + "\n")
                HW.ArC.write_b(str(float(positive_list[i])) + "\n")
                HW.ArC.write_b(str(float(negative_list[i])) + "\n")
                HW.ArC.write_b(str(float(state.Application.curvetracer4)) + "\n")
                HW.ArC.write_b(str(float(state.Application.curvetracer3)) + "\n")
                HW.ArC.write_b(str((float(state.Application.curvetracer5) - 2) / 1000) + "\n")
                HW.ArC.write_b(str(float(state.Application.curvetracer7) / 1000) + "\n")
                time.sleep(0.01)
                state.Application.CSp = float(state.Application.curvetracer8)
                state.Application.CSn = float(state.Application.curvetracer9)

                if state.Application.CSp == 10.0:
                    state.Application.CSp = 10.1
                if state.Application.CSn == 10.0:
                    state.Application.CSn = 10.1

                HW.ArC.write_b(str(state.Application.CSp / 1000000) + "\n")
                HW.ArC.write_b(str(state.Application.CSn / -1000000) + "\n")

                HW.ArC.write_b(str(int(state.Application.curvetracer6)) + "\n")
                HW.ArC.write_b(str(int(state.Application.curvetracer_combo1)) + "\n")
                HW.ArC.write_b(str(int(state.Application.curvetracer_combo2)) + "\n")
                HW.ArC.write_b(str(int(state.Application.CB_curvetracer1)) + "\n")


                readTag = 'R' + str(HW.conf.readmode) + ' V=' + str(HW.conf.Vread)
                HW.ArC.write_b(str(int(len(self.deviceList))) + "\n")

                print(positive_list)
                print(negative_list)
                
                w = device[0]
                b = device[1]
                self.highlight.emit(w, b)
                HW.ArC.queue_select(w, b)
                firstPoint = 1

                
                #repeats the procedure in case is specified
                for cycle in range(1, state.Application.totalCycles + 1):
                    endCommand = 0
                    valuesNew = HW.ArC.read_floats(3)

                    if (float(valuesNew[0]) != 0 or float(valuesNew[1]) != 0 or float(valuesNew[2]) != 0):
                        if (firstPoint == 1):
                            tag_ = "%s5" % (tag) + "_s"
                            firstPoint = 0
                        else:
                            tag_ = "%s5" % (tag) + '_i_' + str(cycle)
                    else:
                        endCommand = 1

                    while (endCommand == 0):
                        valuesOld = valuesNew
                        valuesNew = HW.ArC.read_floats(3)

                        if (float(valuesNew[0]) != 0 or float(valuesNew[1]) != 0 or float(valuesNew[2]) != 0):
                            data_ct = {'Measurement': "CT", 'D': state.Application.Dice_no, \
                                       'S': state.Application.Subdice_no, \
                                       'W': w, 'B': b, 'Res': str(valuesOld[0]), 'V': str(valuesOld[1]), \
                                       'PW': str(valuesOld[2]), 'Time': str(time.time())}
                            dictwriter_object.writerow(data_ct)

                            self.sendData.emit(w, b, valuesOld[0], valuesOld[1], valuesOld[2], tag_, valuesOld[1])

                            tag_ = "%s5" % (tag) + '_i_' + str(cycle)

                            self.displayData.emit()

                        else:
                            if (cycle == state.Application.totalCycles):
                                tag_ = "%s5" % (tag) + "_e"
                            else:
                                tag_ = "%s5" % (tag) + '_i_' + str(cycle)

                            data_ct = {'Measurement': "CT", 'D': state.Application.Dice_no, \
                                       'S': state.Application.Subdice_no, \
                                       'W': w, 'B': b, 'Res': str(valuesOld[0]), 'V': str(valuesOld[1]), \
                                       'PW': str(valuesOld[2]), 'Time': str(time.time())}
                            dictwriter_object.writerow(data_ct)
                            self.sendData.emit(w, b, valuesOld[0], valuesOld[1], valuesOld[2], tag_, valuesOld[1])

                            self.displayData.emit()

                            endCommand = 1
                            
                    
                    R_limit = HW.ArC.read_one(w, b)
                    print(R_limit)
                    
                    #print(float(state.Application.form_finder9))
                    if R_limit < float(state.Application.form_finder9):
                        break

                
                if R_limit < float(state.Application.form_finder9):
                    print("limita depasita")
                    break
                
                self.updateTree.emit(w, b)
        ct_index = ct_index + 1
        f_object.close()


#converge to state
    @BaseThreadWrapper.runner
    def run_Converge(self):
        global tag, cts_index, manual_signal
        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']

        self.log("Initiating ConvergeToState (job 21)")
        HW.ArC.write_b(str(21) + "\n")  # job number, converge to state
        self.log("Sending ConvergeToState params")
        HW.ArC.write_b("%.3e\n" % state.Application.converge9)
        HW.ArC.write_b("%.3e\n" % state.Application.converge10)
        HW.ArC.write_b("%.3e\n" % state.Application.converge11)
        HW.ArC.write_b("%.3e\n" % state.Application.converge3)
        HW.ArC.write_b("%.3e\n" % state.Application.converge4)
        HW.ArC.write_b("%.3e\n" % state.Application.converge5)
        HW.ArC.write_b("%.3e\n" % state.Application.converge6)
        HW.ArC.write_b("%.3e\n" % state.Application.converge1)
        HW.ArC.write_b("%.3e\n" % state.Application.converge7)
        HW.ArC.write_b("%.3e\n" % state.Application.converge8)
        HW.ArC.write_b("%d\n" % state.Application.converge12)
        HW.ArC.write_b("%d\n" % state.Application.converge_combo1)
        HW.ArC.write_b(str(len(self.deviceList)) + "\n")

        self.DBG = bool(os.environ.get('CTSDBG', False))

        if manual_signal==0:
            file_name=os.path.join(Log_Data, "automation_%s_T%s.csv"%(rdf, state.Application.time_start))
        else:
            file_name=os.path.join(Log_Data, "manual_data.csv")

        with open(file_name, 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)

            for device in self.deviceList:
                w = device[0]
                b = device[1]
                self.highlight.emit(w, b)

                self.log("Running ConvergeToState on (W=%d, B=%d)" % (w, b))
                HW.ArC.queue_select(w, b)

                # Read the first batch of values

                end = False
                buf = np.zeros(3)
                curValues = list(HW.ArC.read_floats(3))
                self.log(curValues)
                buf[0] = curValues[0]
                buf[1] = curValues[1]
                buf[2] = curValues[2]
                aTag = "%s4" % (tag) + "_s"

                # Repeat while an end tag is not encountered
                while (not end):
                    curValues = list(HW.ArC.read_floats(3))
                    self.log(curValues)

                    if (self.isEndTag(curValues)):
                        self.log("ConvergeToState on (W=%d, B=%d) finishing..." % (w, b))
                        end = True
                        aTag = "%s4" % (tag) + "_e"

                    self.sendData.emit(w, b, buf[0], buf[1], buf[2], aTag, 0)
                    self.displayData.emit()
                    aTag = "%s4" % (tag) + "_i"

                    buf[0] = curValues[0]
                    buf[1] = curValues[1]
                    buf[2] = curValues[2]

                    data_cts = {'Measurement': "CTS", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                               'W': w, 'B': b, 'Res': str(buf[0]), 'V': str(buf[1]), \
                               'PW': str(buf[2]), 'Time': str(time.time())}
                    dictwriter_object.writerow(data_cts)

                self.updateTree.emit(w, b)
            self.log("ConvergeToState on (W=%d, B=%d) finished..." % (w, b))
        self.log("ConvergeToState finished")


        cts_index = cts_index + 1


    def log(self, *args, **kwargs):
        """ Write to stderr if CTSDBG is set"""
        if self.DBG:
            print(*args, file=sys.stderr, **kwargs)

    def isEndTag(self, val):
        """
        Check for three consecutives 0.0, which indicate that the process
        has finished
        """
        try:
            for v in val:
                # this works because there is no way we are having
                # < 1 Ohm resistance; at least one of the values will
                # be <> 0 unless it's a program termination signal
                if int(v) != 0:
                    self.log("end-tag-assess: Found a non-zero val: %f" % v)
                    return False
        except:
            return False
        return True


#form finder
    @BaseThreadWrapper.runner
    def run_Form(self):

        global ff_index, tag

        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']

        state.Application.polarity = 1
        if (state.Application.CB_form_finder1 == 1):
            state.Application.polarity = -1
            
        HW.ArC.write_b(str(state.Application.job_ff) + "\n")  # sends the job
        HW.ArC.write_b(str(float(state.Application.form_finder1) * state.Application.polarity) + "\n")
        HW.ArC.write_b(str(float(state.Application.form_finder2) * state.Application.polarity) + "\n")
        HW.ArC.write_b(str(float(state.Application.form_finder3) * state.Application.polarity) + "\n")
        time.sleep(0.05)
        HW.ArC.write_b(str(float(state.Application.form_finder4) / 1000000) + "\n")
        
        # Determine the step
        if state.Application.job_ff != "14":  # modal formfinder
            if state.Application.pmode == 1:
                # if step is time make it into seconds
                HW.ArC.write_b(str(float(state.Application.form_finder5) / 1000000) + "\n")
            else:
                # else it is percentage, leave it as is
                HW.ArC.write_b(str(float(state.Application.form_finder5)) + "\n")
        else:  # legacy behaviour
            HW.ArC.write_b(str(float(state.Application.form_finder5)) + "\n")

        HW.ArC.write_b(str(float(state.Application.form_finder6) / 1000000) + "\n")
        HW.ArC.write_b(str(float(state.Application.form_finder7) / 1000) + "\n")
        time.sleep(0.05)
        HW.ArC.write_b(str(float(state.Application.form_finder9)) + "\n")
        time.sleep(0.05)

        if state.Application.CB_form_finder2:
            HW.ArC.write_b(str(float(state.Application.form_finder10)) + "\n")
        else:
            HW.ArC.write_b(str(float(0)) + "\n")
            
        time.sleep(0.05)
        
        if state.Application.job_ff != 14:  # newer version of formfinder
            HW.ArC.write_b(str(int(state.Application.pmode)) + "\n")
            
        HW.ArC.write_b(str(int(state.Application.pSR)) + "\n")
        HW.ArC.write_b(str(int(state.Application.form_finder8)) + "\n")
        HW.ArC.write_b(str(int(len(self.deviceList))) + "\n")

        if manual_signal==0:
            file_name=os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, state.Application.time_start))
        else:
            file_name=os.path.join(Log_Data, "manual_data.csv")

        with open(file_name, 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)

            for device in self.deviceList:
                print("aici")
                print(device)
                w = device[0]
                b = device[1]
                self.highlight.emit(w, b)

                HW.ArC.queue_select(w, b)
                firstPoint = 1
                endCommand = 0

                valuesNew = HW.ArC.read_floats(3)

                if (float(valuesNew[0]) != 0 or float(valuesNew[1]) != 0 or float(valuesNew[2]) != 0):
                    tag_ = "%s3_s" % (tag)
                else:
                    endCommand = 1

                while (endCommand == 0):
                    valuesOld = valuesNew
                    valuesNew = HW.ArC.read_floats(3)
                    if (float(valuesNew[0]) != 0 or float(valuesNew[1]) != 0 or float(valuesNew[2]) != 0):
                        self.sendData.emit(w, b, valuesOld[0], valuesOld[1], valuesOld[2], tag_, 0)
                        self.displayData.emit()
                        tag_ = "%s3_i" % (tag)
                    else:
                        tag_ = "%s3_e" % (tag)
                        self.sendData.emit(w, b, valuesOld[0], valuesOld[1], valuesOld[2], tag_, 0)
                        self.displayData.emit()
                        endCommand = 1

                    data_ff = {'Measurement': "FF", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                               'W': w, 'B': b, 'Res': str(valuesOld[0]), 'V': str(valuesOld[1]), \
                               'PW': str(valuesOld[2]), 'Time': str(time.time())}
                    dictwriter_object.writerow(data_ff)

                self.updateTree.emit(w, b)

        ff_index = ff_index + 1

#switch seeker
    @BaseThreadWrapper.runner
    def run_Switch(self):

        global tag, ss_index, rdf, pf_signal
        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']

        start = time.time()

        f = open(os.path.join(arcpyqt ,"data_ss_pf.csv"), "w")
        f.truncate()
        f.close()

        if manual_signal == 0:
            file_name = os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, state.Application.time_start))
        else:
            file_name = os.path.join(Log_Data, "manual_data.csv")

        if pf_signal == 1:
            file_name = os.path.join(Log_Data, "data_ss_pf.csv")

        f_object = open(file_name, 'a', newline='')
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)

        HW.ArC.write_b(state.Application.job_ss + "\n")  # sends the job
        HW.ArC.write_b(str(float(state.Application.switch_seek3) / 1000) + "\n")
        HW.ArC.write_b(str(float(state.Application.switch_seek4)) + "\n")
        HW.ArC.write_b(str(float(state.Application.switch_seek5)) + "\n")
        HW.ArC.write_b(str(float(state.Application.switch_seek6)) + "\n")
        HW.ArC.write_b(str(float(state.Application.switch_seek9) / 1000) + "\n")
        HW.ArC.write_b(str(float(state.Application.switch_seek10)) + "\n")
        time.sleep(0.1)
        HW.ArC.write_b(str(int(state.Application.switch_seek1)) + "\n")
        HW.ArC.write_b(str(int(state.Application.switch_seek2)) + "\n")
        HW.ArC.write_b(str(int(state.Application.switch_seek7)) + "\n")
        HW.ArC.write_b(str(int(state.Application.switch_seek8)) + "\n")
        HW.ArC.write_b(str(int(state.Application.CB_read_after)) + "\n")
        HW.ArC.write_b(state.Application.skipStageI + "\n")

        HW.ArC.write_b(str(int(len(self.deviceList)))+"\n")



        for device in self.deviceList:
            w=device[0]
            b=device[1]
            self.highlight.emit(w,b)
            HW.ArC.queue_select(w, b)
            firstPoint=1
            endCommand=0
            valuesNew=HW.ArC.read_floats(3)
            #valuesInit=valuesNew
            if (float(valuesNew[0])!=0 or float(valuesNew[1])!=0 or float(valuesNew[2])!=0):
                tag_="%s2" % (tag)+'_s'

            else:
                endCommand=1

            while(endCommand==0):

                valuesOld=valuesNew
                valuesNew=HW.ArC.read_floats(3)

                if (float(valuesNew[0])!=0 or float(valuesNew[1])!=0 or float(valuesNew[2])!=0):
                    self.sendData.emit(w,b,valuesOld[0],valuesOld[1],valuesOld[2],tag_, 0)
                    self.displayData.emit()
                    tag_="%s2" % (tag)+'_i'
                else:
                    tag_="%s2" % (tag)+'_e'
                    self.sendData.emit(w,b,valuesOld[0],valuesOld[1],valuesOld[2],tag_, 0)
                    self.displayData.emit()
                    endCommand=1

                #read file
                data_ss = {'Measurement': "SS", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                           'W': w, 'B': b, 'Res': str(valuesOld[0]), 'V': str(valuesOld[1]), \
                           'PW': str(valuesOld[2]), 'Time': str(time.time())}
                dictwriter_object.writerow(data_ss)

            self.updateTree.emit(w,b)
        end = time.time()
        ss_index = ss_index + 1
        f_object.close()
        if pf_signal==1:
            self.find_voltage_pf()

#reading retention
    @BaseThreadWrapper.runner
    def run_Retention(self):

        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'Time', 'Rate']

        self.disableInterface.emit(True)
        global tag, rt_index
        reading_rt=np.array([])
        print("run")
        start=time.time()

        if manual_signal==0:
            file_name=os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, state.Application.time_start))
        else:
            file_name=os.path.join(Log_Data, "manual_data.csv")

        with open(file_name, 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)

            #Initial read
            for device in self.deviceList:
                global reading
                w=device[0]
                b=device[1]
                self.highlight.emit(w,b)

                Mnow = HW.ArC.read_one(w, b)

                tag_ = "%s1" % (tag)+"_s"

                self.sendData.emit(w,b,Mnow,self.Vread,0,tag_, 0)
                self.displayData.emit()

            while True:
                start_op=time.time()

                for device in self.deviceList:
                    w=device[0]
                    b=device[1]
                    self.highlight.emit(w,b)
                    
                    
                    print(time.time())
                    
                    Mnow = HW.ArC.read_one(w, b)
                    
                    #print(time.time())
                    #HW.ArC.pulseread_one(w,b,1,0.001)
                    #print(time.time())
                    
                    
                    tag_="%s1"%(tag)+"_"+str(time.time())
                    self.sendData.emit(w,b,Mnow,self.Vread,0,tag_, 0)
                    self.displayData.emit()

                data_rt = {'Measurement': "RT", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                           'W': w, 'B': b, 'Res': str(Mnow), 'V': str(self.Vread), \
                           'Time': str(time.time())}
                dictwriter_object.writerow(data_rt)

                end=time.time()
                time.sleep(self.every-(end-start_op))
                end=time.time()

                if (end-start)>self.duration:
                    break

            #Final read
            for device in self.deviceList:
                i=0
                w=device[0]
                b=device[1]
                self.highlight.emit(w,b)

                Mnow = HW.ArC.read_one(w, b)
                tag_ = "%s1" % (tag)+"_e"
                print("Tag is: %s" % tag_)

                self.sendData.emit(w,b,Mnow,self.Vread,0,tag_, 0)
                self.displayData.emit()

                self.updateTree.emit(w,b)

        rt_index = rt_index + 1

#reading selected devices for every subdie it goes through during automation
    @BaseThreadWrapper.runner
    def run_readall(self):
        print("readall")
        for device in self.deviceList:
            i=0
            w=device[0]
            b=device[1]
            self.highlight.emit(w,b)
            Mnow = HW.ArC.read_one(w, b)
            tag_ = "%s1" % (tag)+"_e"
              
            self.sendData.emit(w,b,Mnow,self.Vread,0,tag_, 0)
        self.updateTree.emit(w,b)
        
#reading retention
    @BaseThreadWrapper.runner
    def run_Uniformity(self):
        print("uniformity")
        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'Pulsewidth', 'Time', 'Rate']

        self.disableInterface.emit(True)
        global tag, rt_index
        
        Mnow=0
        Mnow_sum=0
        

        if manual_signal==0:
            file_name=os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, state.Application.time_start))
        else:
            file_name=os.path.join(Log_Data, "manual_data.csv")

        with open(file_name, 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)

              
            #Resistance read function         
            for device in self.deviceList:
                global reading
                w=device[0]
                b=device[1]
                self.highlight.emit(w,b)

                #repeat reading pulse for a number of times defined in interface
                for i in range(state.Application.uniformity1):
                    
                    #if compensation checkbox is ticked apply Rs compensation
                    if state.Application.CB_uniformity2==True:
                        Mnow, Vm = self.uniform_reading(w, b, self.Vread, state.Application.CB_uniformity3)
                    
                    elif state.Application.CB_uniformity2==False:
                        Mnow = HW.ArC.read_one(w, b)
                        Vm = self.Vread
                    #Mnow = HW.ArC.read_one(w, b)
                    #print("Vm is: %s" %Vm)
                    
                    Mnow_sum=Mnow+Mnow_sum
                    
                if state.Application.uniformity1!=0:
                    Mnow=Mnow_sum/state.Application.uniformity1
                    
                    Mnow_sum=0
                    
                    tag_ = "%s1" % (tag)+"_s"
                    self.sendData.emit(w,b,Mnow,self.Vread,0,tag_, 0)
                    self.displayData.emit()
                    
                    
                    
                data_u = {'Measurement': "U", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                'W': w, 'B': b, 'Res': str(Mnow), 'V': str(self.Vread), 'Pulsewidth': str(0),\
                'Time': str(time.time())}
                dictwriter_object.writerow(data_u)

            self.updateTree.emit(w,b)

        rt_index = rt_index + 1
        
        #self.display_uniformity()
        
    @BaseThreadWrapper.runner
    def display_uniformity(self):#now it is in the post-processing folder
        print('Display uniformity')
        field_names = ['Measurement', 'D', 'S', 'AverageR', 'DeviationR', 'Deviation%', 'Vread', 'Time']
        
        
        S_sum=0
        count=0
        j=0
        dev=0
        s=0
        
        with open(os.path.join(arcpyqt, "data_ux.csv"), 'r') as file:
            csvreader = list(csv.reader(file, delimiter=","))
            csvreader = np.array(csvreader)
            size_csv = csvreader.shape
            size_csv = size_csv[0]
            print(size_csv)
            
        with open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, state.Application.time_start)), 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            
            for i in range(size_csv):
             
                S_sum=S_sum+float(csvreader[i][5])#sum resistance values
                count=count+1 #number of values up to 32
                
                if i<size_csv-1:

                    if (int(csvreader[i][2])!=int(csvreader[i+1][2])): #if current subdie value is different from next
                        S_sum=S_sum/count
                        
                        for j in range(count):
                            dev=S_sum-float(csvreader[(count*s)+j][5])
                            dev_percent=(dev/S_sum)*100
                            data_u = {'Measurement': "Ulocal", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                            'AverageR': str(S_sum), 'DeviationR': str(dev), 'Deviation%': str(dev_percent), 'Vread': str(self.Vread), \
                            'Time': str(time.time())}
                            dictwriter_object.writerow(data_u)
                        
                        S_sum=0#reset average resistance
                        count=0#reset count for the subarray
                        s=s+1 #increase the count for the subdie
                        
                else:  #this case is for last element to skip as it gives an error due to i+1 out of bonds

                    S_sum=S_sum/count
                        
                    for j in range(count):
                        dev=S_sum-float(csvreader[(count*s)+j][5])
                        dev_percent=(dev/S_sum)*100
                        data_u = {'Measurement': "Ulocal", 'D': state.Application.Dice_no, 'S': state.Application.Subdice_no, \
                        'AverageR': str(S_sum), 'DeviationR': str(dev), 'Deviation%': str(dev_percent), 'Vread': str(self.Vread), \
                        'Time': str(time.time())}
                        dictwriter_object.writerow(data_u)
                        
                    S_sum=0#reset average resistance
                    count=0#reset count for the subarray
                    s=s+1 #increase the count for the subdie

    @BaseThreadWrapper.runner
    def init(self):
        print('Running initialisation')
        self.probestation.initchuck()

    @BaseThreadWrapper.runner
    def move_relative(self, dx, dy):
        self.probestation.move_relative(dx,dy)

    @BaseThreadWrapper.runner
    def set_chuck_heights(self, type, value):
        self.probestation.set_chuck_heights(type, value)

    @BaseThreadWrapper.runner
    def read_chuck_heights(self):
        self.probestation.read_chuck_heights()

    @BaseThreadWrapper.runner
    def check_chuck_contact(self):
        self.probestation.check_chuck_contact()

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
        self.find_index_position()
        #self.lcd_site()
    
    
    @BaseThreadWrapper.runner
    #save and store the reference position for the wafer
    #Die 1 subdie 1 is the default reference
    #if the alignment is done on a different die, please keep it on subdie 1 always,
    #and click the corresponding die on the wafer map before setting the reference
    #if arrows are used to navigate, the reference is saved at the current position
    def set_reference_position(self):
        field_names = ['X','Y']
        f = open(os.path.join(arcpyqt, "Reference.csv"), "w")
        f.truncate()
        f.close()
        f = open(os.path.join(arcpyqt, "Reference.csv"), "a")

        config.Xr, config.Yr, c = self.probestation.position
        print("Xref=%s, Yref=%s" % (config.Xr, config.Yr))
        if any(config.row) and any(config.col):
            print("1")
            print(config.row)
            print(config.col)
            if config.row[0]!=0 or config.col[0]!=0:
                print("2")
                config.Yr=config.Yr-(config.row[0]*config.index_y)
                config.Xr=config.Xr-((config.col[0]-config.w[config.row[0]])*config.index_x) #please double check this
                print("Xrefdie=%s, Yrefdie=%s" % (config.Xr, config.Yr))
        self.find_index_position()
        dictwriter_object = DictWriter(f, fieldnames=field_names)
        XY = {'X': config.Xr, 'Y': config.Yr}
        dictwriter_object.writerow(XY)
        f.close()
        time.sleep(0.1)

    #@BaseThreadWrapper.runner
    #load the previously saved reference position if vacuum was not interrupted
    def load_prev_reference(self):
        with open(os.path.join(arcpyqt, "Reference.csv"),'r') as file:
            csvreader = list(csv.reader(file, delimiter=","))

            for coordinates in csvreader:
                if len(coordinates) > 0:
                    config.Xr=float(coordinates[0])
                    config.Yr=float(coordinates[1])
                    break
                else:
                    print("No reference values found, please Set Ref")
            print("Xref=%s, Yref=%s" % (config.Xr, config.Yr))
            self.find_index_position()
       
    @BaseThreadWrapper.runner
    #move back to the reference position
    def reset_move(self):
        x, y, z = self.probestation.position
        print("Uncorrected reference position x=%s, y=%s" %(x,y))
        x=x-config.Xr
        y=y-config.Yr
        #print("Corrected delta reset by x=%s, y=%s" %(x,y))
        self.move_relative(-x, -y)
        x, y, z = self.probestation.position
        print("Corrected reference position")
        print(x,y,z)
        self.find_index_position()

    @BaseThreadWrapper.runner
    #finds the current position in the given map after setting the reference
    def find_index_position(self):

        sx,sy,sum=(0,0,0)
        x, y, z = self.probestation.position
        x =int(x - config.Xr)
        y =int(y - config.Yr)
        round_x=len(str(config.index_x))-1
        round_y=len(str(config.index_x))-1
        x = round(x, -round_x)
        y = round(y, -round_y)
        #print(x,y)
        #aici bagi conditia de x
        Dx=abs(int(x/config.index_x))
        Dy=abs(int(y/config.index_y))
        Dx_signed=int(x/config.index_x)
        Dy_signed=int(x/config.index_x)
        
        #if 0<abs(x)<config.index_x:
        #    sx=int(abs(x)/config.subindex_x)
        #else:
        #    sx = int((abs(x) % config.index_x) / config.subindex_x)
        #if 0<abs(y)<config.index_y:
        #    sy=int(abs(y)/config.subindex_y)
        #else:
        #    sy = int((abs(y) % config.index_y) / config.subindex_y)
        sy = int((abs(y) % config.index_y) / config.subindex_y)

        if x<=0 and 0<abs(x)<config.index_x:
            sx = int(abs(x) / config.subindex_x)
        elif x<=0 and abs(x)>=config.index_x:
            sx = int((abs(x) % config.index_x) / config.subindex_x)
        elif x>0 and 0<abs(x)<=config.index_x:
            sx = int(abs(x-config.index_x)/ config.subindex_x)
        elif x>0 and abs(x)>config.index_x: #and abs(x)>=config.index_x:
            sx = abs( (int(((x-1)%config.index_x)/ config.subindex_x))-2)
            #print(abs(config.index_x - x + 1))

 

        #print(x,y, sx, sy)

        #if x>0:
        #    sx = int((abs(config.index_x-x-1) % config.index_x) / config.subindex_x)
            
        #if y>0:
        #    sx = int((abs(config.index_y-y-1) % config.index_y) / config.subindex_y)

        if Dy>=len(config.x):
            Dy="-Out"
            Dx="N/A"
        elif (y<0):
            Dy = "+Out"
            Dx = "N/A"
        else:
            if Dx >= config.x[Dy]:
                Dx = "+Out"
            elif (x-(config.w[Dy]*config.index_x))>0:
                Dx = "-Out"
            else:
                if x<=0:
                    Dx = -Dx_signed + config.w[Dy]
                else:
                    Dx = -int((x+6000)/config.index_x) + config.w[Dy]

                for i in range(Dy):
                    sum = sum + config.x[i]
                sum = sum + Dx + 1
                
        subdice=sy*3+sx+1
        print("Here is: D%s:(%s,%s) S%s:(%s,%s)" %(sum,Dx,Dy,subdice,sx,sy))
        state.Application.current_x_D=Dx
        state.Application.current_y_D=Dy
        state.Application.current_x_s=sx
        state.Application.current_y_s=sy
        state.Application.Dice_no=sum
        state.Application.Subdice_no = subdice

        return (Dx, Dy, sx, sy)

    #@BaseThreadWrapper.runner
    #def read_subdice(self):
    #    self.probestation.read_subdice()

    
    @BaseThreadWrapper.runner
    #go to a specific die from config.col and config.row defined in the wafer map
    def goto_die(self):
       
        self.find_index_position() #find current coordinates
        y_rel=config.row-state.Application.current_y_D #find relative y
        x_rel=(config.col-config.w[config.row])-(\
              state.Application.current_x_D-\
               config.w[state.Application.current_y_D])#find relative x
        print("xrel is: %s, %s" %(x_rel, y_rel))
        self.set_chuck_index(config.index_x, config.index_y) #set chuck index to dies
        self.move_chuck_index(float(-x_rel), float(y_rel)) #perform the movement

    #open and clear the saving files for each module
    @BaseThreadWrapper.runner
    def open_files(self):
        global rdf
        
        #f = open(os.path.join(Log_Data, "signal_ss_%s.csv" %rdf), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "signal_ff_%s.csv" %rdf), "w")
        #f.truncate()
        #f.close()
        
        #f = open(os.path.join(arcpyqt, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        #f = open(os.path.join(Log_Data, "automation_%s_T%s.csv" %(rdf, time.time())), "w")
        #f.truncate()
        #f.close()
        f = open(os.path.join(arcpyqt, "data_ux.csv"), "w")
        f.truncate()
        f.close()

    
    #Correct the error of the current die position compared to the reference position
    @BaseThreadWrapper.runner    
    def correct_error_die(self, i):
        global rdf
        self.probestation.check_move_status()
        time.sleep(0.5)
        
        x, y, z = self.probestation.position
        print("Current reference position is: %s %s %s" %(x, y, z))
        
        #real displacement from ref to current position (it contains error)
        x_current=x-config.Xr
        y_current=y-config.Yr
        
        #print("x displacement from ref is: %s; y displacement is: %s" %(x_current, y_current))
        
        
        #ideal displacement from ref to current position
        
        x_ideal=-(config.col[i]-0-config.w[config.row[i]])*config.index_x
        y_ideal=config.row[i]*config.index_x
        
        #print("x ideal displacement is: %s; y ideal displacement is: %s" %(x_ideal, y_ideal))
        
        #error rounded found in between the ideal distance and real one
        x_correction=round((x_ideal-x_current),0)
        y_correction=round((y_ideal-y_current),0)
        
        #error not rounded found in between the ideal distance and real one
        x_correction_noround=x_ideal-x_current
        y_correction_noround=y_ideal-y_current
        
        #corrected position
        print("Corrected round error amount by x=%s, y=%s" %(x_correction,y_correction))
        print("Corrected error amount by x=%s, y=%s" %(x_correction_noround,y_correction_noround))
        
        #more relative to compensate for the error accumulated
        self.move_relative(x_correction, y_correction)
        x_corrected, y_corrected, z_corrected = self.probestation.position
        print("Wafer position corrected. Now is: x=%s, y=%s" %(x_corrected,y_corrected))   
        #self.find_index_position()
        
        
        
        field_names = ['Measurement', 'D', 'Error_x', 'Error_y', 'Time']
        
        #comment out self.move_relative to skip the correction in this case
        with open(os.path.join(Positing_Error, "error_no_correction_%s_T%s.csv"%(rdf, state.Application.time_start)), 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            data_error = {'Measurement': str(rdf), 'D': state.Application.Dice_no,  \
                        'Error_x': str(x_correction), 'Error_y': str(y_correction), 'Time': str(state.Application.time_start)}
            dictwriter_object.writerow(data_error)
        
        with open(os.path.join(Positing_Error, "error_precorrection_%s_T%s.csv" %(rdf, state.Application.time_start)), 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            data_error = {'Measurement': str(rdf), 'D': state.Application.Dice_no,  \
                        'Error_x': str(x_correction), 'Error_y': str(y_correction), 'Time': str(state.Application.time_start)}
            dictwriter_object.writerow(data_error)
            
            
        with open(os.path.join(Positing_Error, "error_postcorrection_%s_T%s.csv" %(rdf, state.Application.time_start)), 'a', newline='') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            data_error = {'Measurement': str(rdf), 'D': state.Application.Dice_no,  \
                        'Error_x': str(x-x_corrected), 'Error_y': str(y-y_corrected), 'Time': str(state.Application.time_start)}
            dictwriter_object.writerow(data_error)
            
        
    
    
    @BaseThreadWrapper.runner
    def read_subdice(self):
        # perform the chuck movement in the given subdie in 
        # given sub_row, sub_col vectors
        print("\nStart subdice scanning/reading")
        self.set_chuck_index(config.subindex_x, config.subindex_y)
        self.move_chuck_index(-config.col_sub[0], config.row_sub[0])

        for i in range(config.col_sub.size):

            config.device_count=config.device_count+1#track current progress
            print("Sub-column is %s, Sub-row is %s" % (config.col_sub[i], \
            config.row_sub[i]))
            
            #correct the current position
            #self.correct_error_subdie(i)
                       
            self.move_contact()
            self.read_protocol()
            self.move_separation()
            if i == (config.col_sub.size - 1):
                self.move_chuck_index(-(-config.col_sub[i]), -config.row_sub[i])
            else:
                self.move_chuck_index(-(config.col_sub[i + 1] - config.col_sub[i]), \
                                      config.row_sub[i + 1] - config.row_sub[i])

        self.set_chuck_index(config.index_x, config.index_y)
        self.read_chuck_index()
        print(" Subdice Finished!\n")
        
    @BaseThreadWrapper.runner
    def read_any_row(self, r):
        # read any preferred single die row in the wafer
        global rdf
        self.open_files()
        time_start=time.time()

        self.reset_move()
        self.set_chuck_index(config.index_x, config.index_y)
        self.read_chuck_index()
        a, b, c = self.probestation.position
        print("wafer position initial")
        print(self.probestation.position)

        self.move_separation()
        self.move_chuck_index(-(-config.w[r]), r)
        for i in range(config.x[r]):

            print("Current die: " + str(i))
            if i==0  and config.odd_check[r]==0 and config.skip_odd==1:
                self.read_subdice()
            if i!=0  and config.odd_check[r]==1 and (i+1)%2==0 and config.skip_odd==1:
                self.read_subdice()
            if i!=0  and config.odd_check[r]==0 and i%2==0 and config.skip_odd==1:
                self.read_subdice()
            if config.skip_odd==0:
                self.read_subdice()
            if i == (config.x[r] - 1):
                self.move_chuck_index(-(-i + config.w[r]), -r)  # move back to (0,0)
            else:
                self.move_chuck_index(-1, 0)
        print("reading Finished\n")
        print("wafer position uncorrected")
        print(self.probestation.position)
        self.reset_move()

        time_process = time_start - time.time()
        print("Automation took: %s s" % abs(time_process))
        #self.find_rate_ss()
        #self.find_rate_ff()
        rdf = rdf + 1

    @BaseThreadWrapper.runner
    def read_row_range(self, ix2, ix1):
        # it is used for reading a range of rows<maximum wafer rows. For that use read all wafer function
        # changed to the inverse move direction than the prototype code
        global rdf
        self.open_files()
        time_start=time.time()

        self.reset_move()
        self.set_chuck_index(config.index_x, config.index_y)

        self.move_chuck_index(-(-config.w[ix1]), ix1)  # move to start position

        for i in range(ix2 - ix1 + 1):
            for j in range(config.x[ix1 + i]):

                print("Current row is: " + str(i + ix1))
                if j == 0 and config.odd_check[i+ix1] == 0 and config.skip_odd==1:
                    self.read_subdice()
                if j != 0 and config.odd_check[i+ix1] == 1 and (j + 1) % 2 == 0 and\
                        config.skip_odd==1:
                    self.read_subdice()
                if j != 0 and config.odd_check[i+ix1] == 0 and j % 2 == 0 and\
                        config.skip_odd==1:
                    self.read_subdice()
                if config.skip_odd == 0:
                    self.read_subdice()
                if j == (config.x[ix1 + i] - 1):
                    self.move_chuck_index(j, 0)
                else:
                    self.move_chuck_index(-1, 0)
            if i == (ix2 - ix1):
                self.move_chuck_index(-config.w[ix2], -ix2)
            else:
                self.move_chuck_index((config.w[ix1 + i + 1] - config.w[ix1 + i]), 1)
            print("\n")
        print("Reading Finished\n")
        print("wafer position uncorrected")
        print(self.probestation.position)
        self.reset_move()
        time_process = time_start - time.time()
        print("Automation took: %s s" % abs(time_process))
        #self.find_rate_ss()
        #self.find_rate_ff()
        rdf = rdf + 1

        @BaseThreadWrapper.runner
        def read_full_wafer(self):
            # read all the wafer dice, but keeps the selection for subdie defined by the coordinates
            # in col_sub, row_sub vectors
            global rdf
            time_start=time.time()
            self.open_files()

            self.reset_move()
            self.set_chuck_index(config.index_x, config.index_y)
            ix1 = 0
            ix2 = x.size - 1
            a, b, c = self.probestation.position  # position correction reference
            self.move_chuck_index(-(-config.w[ix1]), ix1)  # move to start position

            for i in range(ix2 - ix1 + 1):
                for j in range(config.x[ix1 + i]):

                    print("Current row is: " + str(i + ix1))
                    if i == 0 and config.odd_check[i + ix1] == 0 and\
                            config.skip_odd==1:
                        self.read_subdice()
                    if i != 0 and config.odd_check[i + ix1] == 1 and\
                            (j + 1) % 2 == 0 and config.skip_odd==1:
                        self.read_subdice()
                    if i != 0 and config.odd_check[i + ix1] == 0 and\
                            j % 2 == 0 and config.skip_odd==1:
                        self.read_subdice()
                    if config.skip_odd == 0:
                        self.read_subdice()
                    if j == (config.x[ix1 + i] - 1):
                        self.move_chuck_index(j, 0)
                    else:
                        self.move_chuck_index(-1, 0)
                if i == (ix2 - ix1):
                    self.move_chuck_index(-config.w[ix2], -ix2)
                else:
                    self.move_chuck_index((config.w[ix1 + i + 1] - config.w[ix1 + i]), 1)
                print("\n")
            print("Reading Finished\n")
            print("wafer position uncorrected")
            print(self.probestation.position)
            self.reset_move()
            time_process = time_start - time.time()
            print("Automation took: %s s" % abs(time_process))
            #self.find_rate_ss()
            #self.find_rate_ff()
            rdf = rdf + 1

    @BaseThreadWrapper.runner
    def read_defined(self):

        global rdf, process_finished, no_errors
        no_errors=0
        process_finished=0
        self.open_files()
        config.device_count=0
        time_start=time.time()
        state.Application.time_start=int(time.time())

        self.reset_move()
        self.set_chuck_index(config.index_x, config.index_y)
        self.move_chuck_index(-(config.col[0] - config.w[config.row[0]]), config.row[0])

        for i in range(config.row.size):

            #print("Current Row is: " + str(config.row[i]))
            
            #correct the current position
            self.correct_error_die(i)
            
            self.read_subdice()
            if i == config.row.size - 1:
                self.move_chuck_index(-(-config.col[i] + \
                                        config.w[config.row[i]]), -config.row[i])
                time.sleep(config.sleep_time)
            else:
                self.move_chuck_index(-((config.col[i + 1] - config.col[i]) - \
                                        (config.w[config.row[i + 1]] - config.w[config.row[i]])), \
                                      config.row[i + 1] - config.row[i])
        print("Reading Finished\n")
        print("wafer position uncorrected")
        print(self.probestation.position)
        self.reset_move()
        time_process = time_start - time.time()
        print("Automation took: %s s" % abs(time_process))
        #self.find_rate_ss()
        #self.find_rate_ff()
        process_finished=1
        rdf=rdf+1


class Process(BaseThreadWrapper):

    def __init__(self, deviceList, params = {}):
        super().__init__()
        self.deviceList = deviceList
        self.params = params


class TestModule(BaseProgPanel):

    def __init__(self, short=False):
        super().__init__(title="TestModule",
            description="Demo module for ArC1", short=short)   
        self.short = short
        self.lcd_value_old = ""

        self.lcd_value = 'D' + str(state.Application.Dice_no) \
                         + ':(' + str(state.Application.current_x_D) + \
                         ',' + str(state.Application.current_y_D) \
                         + ') S' + str(state.Application.Subdice_no) \
                         + ':(' + str(state.Application.current_x_s) \
                         + ',' + str(state.Application.current_y_s) \
                         + ')'
        self.ban=0

        self.initUI()
        self.pop=waferMap('wafer map', self)


#PushButtons connections
        self.button.clicked.connect(self.reset_move)
        self.doOne.clicked.connect(self.programOne)
        self.doRange.clicked.connect(self.programRange)
        self.doAll.clicked.connect(self.programAll)
        self.move_up.clicked.connect(self.manual_control)
        self.move_down.clicked.connect(self.manual_control)
        self.move_left.clicked.connect(self.manual_control)
        self.move_right.clicked.connect(self.manual_control)
        self.move_separation.clicked.connect(self.manual_control)
        self.move_contact.clicked.connect(self.manual_control)
        self.set_index_dice.clicked.connect(self.manual_control)
        self.set_index_subdice.clicked.connect(self.manual_control)
        self.set_reference.clicked.connect(self.set_ref)
        self.button_map.clicked.connect(self.launch_map_popup)

        self.pop.goto_dies.clicked.connect(self.manual_control)
        self.pop.btn_contact.clicked.connect(self.manual_control)
        self.pop.btn_contact.clicked.connect(self.manual_control)
        self.pop.set_reference.clicked.connect(self.manual_control)
        self.pop.load_reference.clicked.connect(self.manual_control)

        self.load_reference.clicked.connect(self.load_ref)
        self.show_fct1.clicked.connect(self.choose_combo)
        self.show_fct2.clicked.connect(self.choose_combo)
        self.show_fct3.clicked.connect(self.choose_combo)
        self.show_fct4.clicked.connect(self.choose_combo)
        self.show_fct5.clicked.connect(self.choose_combo)
        self.show_fct6.clicked.connect(self.choose_combo)

        self.CB_skip_stage1.clicked.connect(self.skip_stage1)
        self.CB_uniformity2.clicked.connect(self.skip_stage1)
        self.CB_parameterfit1.clicked.connect(self.skip_parameterfit)
        self.form_finder_combo2.currentIndexChanged.connect(self.pulsingModeComboIndexChanged)
        self.curvetracer8.editingFinished.connect(self.imposeLimitsOnCurrentStopP)
        self.curvetracer8.editingFinished.connect(self.imposeLimitsOnCurrentStopN)
        self.curvetracer5.editingFinished.connect(self.imposeLimitsOnStepWidth)
        #self.CB_func1.clicked.connect(self.highlight_position)
        #self.controller=make_controller(CNTRL_TYPE.PROLOGIX,20, ['COM4'])
        self.probestation =  ProbeStation(22, CNTRL_TYPE.PROLOGIX, ['COM4'])
        #self.timer2 = QTimer()
        #self.timer2.timeout.connect(self.highlight_position)
        #self.timer2.start(100)



    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        #push button "Move Probe"
        self.button = QtWidgets.QPushButton('Move back to reference')
        layout.addWidget(self.button)

        exec(open(os.path.join(arcpyqt, "graphics_testmodule.py")).read())
        exec(open(os.path.join(arcpyqt, "switchscript.py")).read())#switch seeker graphics
        exec(open(os.path.join(arcpyqt, "formingscript.py")).read())#form finder graphics
        exec(open(os.path.join(arcpyqt, "convergescript.py")).read())#converge to state graphics
        exec(open(os.path.join(arcpyqt, "retentionscript.py")).read())#retention graphics
        exec(open(os.path.join(arcpyqt, "uniformityscript.py")).read())#uniformity graphics
        exec(open(os.path.join(arcpyqt, "curvetracerscript.py")).read())#curve tracer graphics
        exec(open(os.path.join(arcpyqt, "parameterfitscript.py")).read())  # curve tracer graphics
        exec(open(os.path.join(arcpyqt, "RILFormingscript.py")).read())  # reinforcement learning forming
    exec(open(os.path.join(arcpyqt, "hideunhide.py")).read())#hide/unhide different functions fct


    #Repeat a specific function for a number of times
    def choose_global_param(self):
        config.rate=float(self.fct8.text())
        config.rate2 = float(self.fct9.text())  
        state.Application.repeat_fct=int(self.repeat_fct.text())
        state.Application.repeat_chain=int(self.repeat_chain.text())
        print("repeat fct: %s" %state.Application.repeat_fct)
        print("repeat chain: %s" %state.Application.repeat_chain)

    #choose the die/dies where you want to go to (see function goto_die)
    #this function takes the selected values from the wafer map and converts it into coordinates row and col
    def choose_dice(self, sel):
        sum=0

        config.D=np.array([])
        config.D = config.D.astype(int)
        config.row = np.array([])
        config.col = np.array([])
        config.row = config.row.astype(int)
        config.col = config.col.astype(int)

        config.sel_dies_values = list(itertools.chain.from_iterable(config.sel_dies_values))#extract items from a list of lists
        print("sel_dies_values are: %s" % config.sel_dies_values)

        if sel == 1: # select only first element
            del config.sel_dies_values[1:]
            print("sel1 sel_dies_values at index 0 is: %s" % config.sel_dies_values)

        for i in config.sel_dies_values:
            config.D=np.append(config.D, int(i))

        i=0
        for j in range(config.D.size):
            for i in range(config.x.size):
                sum = sum + config.x[i]
                if sum >= config.D[j]:
                    config.row = np.append(config.row, int(i))
                    config.col = np.append(config.col, int(config.x[i] - (sum - config.D[j]) - 1))
                    sum = 0
                    break
        print(config.row, config.col)

    def functie_test(self):
        print("esti bomba")

    def choose_combo(self):
        sender = self.sender()
        val1=self.fct1_combo.currentText()
        val2=self.fct2_combo.currentText()
        val3=self.fct3_combo.currentText()
        val4=self.fct4_combo.currentText()
        val5=self.fct5_combo.currentText()
        val6 = self.fct6_combo.currentText()
        val7 = self.fct7_combo.currentText()
        buttons=['fct1', 'fct2', 'fct3', 'fct4', 'fct5', 'fct6', 'fct7']
        combo_val=[val1, val2, val3, val4, val5, val6, val7]
        for i in range(len(buttons)):
            if sender.text()==buttons[i]:
                self.hide_unhide(combo_val[i])


    def read_protocol_selection(self):
        list = [self.fct1_combo.currentText(), \
                self.fct2_combo.currentText(), \
                self.fct3_combo.currentText(), \
                self.fct4_combo.currentText(), \
                self.fct5_combo.currentText(), \
                self.fct6_combo.currentText(), \
                self.fct7_combo.currentText()]
        #print(list)
        return list

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

    def check_odd(self):
        if self.skip_odd.isChecked(): #skip odd dice
            config.skip_odd=1
        else:
            config.skip_odd=0
            
            

#defines what "Move Probe!" button does
    def MoveWafer(self, *args):
        self.check()
        self.check_odd()

        every, duration = self.retention_preload()
        rps=self.read_protocol_selection()
        devs = args[0]

        if self.RB_anyrow.isChecked():
            print("anyrow")
            r = self.spinBox_anyrow.value()
            wrapper = InitChuckProcess(self.probestation, devs, rps,\
                                       every, duration, HW.conf.Vread)
            func = partial(wrapper.read_any_row, r)
            self.execute(wrapper, func)

        elif self.RB_rowrange.isChecked():
            print("rowrange")
            iy = self.spinBox_rowrangeto.value()
            ix = self.spinBox_rowrangefrom.value()
            wrapper = InitChuckProcess(self.probestation, devs, rps,\
                                       every, duration, HW.conf.Vread)
            func = partial(wrapper.read_row_range, ix, iy)
            self.execute(wrapper, func)

        elif self.RB_fullwafer.isChecked():
            print("fullwafer")
            wrapper = InitChuckProcess(self.probestation, devs, rps, every, duration, HW.conf.Vread)
            self.execute(wrapper, wrapper.read_full_wafer)

        elif self.manual.isChecked():
            print("Manual Control: Click the directional buttons to move probe")

        else:
            print("Defined")

            wrapper = InitChuckProcess(self.probestation, devs, rps, every, duration, HW.conf.Vread)
            self.execute(wrapper, wrapper.read_defined)

    def manual_control(self):
        self.check()
        sender = self.sender()
        global goto_dies_val, goto_subdies_val

        self.row_old = []
        self.row_old = []

        move_unit = self.spinBox_movestep.value()

        if sender.text()=='up' and self.manual.isChecked():
            print("Move up")

            self.pop.highlight_area(1)
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, 0, -move_unit)
            self.execute(wrapper, func)

        elif sender.text()=='down' and self.manual.isChecked():
            print("Move down")

            self.pop.highlight_area(1)
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, 0, move_unit)
            self.execute(wrapper, func)

        elif sender.text()=='L' and self.manual.isChecked():
            print("Move left")

            self.pop.highlight_area(1)
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, move_unit, 0)
            self.execute(wrapper, func)

        elif sender.text()=='R' and self.manual.isChecked():
            print("Move right")
            print("config limit right %s"%config.move_limit)

            self.pop.highlight_area(1)
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, -move_unit, 0)
            self.execute(wrapper, func)

        elif sender.text()=='C' and self.manual.isChecked():
            print("Move Contact")
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            self.execute(wrapper, wrapper.move_contact)

        elif sender.text()=='S' and self.manual.isChecked():
            print("Move separation")
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            self.execute(wrapper, wrapper.move_separation)
            #time.sleep(3)
            #self.execute(wrapper, wrapper.move_contact)

        elif sender.text()=='Di' and self.manual.isChecked():
            print("Index set to Dice")
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.set_chuck_index, config.index_x, config.index_y)
            self.execute(wrapper, func)

        elif sender.text()=='di' and self.manual.isChecked():
            print("Index set to Subdice")
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.set_chuck_index, config.subindex_x, config.subindex_y)
            self.execute(wrapper, func)

        elif self.pop.sender_pop == 'Go ' and self.manual.isChecked()==0:
            self.pop.highlight_area(1)#original map color
            config.sel_dies_values=[]
            config.sel_dies_values.append(self.pop.selection_temp)
            self.choose_dice(0)
            self.pop.selection_released()#use refresh() if you want to clear selection too
            self.pop.selection_temp=[]
            self.pop.highlight_area(0)#selected map color

        elif self.pop.sender_pop == 'Go ' and self.manual.isChecked():
            self.pop.highlight_area(1)#original map color
            print("germania")
            self.pop.highlight_area(1)
            config.sel_dies_values = []
            config.sel_dies_values.append(self.pop.selection_temp)
            self.choose_dice(1)
            self.pop.selection_released()
            self.pop.selection_temp=[]
            #self.pop.clear_selection()
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.goto_die)
            self.execute(wrapper, func)

        elif self.pop.sender_pop == "Contact":
            print("Move Contact from Map")
            self.probestation.check_chuck_contact()
            if state.Application.check_contact==1:
                self.probestation.move_separation()
                self.pop.btn_contact.setStyleSheet("background-color : red")
            elif state.Application.check_contact==0:
                self.probestation.move_contact()
                self.pop.btn_contact.setStyleSheet("background-color : green")
            else:
                print("set contact from probe first")
                self.pop.btn_contact.setStyleSheet("background-color : yellow")

        elif self.pop.sender_pop == "Set Reference":
            self.pop.highlight_area(1)
            config.sel_dies_values = []
            config.sel_dies_values.append(self.pop.selection_temp) #extract selection dies
            self.choose_dice(1) #extract the cols and rows from selection
            print(config.sel_dies_values)
            self.pop.selection_released() #release the selection for dies size>1
            self.pop.selection_temp = [] #release the selection dies for die size=1
            print("Reference set")
            self.set_ref()  #please uncomment when testing

        #load reference position on the wafer
        #or load die values from the csv list reference.csv
        elif self.pop.sender_pop == "Load Reference":
            
            #self.load_ref() #please uncomment when testing and comment out everything below 
            self.pop.highlight_area(1)
            config.sel_dies_values = []
            values = self.load_dies_csv()
            config.sel_dies_values.append(values)
            self.choose_dice(0)
            self.pop.highlight_area(0)
            self.pop.selection_released()
            self.pop.selection_temp = [] 
            print("Reference loaded")
            
        else:
            print("Manual Control not selected")
            self.lcd_site()
            wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
            self.execute(wrapper, wrapper.check_chuck_contact)

    #this function updates the current position on the screen using a timer
    def lcd_site(self):

        self.lcd_value_old = self.lcd_value
        self.lcd_value='D'+str(state.Application.Dice_no)\
              +':('+str(state.Application.current_x_D)+\
              ','+str(state.Application.current_y_D)\
              +') S'+str(state.Application.Subdice_no)\
              +':('+str(state.Application.current_x_s)\
              +','+str(state.Application.current_y_s)\
              +')'
        self.location_label.setText(str(self.lcd_value))
        
        
        ####check_move_status
        if len(config.sel_dies_values)>0:
            self.manual_check()
            if state.Application.Dice_no==int(config.sel_dies_values[0])\
                and self.ban==0:#highlight first element of selection
                
                self.pop.highlight_position()
                self.ban=1

        if self.lcd_value!=self.lcd_value_old:
            self.manual_check()
            self.ban == 0
            try:
                self.pop.highlight_position()

                #print("salam")

            except:
                print("except")
            else:
                if state.Application.current_x_D=="-Out":
                    print("coloreaza celula stanga")
                elif state.Application.current_x_D=="+Out":
                    print("coloreaza celula dreapta")
                elif state.Application.current_y_D=="+Out":
                    print("coloreaza celula jos")
                elif state.Application.current_y_D == "+Out":
                    print("coloreaza celula sus")



    def set_ref(self):
        wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
        self.execute(wrapper, wrapper.set_reference_position)

    def load_ref(self):
        self.time_lapsed=0
        wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
        self.execute(wrapper, wrapper.load_prev_reference)

    def reset_move(self):
        print("Going back to reference position")
        self.pop.highlight_area
        wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
        self.execute(wrapper, wrapper.reset_move)

    #load die and subbdie values from a csv file
    def load_dies_csv(self):
            df=pd.read_csv('Dies.csv')
            print("aici")
            print(df)
            die_preset = df['Dies']
            #subdie_preset = df['Subdies']
            die_preset = die_preset.to_numpy()
            #subdie_preset = subdie_preset.to_numpy()
            print(die_preset)
            return die_preset#, subdie_preset
    
    #def find_index_position(self):
        #wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
        #self.execute(wrapper, wrapper.find_index_position)
    
#Take the input values from RRAM reading functions

    def manual_check(self):
        global manual_signal
        if self.manual.isChecked():
            manual_signal=1
        else:
            manual_signal=0
            
       
    #these preload functions takes the inputs given in the interface by the user from each selected function
    def retention_preload(self):
        
        time_mag=float(self.lineEdit_every.text())
        unit=float(self.multiply[self.every_dropDown.currentIndex()])
        every=time_mag*unit
        time_mag=float(self.lineEdit_duration.text())
        unit=float(self.multiply[self.duration_dropDown.currentIndex()])
        duration=time_mag*unit
        return (every, duration)
        
        
    def switch_seeker_preload(self):
        
        list=self.read_protocol_selection()
        #list.index("Switch Seeker")#>-1
        state.Application.switch_seek1=self.switch_seek1.text()
        state.Application.switch_seek2=self.switch_seek2.text()
        state.Application.switch_seek3=self.switch_seek3.text()
        state.Application.switch_seek4=self.switch_seek4.text()
        state.Application.switch_seek5=self.switch_seek5.text()
        state.Application.switch_seek6=self.switch_seek6.text()
        state.Application.switch_seek7=self.switch_seek7.text()
        state.Application.switch_seek8=self.switch_seek8.text()
        state.Application.switch_seek9=self.switch_seek9.text()
        state.Application.switch_seek10=self.switch_seek10.text()
        state.Application.switch_seek_combo1=self.switch_seek_combo1.currentIndex()
        state.Application.switch_seek_combo2=self.switch_seek_combo2.currentIndex()
        state.Application.CB_read_after=self.CB_read_after.isChecked()

        state.Application.job_ss ="%d" %self.switch_seek_combo1.itemData\
            (self.switch_seek_combo1.currentIndex())

        if self.CB_skip_stage1.isChecked():
            # -1 or 1 are the QVariants available from the combobox
            # -1 -> negative polarity for Stage II
            #  1 -> positive polarity for Stage II
            polarityIndex = self.switch_seek_combo2.currentIndex()
            
            state.Application.skipStageI = str(self.switch_seek_combo2.\
                                               itemData(polarityIndex))
        else:
             #if 0 then Stage I will not be skipped:
            state.Application.skipStageI = str(0)

        
    def formfinder_preload(self):
        idx = self.form_finder_combo2.currentIndex()
        state.Application.job_ff = self.form_finder_combo2.itemData(idx)["job"]
        state.Application.CB_form_finder1=self.CB_form_finder1.isChecked()
        state.Application.CB_form_finder2=self.CB_form_finder2.isChecked()
        state.Application.form_finder1 = self.form_finder1.text()
        state.Application.form_finder2 = self.form_finder2.text()
        state.Application.form_finder3 = self.form_finder3.text()
        state.Application.form_finder4 = self.form_finder4.text()
        state.Application.form_finder5 = self.form_finder5.text()
        state.Application.form_finder6 = self.form_finder6.text()
        state.Application.form_finder7 = self.form_finder7.text()
        state.Application.form_finder8 = self.form_finder8.text()
        state.Application.form_finder9 = self.form_finder9.text()
        state.Application.form_finder10 = self.form_finder10.text()
        state.Application.form_finder_combo1 = self.form_finder_combo1.currentIndex()
        state.Application.form_finder_combo2 = self.form_finder_combo2.currentIndex()
        state.Application.pSR=self.form_finder_combo1.currentData()
        pmodeIdx = self.form_finder_combo2.currentIndex()
        state.Application.pmode = self.form_finder_combo2.itemData(pmodeIdx)["mode"]

    def converge_preload(self):
        """ Transfer the parameters to ArC ONE """
        state.Application.converge1 = float(self.converge1.text())
        state.Application.converge7 = float(self.converge7.text())
        state.Application.converge8 = float(self.converge8.text())
        state.Application.converge6 = float(self.converge6.text()) / 1000.0
        state.Application.converge12 = int(self.converge12.text())
        state.Application.converge9 = float(self.converge9.text())
        state.Application.converge10 = float(self.converge10.text())
        state.Application.converge11 = float(self.converge11.text())
        state.Application.converge3 = float(self.converge3.text()) / 1000.0
        state.Application.converge4 = float(self.converge4.text())
        state.Application.converge5 = float(self.converge5.text()) / 1000.0
        idx = self.converge_combo1.currentIndex()
        state.Application.converge_combo1 = int(self.converge_combo1.itemData(idx))


    def curveTracer_preload(self):
        state.Application.curvetracer1=self.curvetracer1.text()
        state.Application.curvetracer2=self.curvetracer2.text()
        state.Application.curvetracer3=self.curvetracer3.text()
        state.Application.curvetracer4=self.curvetracer4.text()
        state.Application.curvetracer5=self.curvetracer5.text()
        state.Application.curvetracer6=self.curvetracer6.text()
        state.Application.curvetracer7=self.curvetracer7.text()
        state.Application.curvetracer8=self.curvetracer8.text()
        state.Application.curvetracer9=self.curvetracer9.text()
        state.Application.curvetracer10=self.curvetracer10.text()
        state.Application.curvetracer_combo1=self.curvetracer_combo1.currentIndex()
        state.Application.curvetracer_combo2=self.curvetracer_combo2.currentIndex()
        state.Application.CB_curvetracer1=self.CB_curvetracer1.isChecked()
        state.Application.CB_curvetracer2=self.CB_curvetracer2.isChecked()
        state.Application.totalCycles = int(self.curvetracer6.text())
        state.Application.job_ct = "201"

    def parameterFit_preload(self):
        state.Application.parameterfit1 = float(self.parameterfit1.text())
        state.Application.parameterfit2 = float(self.parameterfit2.text())
        state.Application.parameterfit3 = float(self.parameterfit3.text())
        state.Application.parameterfit4 = float(self.parameterfit4.text())
        state.Application.parameterfit5 = float(self.parameterfit5.text())/1.0e6
        state.Application.parameterfit6 = float(self.parameterfit6.text())/1.0e3
        state.Application.parameterfit7 = float(self.parameterfit7.text())*(-1.0)
        state.Application.parameterfit8 = float(self.parameterfit8.text())*(-1.0)
        state.Application.parameterfit9 = float(self.parameterfit9.text())*(-1.0)
        state.Application.parameterfit10= float(self.parameterfit10.text())

    def RILForming_preload(self):
        state.Application.RILForming1 = float(self.RILForming1.text()) #max voltage
        state.Application.RILForming2 = float(self.RILForming2.text()) #max cycles
        state.Application.RILForming3 = float(self.RILForming3.text()) #step voltage
        state.Application.RILForming4 = float(self.RILForming4.text()) #pulse width
        state.Application.RILForming5 = float(self.RILForming5.text()) #gamma
        
    def uniformity_preload(self):
        state.Application.uniformity1 = int(self.uniformity1.text()) #no of resistance bins to be averaged
        state.Application.CB_uniformity2 = self.CB_uniformity2.isChecked()
        state.Application.CB_uniformity3 = self.CB_uniformity3.isChecked()
        state.Application.Rs_top = float(self.uniformity4.text())
        state.Application.Rs_bottom = float(self.uniformity5.text())

    #decides what happens when pressing "apply to one"
    def programOne(self):
        global manual_signal
        manual_signal = 0
        self.switch_seeker_preload()
        self.formfinder_preload()
        self.converge_preload()
        self.curveTracer_preload()
        self.parameterFit_preload()
        self.RILForming_preload()
        self.uniformity_preload()
        #self.choose_dice(0)
        self.choose_global_param()

        if self.manual.isChecked():
            manual_signal = 1
            every, duration = self.retention_preload()
            rps = self.read_protocol_selection()
            devs = [[CB.word, CB.bit]]
            wrapper = InitChuckProcess(self.probestation, devs, rps,\
                                       every, duration, HW.conf.Vread)
            self.execute(wrapper, wrapper.read_protocol)
        else:
            devs=[[CB.word, CB.bit]]
            self.MoveWafer(devs)

    # decides what happens when pressing "apply to range"
    def programRange(self):
        global manual_signal
        manual_signal=0
        self.switch_seeker_preload()
        self.formfinder_preload()
        self.converge_preload()
        self.curveTracer_preload()
        self.parameterFit_preload()
        self.RILForming_preload()
        self.uniformity_preload()
        #self.choose_dice(0)
        self.choose_global_param()

        if self.manual.isChecked():
            manual_signal = 1
            every, duration = self.retention_preload()
            rps = self.read_protocol_selection()
            rangeDev = makeDeviceList(True)
            wrapper = InitChuckProcess(self.probestation, rangeDev,\
                                       rps, every, duration, HW.conf.Vread)
            self.execute(wrapper, wrapper.read_protocol)
        else:
            rangeDev = makeDeviceList(True)
            every, duration=self.retention_preload()
            self.MoveWafer(rangeDev)

    # decides what happens when pressing "apply to all"
    def programAll(self):
        global manual_signal
        manual_signal = 0 #used to save data in either 0:automation csv, 1:manual csv
        self.switch_seeker_preload()
        self.formfinder_preload()
        self.converge_preload()
        self.curveTracer_preload()
        self.parameterFit_preload()
        self.RILForming_preload()
        self.choose_global_param()
        #self.choose_dice(0)
        self.uniformity_preload()
        
        if self.manual.isChecked():
            manual_signal = 1
            every, duration = self.retention_preload()
            rps = self.read_protocol_selection()
            rangeDev = makeDeviceList(False)
            wrapper = InitChuckProcess(self.probestation, rangeDev,\
                                       rps, every, duration, HW.conf.Vread)
            self.execute(wrapper, wrapper.read_protocol)
        else:
            rangeDev = makeDeviceList(False)
            every, duration=self.retention_preload()
            self.MoveWafer(rangeDev)

    def eventFilter(self, object, event):
        if event.type()==QtCore.QEvent.Resize:
            self.vW.setFixedWidth(event.size().width() - \
                object.verticalScrollBar().width())
        return False

    def disableProgPanel(self,state):
        self.hboxProg.setEnabled(not state)

# skip functions unable or disable some input fields when a checkbox is checked
    def skip_stage1(self):
        if self.CB_skip_stage1.isChecked():
            self.switch_seek_combo2.setEnabled(True)
        else:
            self.switch_seek_combo2.setEnabled(False)
        
        if self.CB_uniformity2.isChecked():
            self.CB_uniformity3.setEnabled(True)
        else:
            self.CB_uniformity3.setEnabled(False)

    def skip_parameterfit(self):
        if self.CB_parameterfit1.isChecked():
            self.parameterfit1.setEnabled(False)
            self.parameterfit2.setEnabled(False)
            self.parameterfit3.setEnabled(False)
            self.parameterfit7.setEnabled(False)
            self.parameterfit8.setEnabled(False)
            self.parameterfit9.setEnabled(False)
        else:
            self.parameterfit1.setEnabled(True)
            self.parameterfit2.setEnabled(True)
            self.parameterfit3.setEnabled(True)
            self.parameterfit7.setEnabled(True)
            self.parameterfit8.setEnabled(True)
            self.parameterfit9.setEnabled(True)

#other auxiliar functions used by the reading modules
    def pulsingModeComboIndexChanged(self, idx):
        #idx = self.form_finder_combo2.currentIndex()
        data = self.form_finder_combo2.itemData(idx)
        mode = data["mode"]
        if int(mode) == 1:
            self.form_finder5_label.setText("Pulse width step (us)")
        else:
            self.form_finder5_label.setText("Pulse width step (%)")


#other imported functions
    def imposeLimitsOnStepWidth(self):
        currentText=float(self.curvetracer5.text())
        if (currentText<2):
            self.curvetracer5.setText("2")

    def imposeLimitsOnCurrentStopP(self):
        currentText=float(self.curvetracer8.text())
        if (currentText<10):
            if (currentText==0):
                self.curvetracer8.setText("0")
            else:
                self.curvetracer8.setText("10")

        if (currentText>1000):
            self.curvetracer8.setText("1000")

    def imposeLimitsOnCurrentStopN(self):
        currentText=float(self.curvetracer8.text())
        if (currentText<10):
            if (currentText==0):
                self.curvetracer8.setText("0")
            else:
                self.curvetracer8.setText("10")
        if (currentText>1000):
            self.curvetracer8.setText("1000")

    exec(open(os.path.join(arcpyqt, "displayscript.py")).read())  # includes all display functions

    #self.valueChanged = pyqtSignal(object)
    #def setValue(self, val):
    #    self.valueChanged.emit(value)

    def launch_map_popup(self):
        global map_show

        if map_show==0:
            self.pop.show()
            map_show=1
        else:
            self.pop.hide()
            map_show=0

#build and show the wafer map defined in config.py in a popup window
class waferMap(QDialog):

    def __init__(self, name, parent):
        super().__init__(parent)
        self.resize(600, 600)
        self.row = 0  # used for highlighting map selection
        self.col = 0
        self.row_old = 0
        self.col_old = 0
        self.sender_pop=0
        self.select_released=0
        self.selection_temp = []
        self.selection_temp2 = []
        self.p1=0
        self.p2=0
        self.UI_wafermap()


        self.goto_dies.clicked.connect(self.pop_sender)
        self.tableWidget.clicked.connect(self.selection_released)
        self.tableWidget.selectionModel().selectionChanged.connect(self.tableWidget_sel)
        self.timer.timeout.connect(self.selection_released)
        self.timer2.timeout.connect(self.progress_bar)
        self.timer2.timeout.connect(self.show_position)
        self.refresh.clicked.connect(self.refresh_fct2)
        self.set_reference.clicked.connect(self.pop_sender)
        self.load_reference.clicked.connect(self.pop_sender)
        self.btn_contact.clicked.connect(self.pop_sender)


        #self.refresh.clicked.connect(self.save_selection)

    def UI_wafermap(self):
        exec(open(os.path.join(arcpyqt, "graphics_wafermap.py")).read())

    #highight the position of the current die
    def highlight_position(self):
        global manual_signal
        print("Manual signal is %s" %manual_signal)

        rel = int(np.amax(config.w, axis=0))#max row offset
        
        #if manual control is selected
        if manual_signal==1: #revert previous device to original color
            brush0_old=QtGui.QBrush(QtGui.QColor(250, 250, 250))
            brush1_old=QtGui.QBrush(QtGui.QColor(214, 0, 0))
        else:
        
            #color previous devices with a 'read' color
            brush0_old = QtGui.QBrush(QtGui.QColor(15, 180, 180))
            brush1_old = QtGui.QBrush(QtGui.QColor(15, 110, 90))
            
        brush0 = QtGui.QBrush(QtGui.QColor(55, 280, 180))
        brush1 = QtGui.QBrush(QtGui.QColor(55, 210, 90))
        
        #paint original colour (deselect) for previous die if automatic control is selected
        if config.dies_color[int(state.Application.Dice_no) - 1] == 1:
            brush0_old.setStyle(QtCore.Qt.SolidPattern)
            self.tableWidget.item(self.row_old, self.col_old).setBackground(brush0_old)
        elif config.dies_color[int(state.Application.Dice_no) - 1] == 0:
            brush1_old.setStyle(QtCore.Qt.SolidPattern)
            self.tableWidget.item(self.row_old, self.col_old).setBackground(brush1_old)
        #self.tableWidget.item(self.row_old, self.col_old).setSelected(False)

        #calculate new position
        self.col = (rel - config.w[state.Application.current_y_D]) + state.Application.current_x_D
        self.row = state.Application.current_y_D

        #paint new position colour (select) for current die
        if config.dies_color[int(state.Application.Dice_no) - 1] == 0:
            brush0.setStyle(QtCore.Qt.SolidPattern)
            self.tableWidget.item(self.row, self.col).setBackground(brush1)
        if config.dies_color[int(state.Application.Dice_no) - 1] == 1:
            brush1.setStyle(QtCore.Qt.SolidPattern)
            self.tableWidget.item(self.row, self.col).setBackground(brush1)
        #self.tableWidget.item(self.row, self.col).setSelected(True)

        self.col_old=self.col
        self.row_old=self.row

    #output selected dies values
    def tableWidget_sel(self, selected, deselected):
        self.timer.start(60000)
        self.p1=1
        self.p2=0

        for ix in selected.indexes():
            self.p2 = 1
            if self.tableWidget.item(ix.row(), ix.column()).text()!=" ":
                self.selection_temp.append(self.tableWidget.item(ix.row(), ix.column()).text())

        #update the selection_temp if selection shrinkfrom a larger one
        if self.p1!=self.p2:
            #print("intors")
            self.selection_temp=[]
            self.refresh_fct()
            self.p1=0
            self.p2=0
        self.pick_structure()

        #self.selection_temp2=self.selection_temp.copy()


    #empty the self.selection_temp and clear selected area
    # after two consectutive clicks, or waiting time
    #allows ctrl selection
    def selection_released(self):

        modifiers=QApplication.keyboardModifiers()
        if len(self.selection_temp) > 1 and modifiers == Qt.ControlModifier:
            pass
        elif len(self.selection_temp)>1:
            print("isi da drumu perfect")
            self.selection_temp=[]
            self.tableWidget.clearSelection()
            self.timer.start(100000000)


    #empty selected dies, and selected area
    def refresh_fct(self):

        #print("isi da refresh perfect")
        self.selection_temp = []
        self.tableWidget.clearSelection()
        self.timer.start(100000000)



    #this function is the refresh set on button to also refresh the color of the dies
    def refresh_fct2(self):

        #print("isi da refresh perfect2")
        self.selection_temp = []
        self.tableWidget.clearSelection()
        self.timer.start(100000000)
        self.highlight_area(1)

    def clear_selection(self):
        self.tableWidget.clearSelection()

    def build_selection(self, row, col):
        self.tableWidget.item(row, col).setSelected(True)

    def delete_selection(self, row, col):
        self.tableWidget.item(row, col).setSelected(False)


    #sends the button name when the respective button is pressed.
    def pop_sender(self):
        self.sender_pop=self.sender().text()

    #update the progress bar
    def progress_bar(self):
        global process_finished#check if reading has finished
        self.all_dies=(config.row.size*config.row_sub.size)+0.0001
        self.pbar.setValue(int((config.device_count/self.all_dies)*100))
        self.time_est.setText("Time Estimated Remaining: %.2f s" %state.Application.time_est)
        
        
        
        if process_finished==1:
            self.pbar.setValue(0) #reset the progress bar when whole process finished
            self.highlight_area(1)#reset previous selection colour
            self.time_est.setText("Time Estimated Remaining:")


    #highlight with a different color the dice that are going to be scanned
    def highlight_area(self, undo):
        
        if undo==0:
            brush0 = QtGui.QBrush(QtGui.QColor(15, 180, 180))
            brush1 = QtGui.QBrush(QtGui.QColor(15, 110, 90))
        elif undo == 1:#restore original map
            brush0 = QtGui.QBrush(QtGui.QColor(250, 250, 250))
            brush1 = QtGui.QBrush(QtGui.QColor(214, 0, 0))

        for i in range(config.row.size):
            
            if config.dies_color[int(config.sel_dies_values[i])-1]==0:

                brush0.setStyle(QtCore.Qt.SolidPattern)
                self.tableWidget.item(config.row[i], int(config.col[i] + \
                (self.maxval_w_index - config.w[config.row[i]]))).setBackground(brush0)

            elif config.dies_color[int(config.sel_dies_values[i])-1]==1:

                brush1.setStyle(QtCore.Qt.SolidPattern)
                self.tableWidget.item(config.row[i], int(config.col[i] + \
                (self.maxval_w_index - config.w[config.row[i]]))).setBackground(brush1)

        #self.tableWidget.clearSelection()
    def check_highlighted(self):
        pass

    #pick the dies with a specific structure e.g. crossbar, single arrays, all
    def pick_structure(self):

        if self.pick_All.isChecked()==0:
            for i in range(len(self.selection_temp)):
                    if config.dies_color[int(self.selection_temp[i])-1]==0\
                    and self.pick_CB.isChecked():
                        self.selection_temp2.append(self.selection_temp[i])

                    elif config.dies_color[int(self.selection_temp[i])-1]==1\
                    and self.pick_SA.isChecked():
                        self.selection_temp2.append(self.selection_temp[i])

            self.selection_temp=[]
            self.selection_temp=self.selection_temp2.copy()
            self.selection_temp2=[]

        elif self.pick_All.isChecked():
            pass


    #show current position die and subdie in text
    def show_position(self):
        self.position_label.setText("D:%s |  S:%s" %(state.Application.Dice_no,\
                                                     state.Application.Subdice_no))

#the 'voltage finder' algorithm
class EpsilonGreedyCautious():
    """Update of EpsilonGreedy with a bit more caution made 
    by starting from lower voltages first and then progressing to higher 
    voltages as we explore
    """
    def __init__(self, max_attempts:int, gamma:float):
        super().__init__()
        
        global NUM_NON_FAIL_STATES, MAX_VOLTAGE, MIN_VOLTAGE, STEP_VOLTAGES, CLASS_NUMBER 
        
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
            


tags = {
    'top': ModTag(tag, "TestModule", None),
    'subtags': [
        ModTag(tag+"1", "Retention", TestModule.display_retention),
        ModTag(tag+"4", "Converge to State", None),
        ModTag(tag+"3", "FormFinder", TestModule.display_formfinder),
        ModTag(tag+"2", "Switch Seeker", TestModule.display_switchseeker),
        ModTag(tag+"5", "CurveTracer", TestModule.display_curve),
        ModTag(tag+"6", "ParameterFit", TestModule.display_parameterfit),
        ModTag(tag+"7", "RILForming", TestModule.display_parameterfit),
        ModTag(tag+"8", "Uniformity", None)
    ]
}

#tags = { 'top': ModTag(tag, "TestModule", TestModule.display_curve) }

