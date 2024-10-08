from enum import IntEnum
from dataclasses import dataclass
import numpy as np
from PyQt5.QtCore import QMutex, QWaitCondition
from .instrument import HWConfig


class DisplayMode(IntEnum):
    RESISTANCE = 0
    CONDUCTANCE = 1
    CURRENT = 2
    ABS_CURRENT = 3


@dataclass
class Crossbar:
    word = 1
    bit = 1
    limits = { 'words': (1, 1), 'bits': (1, 1) }
    history = [[[] for bit in range(33)] for word in range(33)]
    checkSA = False
    customArray = []
    startTags = {}

    def append(self, w, b, *args):
        tag = args[3]
        startIdx = -1
        if tag.endswith('_s'):
            if len(self.history[w][b]) <= 0:
                start = 0
            else:
                start = len(self.history[w][b])-1
            self.addStartTag(w, b, start)
        if tag.endswith('_e'):
            key = '%s,%s' % (w,b)
            if key in self.startTags.keys() and len(self.startTags[key]) > 0:
                startIdx = self.startTags[key].pop()
        self.history[w][b].append([*args, startIdx])

    def addStartTag(self, w, b, idx):
        key = '%s,%s' % (w, b)
        if key not in self.startTags.keys():
            self.startTags[key] = [idx]
        else:
            # So if everything is working properly `self.startTags` should hold
            # **at most** 1 item. If for some reason there are startTags already
            # available when we try to add a new one it means that one of the
            # previous startTags was never closed which will lead to data
            # corruption. To save as much data as possible we will traverse the
            # data history backwards to find out the last intermediate tag
            # (which either ends or includes a `_i`) and change it to an end
            # tag. This will properly delimit the previous block making what's
            # left of that data available to the user.
            if len(self.startTags[key]) > 0:
                print("orphan start tag encountered when adding new start tag")
                # go backwards in history
                for (revidx, entry) in enumerate(reversed(self.history[w][b])):
                    # and find the last intermediate tag (first backwards)
                    if entry[3].endswith('_i') or entry[3].find('_i_') > 0:
                        print(" entry       ", entry)
                        # store the index of that tag
                        revidx = len(self.history[w][b]) - revidx -1
                        # take only the first part of the tag, so for instance
                        # if tag is 'XXX_i' -> 'XXX'
                        # if tag is 'XXX_i_y' -> 'XXX'
                        # this is always first.
                        tag = entry[3].split('_')[0]
                        # correct the intermediate tag into an end tag
                        self.history[w][b][revidx][3] = '%s_e' % tag
                        # and put that stray start index into its proper place
                        # emptying the startTag stack
                        self.history[w][b][revidx][-1] = self.startTags[key].pop()
                        print(" corrected to", self.history[w][b][revidx])

                        # Unfortunately altering history after having been
                        # communicated to the interface means that the previous
                        # entries in the history tree are now invalid. That's
                        # because we can only realise there is a problem with a
                        # given data block only AFTER we cross into the next one
                        # which is already too late. This signal notifies the
                        # history tree to reload that specific (w, b) combination.
                        # As you can understand in a log file with many errors this
                        # will take a while. There is probably a better way to do
                        # this by removing the previous entry from the tree and
                        # reading only those too, however this requires much
                        # working around specific cases for a situation that should
                        # not happen *that* frequently anyway.
                        functions.historyTreeAntenna.rebuildTreeTopLevel.emit(w, b)
                        break

            self.startTags[key].append(idx)


@dataclass
class Application:
    modules = { }
    sessionName = 'Package 1'
    workingDirectory = []
    saveFileName = []
    scalingFactor = 1.0
    displayPoints = 100
    globalDisable = False
    displayMode = DisplayMode.RESISTANCE
    mutex = QMutex()
    waitCondition = QWaitCondition()
    
    #position variables
    current_x_D = '-'
    current_y_D = '-'
    current_x_s = '-'
    current_y_s = '-'
    Dice_no=0
    Subdice_no=0
    check_contact=0 #0-separation, 1-contact, -1 alignment, overtravel, etc.
    
    #function chain parameters
    repeat_fct=0
    repeat_chain=0
    time_est=0
    time_start=0


    

    #switch seeker inputs
    switch_seek1=0
    switch_seek2=0
    switch_seek3=0
    switch_seek4=0
    switch_seek5=0
    switch_seek6=0
    switch_seek7=0
    switch_seek8=0
    switch_seek9=0
    switch_seek10=0
    switch_seek_combo1=0
    switch_seek_combo2=0
    job_ss=0
    skipStageI=0

    #form finder inputs
    polarity=0
    pmode=0
    form_finder1=0
    form_finder2=0
    form_finder3=0
    form_finder4=0
    form_finder5=0
    form_finder6=0
    form_finder7=0
    form_finder8=0
    form_finder9=0
    form_finder10=0
    form_finder_combo1 = 0
    form_finder_combo2 = 0
    job_ff=0
    pSR=0
    CB_form_finder1=0
    CB_form_finder2=0

    #converge to state inputs
    converge1=0
    converge_combo1=0
    converge3=0
    converge4=0
    converge5=0
    converge6=0
    converge7=0
    converge8=0
    converge9=0
    converge10=0
    converge11=0
    converge12=0

    #Curve Tracer inputs
    curvetracer1 =0
    curvetracer2 =0
    curvetracer3 =0
    curvetracer4 =0
    curvetracer5 =0
    curvetracer6 =0
    curvetracer7 =0
    curvetracer8 =0
    curvetracer9 =0
    curvetracer10 =0
    curvetracer_combo1 =0
    curvetracer_combo2 =0
    CB_curvetracer1 =0
    CB_curvetracer2 =False
    CSp=0
    CSn=0
    totalCycles=0
    job_ct = "201"

    #parameterFit inputs
    parameterfit1=0
    parameterfit2=0
    parameterfit3=0
    parameterfit4=0
    parameterfit5=0
    parameterfit6=0
    parameterfit7=0
    parameterfit8=0
    parameterfit9=0
    parameterfit10=0
    
    #RILForming inputs
    RILForming1=10 #max voltage
    RILForming2=10 #max cycles
    RILForming3=120 #step voltage
    RILForming4=0.001 #pulse width
    RILForming5=0.99 #gamma
 
    #uniformity inputs
    uniformity1=1 #no resistance bins to be averaged for uniformity
    CB_uniformity2=1#series resistance compensation :1-yes, 0-no

    #uniform_reading() inputs
    CB_uniformity3=0
    Rs_top=1# value in ohm for top electrode series resistance (ask Alin or measure)
    Rs_bottom=1 # value in ohm for bottom electrode series resistance (ask Alin or measure)
    
@dataclass
class Hardware:
    conf = HWConfig(words=32, bits=32, cycles=50, readmode=2, \
            sessionmode=0, sneakpath=1, Vread=0.5)
    ArC = None


# state variables
app = Application()
crossbar = Crossbar()
hardware = Hardware()

from .Globals import functions
