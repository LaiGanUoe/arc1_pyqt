@staticmethod
def display_curve(w, b, raw, parent=None):

    resistance = []
    voltage = []
    current = []
    abs_current = []

    # Find nr of cycles
    lineNr = 1
    totalCycles = 0
    resistance.append([])
    voltage.append([])
    current.append([])
    abs_current.append([])

    resistance[totalCycles].append(raw[0][0])
    voltage[totalCycles].append(raw[0][1])
    current[totalCycles].append(raw[0][1] / raw[lineNr][0])
    abs_current[totalCycles].append(abs(current[totalCycles][-1]))

    # take all data lines without the first and last one (which are _s and
    # _e)
    while lineNr < len(raw) - 1:
        currentRunTag = raw[lineNr][3]

        while (currentRunTag == raw[lineNr][3]):
            resistance[totalCycles].append(raw[lineNr][0])
            voltage[totalCycles].append(raw[lineNr][1])
            current[totalCycles].append(raw[lineNr][1] / raw[lineNr][0])
            abs_current[totalCycles].append(abs(current[totalCycles][-1]))

            lineNr += 1
            if lineNr == len(raw):
                break
        totalCycles += 1
        resistance.append([])
        voltage.append([])
        current.append([])
        abs_current.append([])

    resistance[totalCycles - 1].append(raw[-1][0])
    voltage[totalCycles - 1].append(raw[-1][1])
    current[totalCycles - 1].append(raw[-1][1] / raw[-1][0])
    abs_current[totalCycles - 1].append(abs(current[totalCycles - 1][-1]))

    # setup display
    resultWindow = QtWidgets.QWidget()
    resultWindow.setGeometry(100, 100, int(1000 * APP.scalingFactor), 400)
    resultWindow.setWindowTitle("Curve Tracer: W=" + str(w) + " | B=" + str(b))
    resultWindow.setWindowIcon(Graphics.getIcon('appicon'))
    resultWindow.show()

    view = pg.GraphicsLayoutWidget()

    label_style = {'color': '#000000', 'font-size': '10pt'}

    plot_abs = view.addPlot()
    plot_abs.getAxis('left').setLabel('Current', units='A', **label_style)
    plot_abs.getAxis('bottom').setLabel('Voltage', units='V', **label_style)
    plot_abs.setLogMode(False, True)
    plot_abs.getAxis('left').setGrid(50)
    plot_abs.getAxis('bottom').setGrid(50)

    # go to next row and add the next plot
    view.nextColumn()

    plot_IV = view.addPlot()
    plot_IV.addLegend()
    plot_IV.getAxis('left').setLabel('Current', units='A', **label_style)
    plot_IV.getAxis('bottom').setLabel('Voltage', units='V', **label_style)
    plot_IV.getAxis('left').setGrid(50)
    plot_IV.getAxis('bottom').setGrid(50)

    # go to next row and add the next plot
    view.nextColumn()

    plot_R = view.addPlot()
    plot_R.getAxis('left').setLabel('Resistance', units='Ohms',
                                    **label_style)
    plot_R.getAxis('bottom').setLabel('Voltage', units='V', **label_style)
    plot_R.setLogMode(False, True)
    plot_R.getAxis('left').setGrid(50)
    plot_R.getAxis('bottom').setGrid(50)

    resLayout = QtWidgets.QVBoxLayout()
    resLayout.addWidget(view)
    resLayout.setContentsMargins(0, 0, 0, 0)

    resultWindow.setLayout(resLayout)

    # setup range for resistance plot
    maxRes_arr = []
    minRes_arr = []

    for cycle in range(1, totalCycles + 1):
        maxRes_arr.append(max(resistance[cycle - 1]))
        minRes_arr.append(min(resistance[cycle - 1]))

    maxRes = max(maxRes_arr)
    minRes = max(minRes_arr)

    for cycle in range(1, totalCycles + 1):
        aux1 = plot_abs.plot(pen=(cycle, totalCycles), symbolPen=None,
                             symbolBrush=(cycle, totalCycles), symbol='s', symbolSize=5,
                             pxMode=True, name='Cycle ' + str(cycle))
        aux1.setData(np.asarray(voltage[cycle - 1]),
                     np.asarray(abs_current[cycle - 1]))

        aux2 = plot_IV.plot(pen=(cycle, totalCycles), symbolPen=None,
                            symbolBrush=(cycle, totalCycles), symbol='s', symbolSize=5,
                            pxMode=True, name='Cycle ' + str(cycle))
        aux2.setData(np.asarray(voltage[cycle - 1]),
                     np.asarray(current[cycle - 1]))

        aux3 = plot_R.plot(pen=(cycle, totalCycles), symbolPen=None,
                           symbolBrush=(cycle, totalCycles), symbol='s', symbolSize=5,
                           pxMode=True, name='Cycle ' + str(cycle))
        aux3.setData(np.asarray(voltage[cycle - 1]),
                     np.asarray(resistance[cycle - 1]))

    plot_R.setYRange(np.log10(_min_without_inf(resistance, np.inf)),
                     np.log10(_max_without_inf(resistance, np.inf)))
    plot_abs.setYRange(np.log10(_min_without_inf(abs_current, 0.0)),
                       np.log10(_max_without_inf(abs_current, 0.0)))

    resultWindow.update()

    return resultWindow


@staticmethod
def display_retention(w, b, data, parent=None):
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
                                        symbolBrush=(0, 0, 255), symbol='s', symbolSize=5, pxMode=True)
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
    resultWindow.setGeometry(100, 100, int(1000 * APP.scalingFactor), 400)
    resultWindow.setWindowTitle("Retention: W=" + str(w) + " | B=" + str(b))
    resultWindow.setWindowIcon(Graphics.getIcon('appicon'))
    resultWindow.show()
    resultWindow.setLayout(resLayout)

    retentionPlot.setYRange(min(m) / 1.5, max(m) * 1.5)
    retentionCurve.setData(np.asarray(timePoints), np.asarray(m))
    resultWindow.update()

    return resultWindow

@staticmethod
def display_formfinder(w, b, data, parent=None):

    siFormat = pg.siFormat

    def _updateLinkedPlots(base, overlay):
        overlay.setGeometry(base.vb.sceneBoundingRect())
        overlay.linkedViewChanged(base.vb, overlay.XAxis)

    dialog = QtWidgets.QDialog(parent)

    containerLayout = QtWidgets.QVBoxLayout()
    dialog.setWindowTitle("FormFinder W=%d | B=%d" % (w, b))

    R = np.empty(len(data) - 1)
    V = np.empty(len(data) - 1)
    P = np.empty(len(data) - 1)
    for (i, line) in enumerate(data[1:]):
        R[i] = line[0]
        V[i] = line[1]
        P[i] = line[2]

    Vidx = np.repeat(np.arange(0, len(R)), 2)

    gv = pg.GraphicsLayoutWidget(show=False)
    Rplot = gv.addPlot(name="resistance")
    Rplot.plot(R, pen=pg.mkPen('r', width=1), symbolPen=None,
               symbolBrush=(255, 0, 0), symbolSize=5, symbol='s')
    Rplot.showAxis('right')
    Rplot.getAxis('left').setLabel('Resistance', units='Ω')
    Rplot.getAxis('left').setStyle(tickTextWidth=40, autoExpandTextSpace=False)
    Rplot.getAxis('left').setGrid(50)
    Rplot.getAxis('bottom').setGrid(50)
    Rplot.getAxis('right').setWidth(40)
    Rplot.getAxis('right').setStyle(showValues=False)
    Rplot.getAxis('bottom').setLabel('Pulse')

    gv.nextRow()

    Vplot = gv.addPlot(name="voltage")
    Vplot.plot(V, pen=None, symbolPen=None, symbolBrush=(0, 0, 255),
               symbolSize=5, symbol='s', connect='pairs')
    Vplot.plot(Vidx, np.dstack((np.zeros(V.shape[0]), V)).flatten(),
               pen='b', symbolPen=None, symbolBrush=None, connect='pairs')
    Vplot.getAxis('left').setLabel('Voltage', units='V')
    Vplot.getAxis('left').setGrid(50)
    Vplot.getAxis('bottom').setGrid(50)
    Vplot.getAxis('left').setStyle(tickTextWidth=40, autoExpandTextSpace=False)
    Vplot.getAxis('bottom').setLabel('Pulse')
    Vplot.setXLink("resistance")

    Pview = pg.ViewBox()
    Vplot.scene().addItem(Pview)
    Vplot.showAxis('right')
    Vplot.getAxis('right').setLabel('Pulse width', units='s')
    Pview.setXLink(Vplot)
    Vplot.getAxis('right').linkToView(Pview)
    Pview.enableAutoRange(Pview.XAxis, True)
    Pview.enableAutoRange(Pview.YAxis, True)

    _updateLinkedPlots(Vplot, Pview)
    Vplot.vb.sigResized.connect(partial(_updateLinkedPlots, base=Vplot, \
                                        overlay=Pview))

    Pplot = pg.ScatterPlotItem(symbol='+')
    Pplot.setPen(pg.mkPen(color=QtGui.QColor(QtCore.Qt.darkGreen), \
                                 width=1))
    Pplot.setBrush(pg.mkBrush(color=QtGui.QColor(QtCore.Qt.darkGreen)))
    Pplot.setData(np.arange(0, len(data) - 1), P)
    Pview.addItem(Pplot)

    containerLayout.addWidget(gv)

    saveButton = QtWidgets.QPushButton("Export data")
    saveCb = partial(functions.writeDelimitedData, np.column_stack((V, R, P)))
    saveButton.clicked.connect(partial(functions.saveFuncToFilename, saveCb,
                                       "Save data to...", parent))

    bottomLayout = QtWidgets.QHBoxLayout()
    labelText = 'Final resistance: %s recorded after a %s %s pulse' % \
                (siFormat(R[-1], suffix='Ω'), siFormat(V[-1], suffix='V'), \
                 siFormat(P[-1], suffix='s'))
    bottomLayout.addWidget(QtWidgets.QLabel(labelText))
    bottomLayout.addItem(QtWidgets.QSpacerItem(40, 10,
                                               QtWidgets.QSizePolicy.Expanding))
    bottomLayout.addWidget(saveButton)

    containerLayout.addItem(bottomLayout)

    dialog.setLayout(containerLayout)

    return dialog

@staticmethod
def display_switchseeker(w, b, raw, parent=None):

    # Initialisations
    pulseNr = 0
    deltaR = []
    initR = []
    ampl = []
    Rs = []

    # Holds under and overshoot voltages
    over = []
    under = []
    offshoots = [] # holds both in order

    # holds maximum normalised resistance offset during a train of reads
    max_dR = 0

    # Find the pulse amplitudes and the resistance (averaged over the read
    # sequence) after each pulse train
    index = 0

    while index < len(raw):

        # if this is the first read pulse of a read sequence:
        if index < len(raw) and raw[index][2] == 0:

            # record the start index
            start_index = index
            # initialise average resistance during a read run accumulator
            readAvgRun = 0
            # counts nr of reads
            idx = 0

            # If the line contains 0 amplitude and 0 width, then we're
            # entering a read run
            while index < len(raw) and raw[index][2] == 0:

                # increment the counter
                idx += 1
                # add to accumulator
                readAvgRun += raw[index][0]
                # increment the global index as we're advancing through the
                # pulse run
                index += 1
                # if the index exceeded the lenght of the run, exit
                if index > len(raw) - 1:
                    break

            # When we exit the while loop we are at the end of the reading
            # run
            readAvgRun = readAvgRun/idx

            # append with this resistance
            Rs.append(readAvgRun)

            # find the maximum deviation from the average read during a
            # read sequence (helps future plotting of the confidence bar)
            for i in range(idx):

                # maybe not the best way to do this but still
                if abs(raw[start_index+i][0] - readAvgRun)/readAvgRun > max_dR:
                    max_dR = abs(raw[start_index+i][0] - readAvgRun)/readAvgRun

        # if both amplitude and pw are non-zero, we are in a pulsing run
        # if this is the first  pulse of a write sequence:
        if index<len(raw) and raw[index][1] != 0 and raw[index][2] != 0:
            while index<len(raw) and raw[index][1] != 0 and raw[index][2] != 0:

                # increment the index
                index += 1
                # if the index exceeded the length of the run, exit
                if index == len(raw) - 1:
                    break

            # record the pulse voltage at the end
            ampl.append(raw[index-1][1])


    # Record initial resistances and delta R.
    for i in range(len(ampl)):
        initR.append(Rs[i])
        deltaR.append((Rs[i+1] - Rs[i])/Rs[i])

    confX = [0, 0]
    confY = [-max_dR, max_dR]

    # setup display
    resultWindow = QtWidgets.QWidget()
    resultWindow.setGeometry(100, 100, int(1000*APP.scalingFactor), 500)
    resultWindow.setWindowTitle("SwitchSeeker: W="+ str(w) + " | B=" + str(b))
    resultWindow.setWindowIcon(Graphics.getIcon('appicon'))
    resultWindow.show()

    view = pg.GraphicsLayoutWidget()

    labelStyle = {'color': '#000000', 'font-size': '10pt'}

    japanPlot = view.addPlot()
    japanCurve = japanPlot.plot(pen=None, symbolPen=None,
            symbolBrush=(0,0,255), symbol='s', symbolSize=5, pxMode=True)
    japanPlot.getAxis('left').setLabel('dM/M0', **labelStyle)
    japanPlot.getAxis('bottom').setLabel('Voltage', units='V', **labelStyle)
    japanPlot.getAxis('left').setGrid(50)
    japanPlot.getAxis('bottom').setGrid(50)

    resLayout = QtWidgets.QHBoxLayout()
    resLayout.addWidget(view)
    resLayout.setContentsMargins(0, 0, 0, 0)

    resultWindow.setLayout(resLayout)

    japanCurve.setData(np.asarray(ampl), np.asarray(deltaR))
    resultWindow.update()

    return resultWindow

@staticmethod
def display_parameterfit(w, b, data, parent=None):
    dialog = FitDialog(w, b, data, parent)

    return dialog

def _max_without_inf(lst, exclude):
    maxim = 0
    for value in lst:
        if type(value) == list:
            value = _max_without_inf(value, exclude)
            if value > maxim:
                maxim = value
        else:
            if value > maxim and value != exclude:
                maxim = value

    return maxim


def _min_without_inf(lst, exclude):
    maxim = 1e100
    for value in lst:
        if type(value) == list:
            value = _min_without_inf(value, exclude)
            if value < maxim:
                maxim = value
        else:
            if value < maxim and value != exclude:
                maxim = value

    return maxim
    
@staticmethod
def display_RILForming(w, b, raw, parent=None):
    pass