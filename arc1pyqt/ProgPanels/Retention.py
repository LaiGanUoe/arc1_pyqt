####################################

# (c) Radu Berdan
# ArC Instruments Ltd.

#myfolder
# This code is licensed under GNU v3 license (see LICENSE.txt for details)

####################################

from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import time
import numpy as np
import pyqtgraph as pg

from arc1pyqt import Graphics
from arc1pyqt import state
HW = state.hardware
APP = state.app
CB = state.crossbar
from arc1pyqt.Globals import styles, fonts
from arc1pyqt.modutils import BaseThreadWrapper, BaseProgPanel, \
        makeDeviceList, ModTag

from arc1pyqt.database_methods import inserting_data_into_database_singleRead_Retention_setParameters
from arc1pyqt.database_methods import inserting_data_into_database_allOrRangeRead_Retention_setParameters
from arc1pyqt.database_methods import inserting_data_into_database_allFunction_experimentalDetail
from arc1pyqt.database_methods import inserting_data_into_database_setFirstLocation

tag = "RT"

#1: compensate for series resistance, 0:do not compesate
Rs_compensation=1
Rs_top=50
Rs_bottom=50
subdie=9

current_directory = os.getcwd()

#f = open(os.path.join(current_directory, "target_subdie.csv") , "w")

#we measure Rs from largest width and largest length, bottom-left elecrode on microscope
#starting with devices with wordline: w1, w2, w3,...wn or length L1, L2, L3, etc
#Therefore length coefficient (L_ratio) is ratio between Li/Lmax, L1/Lmax, L2/Lmax etc.
L_ratios=np.array([0.159090909,0.215909091,0.272727273,0.329545455,0.272727273,0.443181818,0.386363636,0.556818182,\
                    0.5,0.674242424,0.613636364,0.784090909,0.727272727,0.897727273,0.840909091,1,1,\
                    0.954545455,0.897727273,0.840909091,0.784090909,0.727272727,0.674242424,0.613636364,\
                    0.556818182,0.5,0.443181818,0.386363636,0.329545455,0.272727273,0.215909091,1])


#width ratio of electrode for every device size starting from S1, S2, S3...etc. 
#In order, device sizes are:  1, 2, 5, 10, 20, 30, 40, 50, 60um
#in this array the width ratio (or width coefficient) is S1/S9, S1/S8, S1/S7...etc. 
W_ratios=np.array([0.016666667,0.02,0.025,0.033333333,0.05,0.1,0.2,0.5,1])



class ThreadWrapper(BaseThreadWrapper):

    def __init__(self, deviceList, every, duration, Vread):
        super().__init__()
        self.deviceList=deviceList
        self.every=every
        self.duration=duration
        self.Vread=Vread


    #comensate for series resistance     
    def uniform_reading(self, w, b, Vin, Rs_bottom, Rs_top, subdie):
    
        
        #extract the correct L and W ratios accoring to the w/b lines
        global L_ratios, W_ratios
        
        L_ratio = L_ratios[w-1]
        W_ratio = W_ratios[subdie-1]
        
        print("Length %s has ratio: %s"%(w, L_ratio))
        print("Width %s has ratio: %s"%(subdie, W_ratio))
        
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
        
        print("Vm not calibrated is: %s" %Vm)
        #print("Rm not calibrated is: %s" %Rm)
        ##########find correction Vadjust to be equal with Vd###########
        
        #adjust Itot to have Vm drop at memeristor the quantity we want
        #here I can try a polynomial fit instead to reduce error
        I_adjust = Vd / Rm
        
        #adjust input voltage to provide Vd across memristor
        V_adjust = I_adjust * R_tot
        
        #take V_adjust as the new reading voltage
        self.Vread=V_adjust     
        #apply reading again with the calibrated voltage
        R_tot_new = HW.ArC.read_one(w, b)
        #restore Vread to its original value
        self.Vread = Vd
        
        #find Itot_new of the adjusted Voltage
        I_tot_new = V_adjust / R_tot_new
        
        #find the corrected memristor resistance without Rs for the new voltage
        Rm_new = R_tot - (Rs_bottom*L_ratio*W_ratio)- (Rs_top*L_ratio*W_ratio)
        
        #find corrected memristor drop voltage Vm
        Vm_new = I_tot_new * Rm_new
        
        #if Vm_new is not equal to Vd as intended, perform an improved calculus
        #either by error subtraction or polynomial fit
        print("Vm new is: %s" %Vm_new)
        print("Rm new is: %s" %Rm_new)
        
        if (R_tot_new and Vm_new) is not None:
        # Perform calculations with R_tot_new
            
            #outputs memristor resistance at calibrated voltage and without series resistance
            #outputs memristor voltage drop without series resistance influence
            return float(Rm_new), float(Vm_new)
    
    def uniformity_pulsing(self, w, b, Vin, pw, Rs_bottom, Rs_top, subdie, compensation):
        
        #if Rs compensated, v takes the compensated value
        if compensation==1:
            Rm_read_new, Vm_read_new = self.uniform_reading(w, b, self.Vread, Rs_top, Rs_bottom, subdie)
            v=(v * Vm_read_new) / self.Vread
                
            #print("Voltage applied: %s"%v)
            
        #apply the pulse with input voltage v     
        HW.ArC.pulseread_one(w, b, v, pw)
        
        #read current resistance at read voltage 
        if compensation==1:
            
            Rm_read_new2, Vm_read_new2= self.uniform_reading(w, b, self.Vread, Rs_top, Rs_bottom, subdie)
        else:
            Rm_read_new2 = HW.ArC.read_one(w, b)
        
        #return compensated writing voltage on electrodes
        #return comensated resistance on memristor after forming pulse
        return v, Rm_read_new2
    
    @BaseThreadWrapper.runner    
    def run(self):
        # new
        storeLocation = 0
        arrayForStoreData = []  # Array to store the final result
        start_values = []  # Array to store (w, b, start_for_wb)
        end_values = []  # Array to store (w, b, end_for_wb)
        db_file = 'Database.db'
        # new

        self.disableInterface.emit(True)
        global tag, Rs_compensation, Rs_top, Rs_bottom, subdie

        start=time.time()
        print(self.deviceList)
        #Initial read
        for device in self.deviceList:
            w=device[0]
            b=device[1]
            self.highlight.emit(w,b)

            # new
            #get the start position of the cycle
            start_for_wb = len(CB.history[w][b])
            print("the local position of the wordline and bitline for start")
            print(w, b)
            print(start_for_wb)
            start_values.append((w, b, start_for_wb))
            # new

         #if series resistance compensation is off
            if Rs_compensation==0:
                Rm_new = HW.ArC.read_one(w, b)
            else:
                Rm_new, Vm_new = self.uniform_reading(w, b, self.Vread, Rs_top, Rs_bottom, subdie)
        
            Rm_new = HW.ArC.read_one(w, b)
            tag_ = tag+"_s"
            self.sendData.emit(w,b,Rm_new,self.Vread,0,tag_)
            self.displayData.emit()
            
        #core read
        while True:
            start_op=time.time()

            for device in self.deviceList:
                w=device[0]
                b=device[1]
                self.highlight.emit(w,b)

                #if series resistance compensation is off
                if Rs_compensation==0:
                    Rm_new = HW.ArC.read_one(w, b)

                else:
                    Rm_new, Vm_new = self.uniform_reading(w, b, self.Vread, 10, 10, 1)
         
                tag_=tag+"_"+ str(time.time())
                self.sendData.emit(w,b,Rm_new,Vm_new,0,tag_)
                #print(self.Vread)
                self.displayData.emit()

            end=time.time()
            time.sleep(self.every-(end-start_op))
            end=time.time()

            if (end-start)>self.duration:
                break

        #Final read
        for device in self.deviceList:
            w=device[0]
            b=device[1]
            self.highlight.emit(w,b)

            # new
            # due to some reason, the end is always one bigger than the end number
            end_for_wb = len(CB.history[w][b]) - 1
            print("the local position of the wordline and bitline for end")
            print(w, b)
            print(end_for_wb)
            end_values.append((w, b, end_for_wb))
            # new

            Mnow = HW.ArC.read_one(w, b)
            tag_=tag+"_e"
            self.sendData.emit(w,b,Mnow,self.Vread,0,tag_)
            self.displayData.emit()
            self.updateTree.emit(w,b)


        # new
        # Combine (w, b, start_for_wb) and (w, b, end_for_wb) into (w, b, start, end)
        for (w1, b1, start_for_wb) in start_values:
            for (w2, b2, end_for_wb) in end_values:
                if w1 == w2 and b1 == b2:  # Ensure w and b match
                    arrayForStoreData.append((w1, b1, start_for_wb, end_for_wb))

        print(arrayForStoreData)


        for w, b, start_for_wb, end_for_wb in arrayForStoreData:
            print("Lai Gan")
            wafer = '6F01'
            insulator = 'TiOx'
            cross_sectional_area = 'SA10'
            die = 'D119'

            #for the whole parameters that are moved to the newest position
            if (storeLocation == 1):
                inserting_data_into_database_allOrRangeRead_Retention_setParameters(db_file, wafer, insulator,
                                                                                      cross_sectional_area, die, w, b)
                print("this is the allorRangeRead set parameters")
            else:# for the start location
                inserting_data_into_database_setFirstLocation(db_file, wafer, die, w, b)
                print("this is the set first location")
            #this is not the first time set the location, so storeLocation = 1
            storeLocation = 1

            # Inner loop, modifying start_for_wb and end_for_wb
            for i in range(start_for_wb, end_for_wb + 2):
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

        print("this is the allFunction_experimentalDetail")

        print("the end of the whole cycles-------------------------------")
        # new


class Retention(BaseProgPanel):

    def __init__(self, short=False):
        super().__init__(\
                title='Retention', \
                description='Measure resistive states for '
                            'extended periods of time.', \
                short=short)
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

        leftLabels=['Read every:', \
                    'Read for:']
        leftInit=  ['1',\
                    '1']

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
        gridLayout.addWidget(self.every_dropDown,0,3)
        gridLayout.addWidget(self.leftEdits[1],1,1)
        gridLayout.addWidget(self.duration_dropDown,1,3)

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

    def programDevs(self, devs):
        time_mag=float(self.leftEdits[0].text())
        unit=float(self.multiply[self.every_dropDown.currentIndex()])
        every=time_mag*unit
        print("This is the important information for left 0:" + str(time_mag),  str(unit), str(every))

        time_mag=float(self.leftEdits[1].text())
        unit=float(self.multiply[self.duration_dropDown.currentIndex()])
        duration=time_mag*unit
        # new
        print("set parameter")
        db_file = 'Database.db'
        insulator = 'TiOx'
        cross_sectional_area = 'SA10'

        # retention set parameters
        inserting_data_into_database_singleRead_Retention_setParameters(
            db_file, insulator, cross_sectional_area, float(self.leftEdits[0].text()),
            float(self.multiply[self.every_dropDown.currentIndex()]), float(self.leftEdits[1].text()),
            float(self.multiply[self.duration_dropDown.currentIndex()])
        )
        # new

        print("This is the important information for left 1:" + str(time_mag),  str(unit), str(duration))

        wrapper = ThreadWrapper(devs, every, duration, HW.conf.Vread)
        self.execute(wrapper, wrapper.run)

    def programOne(self):
        self.programDevs([[CB.word, CB.bit]])

    def programRange(self):
        rangeDev = makeDeviceList(True)
        self.programDevs(rangeDev)

    def programAll(self):
        rangeDev = makeDeviceList(False)
        self.programDevs(rangeDev)

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


tags = { 'top': ModTag(tag, "Retention", Retention.display) }
