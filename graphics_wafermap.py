self.setWindowTitle("Wafer Map Control")

self.timer = QTimer()
self.timer2 = QTimer()
self.timer2.start(200)

#input the map limits from the config file
self.table_cols = int(np.amax(config.x, axis=0))# column size of wafer map
self.table_rows = config.x.size #row size of wafer map
self.maxval_w_index = int(np.amax(config.w, axis=0))#max column offset from D1
#config.w shows the offset for each row#
#config.x shows the number of dies per each row#


#set table properties to accommodate the wafer map
layoutGrid=QVBoxLayout()
self.setLayout(layoutGrid)
self.tableWidget = QtWidgets.QTableWidget(self.table_rows, self.table_cols, self)
self.tableWidget.setGeometry(QtCore.QRect(10, 10, 600, 600))
self.tableWidget.setObjectName("tableWidget")
layoutGrid.addWidget(self.tableWidget) #add wafer map to a layout
self.tableWidget.setColumnCount(self.table_cols)#set wafer rows
self.tableWidget.setRowCount(self.table_rows)#and columns
self.tableWidget.setStyleSheet('''QTableView::item::selected {border: 2px solid black; selection-color : #7ECC49}''')



#build wafer map shape into the table
item = QtWidgets.QTableWidgetItem()
for i in range(self.table_rows):
    item = QtWidgets.QTableWidgetItem()
    self.tableWidget.setHorizontalHeaderItem(i, item)

for i in range(self.table_cols):
    item = QtWidgets.QTableWidgetItem()
    self.tableWidget.setColumnWidth(i, self.table_cols)



q = 1  # die number displayed
for i in range(self.table_rows):
    for j in range(self.table_cols):

        if j >= (self.maxval_w_index - config.w[i]) and j < ((self.maxval_w_index - config.w[i]) + config.x[i]):
            item = QtWidgets.QTableWidgetItem()

            if j % 2 == i % 2:
                #print red dies
                brush = QtGui.QBrush(QtGui.QColor(214, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                item.setBackground(brush)
                self.tableWidget.setItem(i, j, item)
                item.setText("%s" % q)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                config.dies_color.append(1)#1-red
                
            else:
                #print white dies
                item.setText("%s" % q)
                self.tableWidget.setItem(i, j, item)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                config.dies_color.append(0)#0-white
                
            q = q + 1

        else:
            #print grey area
            item = QtWidgets.QTableWidgetItem()
            brush = QtGui.QBrush(QtGui.QColor(214, 214, 214))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setBackground(brush)
            self.tableWidget.setItem(i, j, item)
            item.setText(" ")
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)

#add grey points for alignment

for i in range(config.row_align.size):

        item = QtWidgets.QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.tableWidget.setItem(config.row_align[i], config.col_align[i]+\
        (self.maxval_w_index-config.w[config.row_align[i]]), item)
        item.setText(" ")
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)

            
    
            
#print("dies color is: %s" %config.dies_color)



#####Table Subarray#######

#input the map limits from the config file
self.table_subcols = int(np.amax(config.sx, axis=0))# column size of wafer map
self.table_subrows = config.sx.size #row size of wafer map


#set table properties to accommodate the wafer map
#formLayout=QFormLayout()
#groupBox=QGroupBox("Groupbox")
#groupBox.setLayout(formLayout)
#self.scroll = QScrollArea()
#self.scroll.setWidget(groupBox)
#self.scroll.setWidgetResizable(True)
#self.scroll.setFixedHeight(100)
#self.scroll.setFixedWidth(100)

self.pbar=QProgressBar()
self.pbar.setValue(1)
self.time_est=QLabel('Time Estimated Remaining: ')


layout=QVBoxLayout()
#layoutGrid.addWidget(self.scroll)
layoutGrid.addWidget(self.pbar)
layoutGrid.addWidget(self.time_est)
self.setLayout(layoutGrid)

#self.subtableWidget = QtWidgets.QTableWidget(self.table_subrows, self.table_subcols, self)
#self.subtableWidget.setGeometry(QtCore.QRect(10, 10, 200, 200))
#self.subtableWidget.setObjectName("subtableWidget")
#self.vbox.addWidget(self.subtableWidget) #add wafer map to a layout
#self.subtableWidget.setColumnCount(self.table_subcols)#set wafer rows
#self.subtableWidget.setRowCount(self.table_subrows)#and columns

#build wafer map shape into the table
#item2 = QtWidgets.QTableWidgetItem()
#for i in range(self.table_subrows):
#    item2 = QtWidgets.QTableWidgetItem()
#    self.subtableWidget.setHorizontalHeaderItem(i, item2)

#    q=q+1


#for i in range(self.table_subcols):
#    item2 = QtWidgets.QTableWidgetItem()
#    self.subtableWidget.setColumnWidth(i, self.table_subcols)

#self.scroll.setWidget(self.subtableWidget)



######set other buttons layout#####
self.vbox = QVBoxLayout()
layoutGrid.addLayout(self.vbox)
self.hbox = QVBoxLayout()
layoutGrid.addLayout(self.hbox)

#self.dice_label=QLabel('Dies send are:', self)
#self.dice_label.setGeometry(30, 525, 1000, 20)

self.goto_dies = QtWidgets.QPushButton('Go ')
self.refresh=QtWidgets.QPushButton('Refresh')
self.btn_contact = QtWidgets.QPushButton('Contact')
self.set_reference=QtWidgets.QPushButton('Set Reference')
self.load_reference=QtWidgets.QPushButton('Load Reference')
self.pick_CB=QtWidgets.QRadioButton('Pick CB')
self.pick_SA=QtWidgets.QRadioButton('Pick SA')
self.pick_All=QtWidgets.QRadioButton('Pick All')
self.pick_All.setChecked(True)
self.position_label=QLabel("D: | S:")

self.vbox.addWidget(self.goto_dies)
self.vbox.addWidget(self.refresh)
self.vbox.addWidget(self.btn_contact)
self.vbox.addWidget(self.set_reference)
self.vbox.addWidget(self.load_reference)
self.hbox.addWidget(self.pick_CB)
self.hbox.addWidget(self.pick_SA)
self.hbox.addWidget(self.pick_All)
self.vbox.addWidget(self.position_label)

self.setLayout(layoutGrid)