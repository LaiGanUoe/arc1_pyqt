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

from probelibrary import ProbeStation
from controller import make_controller
from controller import CNTRL_TYPE

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTime, QTimer

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

heading="Measurement,Die, Subdie, Word, Bit, Resistance (Ohms),\
# Read Voltage (V), PW (ms), Time (s)"
heading_signal="Yes/No, Dice, Subdice, W,B, Rate, Vnew, Rnew, Vold, Rold, Time (s)"

#clear the files containing the manual measurement data
f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ss_manual.csv", "w")
f.truncate()
f.close()
f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ct_manual.csv", "w")
f.truncate()
f.close()
f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ff_manual.csv", "w")
f.truncate()
f.close()
f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_cts_manual.csv", "w")
f.truncate()
f.close()
f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_rt_manual.csv", "w")
f.truncate()
f.close()
f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_pf_manual.csv", "w")
f.truncate()
f.close()


ss_index=0
ff_index=0
ct_index=0
cts_index=0
rt_index=0
pf_index=0

rdf=1

Dx_local=0
sx_local=0
manual_signal=0
pf_signal=0

def _log(*args, **kwargs):
    if bool(os.environ.get('TMMDBG', False)):
        print(*args, file=sys.stderr, **kwargs)

class InitChuckProcess(BaseThreadWrapper):

    def __init__(self, probe, deviceList, rps, every, duration, Vread):
        super().__init__()
        self.probestation = probe
        self.deviceList=deviceList
        self.rps = rps
        self.every=every
        self.duration=duration
        self.Vread=Vread
        self.DBG = False

    sendData = QtCore.pyqtSignal(int, int, float, float, float, str, float)

#Thread
#select the reading protocol
    @BaseThreadWrapper.runner
    def read_protocol(self):
        global reading, pf_signal
        self.find_index_position()
        list_var = ['Retention', 'Form Finder', 'Switch Seeker', 'Converge', 'CurveTracer', 'ParameterFit']
        for i in range(len(self.rps)):
            for j in range(len(self.rps)):
                if self.rps[i] == list_var[j]:
                    rps_split = self.rps[i].split(' ')
                    fct_name = ("self.run_%s()" % rps_split[0])
                    if self.rps[i]=="Switch Seeker" and self.rps[i+1]=="ParameterFit":
                        pf_signal=1
                    #else:
                        #pf_signal=0
                    print("pf signal is: %s" %pf_signal)
                    print("rps is: %s" %self.rps)
                    print("rps i is: %s" % self.rps[i])
                    print("rps i+1 is: %s" %self.rps[i+1])
                    print(fct_name)
                    time.sleep(0.1)
                    exec(fct_name)

#find threshold voltage for switch seeker
    @BaseThreadWrapper.runner
    def find_rate_ss(self):
        global rdf, ss_index

        if "Switch Seeker" in self.rps:
            indice=0
            rows=np.array([])
            field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']
            print("1")
            with open('C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ss_%s.csv'%rdf, 'r') as file:
                csvreader=list(csv.reader(file, delimiter=","))
            csvreader=np.array(csvreader)
            size_csv=csvreader.shape
            size_csv=size_csv[0]
            print("size_csv=%s" %size_csv)
            print(csvreader[0])
            target=int(size_csv/(ss_index*len(self.deviceList)))
            print("2")
            with open('C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/signal_ss_%s.csv' % rdf, 'a', newline='') as f_object:
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
    @BaseThreadWrapper.runner
    def find_rate_ff(self):

        global rdf, ff_index

        if "Form Finder" in self.rps:
            indice=0
            print(time.time())
            rows=np.array([])
            field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']
            print("1")
            
            with open('C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ff_%s.csv'%rdf, 'r') as file:
                csvreader=list(csv.reader(file, delimiter=","))
                
            csvreader=np.array(csvreader)
            size_csv=csvreader.shape
            size_csv=size_csv[0]
            print(csvreader[0])
            target = int(size_csv / (ff_index * len(self.deviceList)))
 
            with open('C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/signal_ff_%s.csv' % rdf, 'a', newline='') as f_object:
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

        with open('C:/Users/Alin/Desktop/arc1_pyqt/data_ss_pf.csv', 'r') as file:
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
    def run_ParameterFit(self):
        global tag, pf_signal, manual_signal, pass_pf_data, pass_pf_data2, pass_pf_data_neg, pass_pf_data2_neg, rdf


        #voltages = []
        k=0

        if manual_signal == 0:
            file_name = 'C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_pf_%s.csv' % rdf
        else:
            file_name = 'C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_pf_manual.csv'

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
            k=k+1

            self.updateTree.emit(w, b)
        pf_signal = 0
        f_object.close()

    # form finder Parameter fit
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
#curve tracer
    @BaseThreadWrapper.runner
    def run_CurveTracer(self):
        global tag, ct_index, manual_signal
        repeat=0

        field_names = ['Measurement', 'D', 'S', 'W', 'B', 'Res', 'V', 'PW', 'Time', 'Rate']

        HW.ArC.write_b(state.Application.job_ct + "\n")
        HW.ArC.write_b(str(float(state.Application.curvetracer1)) + "\n")
        HW.ArC.write_b(str(float(state.Application.curvetracer2)) + "\n")
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

        if manual_signal==0:
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ct_%s.csv'%rdf

        else:
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ct_manual.csv'

        f_object = open(file_name, 'a', newline='')
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)

        for device in self.deviceList:
            w = device[0]
            b = device[1]
            self.highlight.emit(w, b)
            HW.ArC.queue_select(w, b)
            firstPoint = 1
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
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_cts_%s.csv'%rdf
        else:
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_cts_manual.csv'

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
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ff_%s.csv'%rdf
        else:
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ff_manual.csv'

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

        f = open("C:/Users/Alin/Desktop/arc1_pyqt/data_ss_pf.csv", "w")
        f.truncate()
        f.close()

        if manual_signal == 0:
            file_name = 'C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ss_%s.csv' % rdf
        else:
            file_name = 'C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ss_manual.csv'

        if pf_signal == 1:
            file_name = 'C:/Users/Alin/Desktop/arc1_pyqt/data_ss_pf.csv'

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
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_rt_%s.csv'%rdf
        else:
            file_name='C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_rt_manual.csv'

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

                    Mnow = HW.ArC.read_one(w, b)
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
    def set_reference_position(self):
        config.Xr, config.Yr, c = self.probestation.position
        print("Xref=%s, Yref=%s" % (config.Xr, config.Yr))
        self.find_index_position()
        time.sleep(0.1)

    @BaseThreadWrapper.runner
    def reset_move(self):
        x, y, z = self.probestation.position
        #print("Uncorrected reset position x=%s, y=%s" %(x,y))
        x=x-config.Xr
        y=y-config.Yr
        #print("Corrected delta reset by x=%s, y=%s" %(x,y))
        self.move_relative(-x, -y)
        x, y, z = self.probestation.position
        print("Wafer position corrected")
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
        print(x,y)
        #aici bagi conditia de x
        Dx=abs(int(x/config.index_x))
        Dy=abs(int(y/config.index_y))
        Dx_signed=int(x/config.index_x)
        Dy_signed=int(x/config.index_x)
        
        if 0<abs(x)<config.index_x:
            sx=int(abs(x)/config.subindex_x)
        else:
            sx = int((abs(x) % config.index_x) / config.subindex_x)
        if 0<abs(y)<config.index_y:
            sy=int(abs(y)/config.subindex_y)
        else:
            sy = int((abs(y) % config.index_y) / config.subindex_y)
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
                Dx = -Dx_signed + config.w[Dy]
                for i in range(Dy):
                    sum=sum+config.x[i]
                sum=sum+Dx+1

        subdice=sy*3+sx+1
        print("D%s:(%s,%s) S%s:(%s,%s)" %(sum,Dx,Dy,subdice,sx,sy))
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
    def open_files(self):
        global rdf
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ss_%s.csv" % rdf, "w")
        f.truncate()
        f.close()
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/signal_ss_%s.csv" % rdf, "w")
        f.truncate()
        f.close()
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ff_%s.csv" % rdf, "w")
        f.truncate()
        f.close()
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/signal_ff_%s.csv" % rdf, "w")
        f.truncate()
        f.close()
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_ct_%s.csv" % rdf, "w")
        f.truncate()
        f.close()
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_cts_%s.csv" % rdf, "w")
        f.truncate()
        f.close()
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_rt_%s.csv" % rdf, "w")
        f.truncate()
        f.close()
        f = open("C:/Users/Alin/Desktop/arc1_pyqt/Log_Data/data_pf_%s.csv" % rdf, "w")
        f.truncate()
        f.close()

    @BaseThreadWrapper.runner
    def read_subdice(self):
        # perform the chuck movement in the given subdie in 
        # given sub_row, sub_col vectors
        print("\nStart subdice scanning/reading")
        self.set_chuck_index(config.subindex_x, config.subindex_y)
        self.move_chuck_index(-config.col_sub[0], config.row_sub[0])

        for i in range(config.col_sub.size):
            print("Sub-column is %s, Sub-row is %s" % (config.col_sub[i], \
            config.row_sub[i]))

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

        global rdf
        self.open_files()
        time_start=time.time()

        self.reset_move()
        self.set_chuck_index(config.index_x, config.index_y)
        self.move_chuck_index(-(config.col[0] - config.w[config.row[0]]), config.row[0])

        for i in range(config.row.size):
            print("Current Row is: " + str(config.row[i]))

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
        self.initUI()
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
        self.show_fct1.clicked.connect(self.choose_combo)
        self.show_fct2.clicked.connect(self.choose_combo)
        self.show_fct3.clicked.connect(self.choose_combo)
        self.show_fct4.clicked.connect(self.choose_combo)
        self.show_fct5.clicked.connect(self.choose_combo)
        self.show_fct6.clicked.connect(self.choose_combo)
        self.CB_skip_stage1.clicked.connect(self.skip_stage1)
        self.CB_parameterfit1.clicked.connect(self.skip_parameterfit)
        self.form_finder_combo2.currentIndexChanged.connect(self.pulsingModeComboIndexChanged)
        self.curvetracer8.editingFinished.connect(self.imposeLimitsOnCurrentStopP)
        self.curvetracer8.editingFinished.connect(self.imposeLimitsOnCurrentStopN)
        self.curvetracer5.editingFinished.connect(self.imposeLimitsOnStepWidth)


        #self.controller=make_controller(CNTRL_TYPE.PROLOGIX,20, ['COM4'])
        self.probestation =  ProbeStation(22, CNTRL_TYPE.PROLOGIX, ['COM4'])

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        #push button "Move Probe"
        self.button = QtWidgets.QPushButton('Move back to reference')
        layout.addWidget(self.button)

#"apply" push bottons for readings
        hbox = QtWidgets.QHBoxLayout()
        self.doOne = QtWidgets.QPushButton('Apply to One')
        self.doRange = QtWidgets.QPushButton('Apply to Range')
        self.doAll = QtWidgets.QPushButton('Apply to All')
        hbox.addWidget(self.doOne)
        hbox.addWidget(self.doRange)
        hbox.addWidget(self.doAll)
        hbox.addWidget(self.doAll)

#lcd screen
        self.my_location_label = QLabel('Current site:', self)
        self.my_location_label.setGeometry(0, 230, 100, 30)
        self.location_label = QLabel('...', self)
        self.location_label.setGeometry(0, 245, 120, 20)
        self.timer=QTimer()
        self.timer.timeout.connect(self.lcd_site)
        self.timer.start(100)
        self.lcd_site()

#Spinboxes
        #spinbox label
        self.spinBox_anyrow_label = QLabel('Read One Row', self)
        self.spinBox_anyrow_label.setGeometry(0, 30, 80, 20)
        #spinbox row
        self.spinBox_anyrow = QtWidgets.QSpinBox(self)
        self.spinBox_anyrow.setGeometry(QtCore.QRect(20, 50, 42, 22))
        self.spinBox_anyrow.setMaximum(config.row_size)
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
        self.spinBox_rowrangeto.setMaximum(config.row_size)
        self.spinBox_rowrangeto.setSingleStep(1)
        self.spinBox_rowrangeto.setObjectName("rowrangeto")
        #spinbox "to"
        self.spinBox_rowrangefrom = QtWidgets.QSpinBox(self)
        self.spinBox_rowrangefrom.setGeometry(QtCore.QRect(70, 110, 42, 22))
        self.spinBox_rowrangefrom.setMaximum(config.row_size)
        self.spinBox_rowrangefrom.setSingleStep(1)
        self.spinBox_rowrangefrom.setObjectName("rowrangefrom")

        #spinbox movestep
        self.spinBox_movestep_label = QLabel('Move Unit', self)
        self.spinBox_movestep_label.setGeometry(147, 144, 60, 20)
        self.spinBox_movestep = QtWidgets.QSpinBox(self)
        self.spinBox_movestep.setGeometry(QtCore.QRect(155, 160, 30, 22))
        self.spinBox_movestep.setMaximum(config.row_size)
        self.spinBox_movestep.setSingleStep(1)
        self.spinBox_movestep.setValue(1)
        self.spinBox_movestep.setObjectName("movestep")


#Radio Buttons
        self.RB_anyrow = QtWidgets.QRadioButton(self)
        self.RB_anyrow.setChecked(False)
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
        self.RB_desired.setChecked(True)
        self.RB_desired.setGeometry(QtCore.QRect(0, 190, 15, 15))
        self.manual = QtWidgets.QRadioButton(self)
        self.manual.setChecked(False)
        self.manual.setGeometry(QtCore.QRect(120, 110, 15, 15))


#Checkboxes
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

        #skip odd checkbox
        self.skip_odd_label=QtWidgets.QLabel('Skip odd dice:', self)
        self.skip_odd_label.setGeometry(0, 205, 100, 20)
        self.skip_odd = QtWidgets.QCheckBox(self)
        self.skip_odd.setGeometry(70, 205, 100, 20)

#Push Buttons
        #manual control
        self.move_up_label=QtWidgets.QLabel('Manual Control', self)
        self.move_up_label.setGeometry(140, 110, 80, 20)
        self.move_up = QtWidgets.QPushButton('up',self)
        self.move_up.setGeometry(150, 130, 40, 20)
        self.move_down = QtWidgets.QPushButton('down',self)
        self.move_down.setGeometry(150, 190, 40, 20)
        self.move_left = QtWidgets.QPushButton('L',self)
        self.move_left.setGeometry(120, 160, 30, 20)
        self.move_right = QtWidgets.QPushButton('R',self)
        self.move_right.setGeometry(190, 160, 30, 20)
        self.move_contact = QtWidgets.QPushButton('C',self)
        self.move_contact.setGeometry(130, 215, 20, 20)
        self.move_separation = QtWidgets.QPushButton('S',self)
        self.move_separation.setGeometry(150, 215, 20, 20)
        self.set_index_dice = QtWidgets.QPushButton('Di',self)
        self.set_index_dice.setGeometry(170, 215, 20, 20)
        self.set_index_subdice = QtWidgets.QPushButton('di',self)
        self.set_index_subdice.setGeometry(190, 215, 20, 20)
        self.set_reference = QtWidgets.QPushButton('Set Ref',self)
        self.set_reference.setGeometry(530, 40, 60, 25)
        self.show_fct1 = QtWidgets.QPushButton('fct1', self)
        self.show_fct1.setGeometry(530, 70, 60, 25)
        self.show_fct2 = QtWidgets.QPushButton('fct2', self)
        self.show_fct2.setGeometry(530, 100, 60, 25)
        self.show_fct3 = QtWidgets.QPushButton('fct3', self)
        self.show_fct3.setGeometry(530, 130, 60, 25)
        self.show_fct4 = QtWidgets.QPushButton('fct4', self)
        self.show_fct4.setGeometry(530, 160, 60, 25)
        self.show_fct5 = QtWidgets.QPushButton('fct5', self)
        self.show_fct5.setGeometry(530, 190, 60, 25)
        self.show_fct6 = QtWidgets.QPushButton('fct6', self)
        self.show_fct6.setGeometry(530, 220, 60, 25)

        layout.addItem(QtWidgets.QSpacerItem(40, 10, \
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        layout.addLayout(hbox)
        self.setLayout(layout)
        
#selection module combo
        self.fct1_combo=QtWidgets.QComboBox(self)
        self.fct1_combo.setGeometry(440, 70, 80, 20)
        self.fct1_combo.addItem(" ")
        self.fct1_combo.addItem("Form Finder")
        self.fct1_combo.addItem("Switch Seeker")
        self.fct1_combo.addItem("Retention")
        self.fct1_combo.addItem("Converge")
        self.fct1_combo.addItem("CurveTracer")
        self.fct1_combo.addItem("ParameterFit")


        self.fct2_combo = QtWidgets.QComboBox(self)
        self.fct2_combo.setGeometry(440, 100, 80, 20)
        self.fct2_combo.addItem(" ")
        self.fct2_combo.addItem("Form Finder")
        self.fct2_combo.addItem("Switch Seeker")
        self.fct2_combo.addItem("Retention")
        self.fct2_combo.addItem("Converge")
        self.fct2_combo.addItem("CurveTracer")
        self.fct2_combo.addItem("ParameterFit")

        self.fct3_combo = QtWidgets.QComboBox(self)
        self.fct3_combo.setGeometry(440, 130, 80, 20)
        self.fct3_combo.addItem(" ")
        self.fct3_combo.addItem("Form Finder")
        self.fct3_combo.addItem("Switch Seeker")
        self.fct3_combo.addItem("Retention")
        self.fct3_combo.addItem("Converge")
        self.fct3_combo.addItem("CurveTracer")
        self.fct3_combo.addItem("ParameterFit")

        self.fct4_combo = QtWidgets.QComboBox(self)
        self.fct4_combo.setGeometry(440, 160, 80, 20)
        self.fct4_combo.addItem(" ")
        self.fct4_combo.addItem("Form Finder")
        self.fct4_combo.addItem("Switch Seeker")
        self.fct4_combo.addItem("Retention")
        self.fct4_combo.addItem("Converge")
        self.fct4_combo.addItem("CurveTracer")
        self.fct4_combo.addItem("ParameterFit")
        self.hidden = True

        self.fct5_combo = QtWidgets.QComboBox(self)
        self.fct5_combo.setGeometry(440, 190, 80, 20)
        self.fct5_combo.addItem(" ")
        self.fct5_combo.addItem("Form Finder")
        self.fct5_combo.addItem("Switch Seeker")
        self.fct5_combo.addItem("Retention")
        self.fct5_combo.addItem("Converge")
        self.fct5_combo.addItem("CurveTracer")
        self.fct5_combo.addItem("ParameterFit")

        self.fct6_combo = QtWidgets.QComboBox(self)
        self.fct6_combo.setGeometry(440, 220, 80, 20)
        self.fct6_combo.addItem(" ")
        self.fct6_combo.addItem("Form Finder")
        self.fct6_combo.addItem("Switch Seeker")
        self.fct6_combo.addItem("Retention")
        self.fct6_combo.addItem("Converge")
        self.fct6_combo.addItem("CurveTracer")
        self.fct6_combo.addItem("ParameterFit")

        self.fct7 = QtWidgets.QTextEdit(self)
        self.fct7.setText("4,12,14,21,23,25,34,36,38,46,48,50,61,63,65,75,77,79,81,91,93,95")
        self.fct7.setGeometry(0, 300, 100, 100)
        self.fct7_label = QLabel("Select dice:", self)
        self.fct7_label.setGeometry(0, 240, 100, 100)

        self.fct8 = QtWidgets.QLineEdit(self)
        self.fct8.setText("10")
        self.fct8.setGeometry(440, 260, 80, 20)
        self.fct8_label=QLabel("Trigger min ratio (%):", self)
        self.fct8_label.setGeometry(440, 240, 80, 20)

        self.fct9 = QtWidgets.QLineEdit(self)
        self.fct9.setText("20")
        self.fct9.setGeometry(440, 300, 80, 20)
        self.fct9_label = QLabel("Trigger max ratio (%):", self)
        self.fct9_label.setGeometry(440, 280, 80, 20)


        exec(open("C:/Users/Alin/Desktop/arc1_pyqt/switchscript.py").read())#switch seeker graphics
        exec(open("C:/Users/Alin/Desktop/arc1_pyqt/formingscript.py").read())#form finder graphics
        exec(open("C:/Users/Alin/Desktop/arc1_pyqt/convergescript.py").read())#converge to state graphics
        exec(open("C:/Users/Alin/Desktop/arc1_pyqt/retentionscript.py").read())#retention graphics
        exec(open("C:/Users/Alin/Desktop/arc1_pyqt/curvetracerscript.py").read())#curve tracer graphics
        exec(open("C:/Users/Alin/Desktop/arc1_pyqt/parameterfitscript.py").read())  # curve tracer graphics
    exec(open("C:/Users/Alin/Desktop/arc1_pyqt/hideunhide.py").read())

    def choose_rate(self):
        config.rate=float(self.fct8.text())
        print("Config rate min: %s" %config.rate)
        config.rate2 = float(self.fct9.text())
        print("Config rate max: %s" %config.rate2)

    def choose_dice(self):
        sum=0
        config.D=np.array([])
        config.D = config.D.astype(int)
        config.row = np.array([])
        config.col = np.array([])
        config.row = config.row.astype(int)
        config.col = config.col.astype(int)

        values=self.fct7.toPlainText()
        values=values.split(',')
        for i in range(len(values)):
            config.D=np.append(config.D, int(values[i]), )
        print(config.D)
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


    def choose_combo(self):
        sender = self.sender()
        val1=self.fct1_combo.currentText()
        val2=self.fct2_combo.currentText()
        val3=self.fct3_combo.currentText()
        val4=self.fct4_combo.currentText()
        val5=self.fct5_combo.currentText()
        val6 = self.fct6_combo.currentText()
        buttons=['fct1', 'fct2', 'fct3', 'fct4', 'fct5', 'fct6']
        combo_val=[val1, val2, val3, val4, val5, val6]
        for i in range(len(buttons)):
            if sender.text()==buttons[i]:
                self.hide_unhide(combo_val[i])


    def read_protocol_selection(self):
        list = [self.fct1_combo.currentText(), \
                self.fct2_combo.currentText(), \
                self.fct3_combo.currentText(), \
                self.fct4_combo.currentText(), \
                self.fct5_combo.currentText(), \
                self.fct6_combo.currentText()]
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

        move_unit = self.spinBox_movestep.value()

        if sender.text()=='up' and self.manual.isChecked():
            print("Move up")

            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, 0, -move_unit)
            self.execute(wrapper, func)

        elif sender.text()=='down' and self.manual.isChecked():
            print("Move down")
            #if config.move_limit==0:
                #config.moved_y = config.moved_y + 1
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, 0, move_unit)
            self.execute(wrapper, func)

        elif sender.text()=='L' and self.manual.isChecked():
            print("Move left")
           # if config.move_limit==0:
           #     config.moved_x = config.moved_x + 1
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, move_unit, 0)
            self.execute(wrapper, func)

        elif sender.text()=='R' and self.manual.isChecked():
            print("Move right")
            print("config limit right %s"%config.move_limit)
            #if config.move_limit==0:
                #config.moved_x = config.moved_x + (-1)
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            func = partial(wrapper.move_chuck_index, -move_unit, 0)
            self.execute(wrapper, func)

        elif sender.text()=='C' and self.manual.isChecked():
            #print("Move Contact")
            wrapper = InitChuckProcess(self.probestation, 0,0,0,0,0)
            self.execute(wrapper, wrapper.move_contact)

        elif sender.text()=='S' and self.manual.isChecked():
            #print("Move separation")
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
        else:
            print("Manual Control not selected")
            self.lcd_site()
            wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
            self.execute(wrapper, wrapper.check_chuck_contact)

    def lcd_site(self):
        value='D'+str(state.Application.Dice_no)\
              +':('+str(state.Application.current_x_D)+\
              ','+str(state.Application.current_y_D)\
              +') S'+str(state.Application.Subdice_no)\
              +':('+str(state.Application.current_x_s)\
              +','+str(state.Application.current_y_s)\
              +')'
        self.location_label.setText(str(value))

    def set_ref(self):
        wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
        self.execute(wrapper, wrapper.set_reference_position)

    def reset_move(self):
        print("Going back to reference position")
        wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
        self.execute(wrapper, wrapper.reset_move)

    #def find_index_position(self):
        #wrapper = InitChuckProcess(self.probestation, 0, 0, 0, 0, 0)
        #self.execute(wrapper, wrapper.find_index_position)
    
#Take the input values from RRAM reading functions

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
        state.Application.curvetracer_combo1=self.curvetracer_combo1.currentIndex()
        state.Application.curvetracer_combo2=self.curvetracer_combo1.currentIndex()
        state.Application.CB_curvetracer1=self.CB_curvetracer1.isChecked()
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

    #decides what happens when pressing "apply to one"
    def programOne(self):
        global manual_signal
        manual_signal = 0
        self.switch_seeker_preload()
        self.formfinder_preload()
        self.converge_preload()
        self.curveTracer_preload()
        self.parameterFit_preload()
        self.choose_dice()
        self.choose_rate()

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
        self.choose_dice()
        self.choose_rate()

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
        self.choose_rate()
        self.choose_dice()

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

    exec(open("C:/Users/Alin/Desktop/arc1_pyqt/displayscript.py").read())  # includes all display functions


tags = {
    'top': ModTag(tag, "TestModule", None),
    'subtags': [
        ModTag(tag+"1", "Retention", TestModule.display_retention),
        ModTag(tag+"4", "Converge to State", None),
        ModTag(tag+"3", "FormFinder", TestModule.display_formfinder),
        ModTag(tag+"2", "Switch Seeker", TestModule.display_switchseeker),
        ModTag(tag+"5", "CurveTracer", TestModule.display_curve),
        ModTag(tag+"6", "ParameterFit", TestModule.display_parameterfit)
    ]
}

#tags = { 'top': ModTag(tag, "TestModule", TestModule.display_curve) }