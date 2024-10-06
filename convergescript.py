ss_x=240
ss_y=35
offset_ss_x=0
offset_ss_y=20
offset_ssl_x=0
offset_ssl_y=18

self.converge1 = QtWidgets.QLineEdit(self)
self.converge1.setText("5000")
self.converge1.setGeometry(ss_x, offset_ss_y+ss_y, 60, 20)
self.converge1_label=QtWidgets.QLabel('Target R', self)
self.converge1_label.setGeometry(ss_x, offset_ssl_y+ss_y-15, 100, 20)
self.converge1.hide()
self.converge1_label.hide()

self.converge_combo1 = QtWidgets.QComboBox(self)
self.converge_combo1.addItem('Positive', 1)
self.converge_combo1.addItem('Negative', -1)
self.converge_combo1.setGeometry(ss_x, offset_ss_y+ss_y*2, 60, 20)
self.converge_combo1_label=QtWidgets.QLabel('Initial polarity', self)
self.converge_combo1_label.setGeometry(ss_x, offset_ssl_y+(ss_y*2)-15, 100, 20)
self.converge_combo1.hide()
self.converge_combo1_label.hide()

self.converge3 = QtWidgets.QLineEdit(self)
self.converge3.setText("0.1")
self.converge3.setGeometry(ss_x, offset_ss_y+ss_y*3, 60, 20)
self.converge3_label=QtWidgets.QLabel('PW min (ms)', self)
self.converge3_label.setGeometry(ss_x, offset_ssl_y+(ss_y*3)-15, 100, 20)
self.converge3.hide()
self.converge3_label.hide()

self.converge4 = QtWidgets.QLineEdit(self)
self.converge4.setText("100")
self.converge4.setGeometry(ss_x, offset_ss_y+ss_y*4, 60, 20)
self.converge4_label=QtWidgets.QLabel('PW step (%)', self)
self.converge4_label.setGeometry(ss_x, offset_ssl_y+(ss_y*4)-15, 100, 20)
self.converge4.hide()
self.converge4_label.hide()

self.converge5 = QtWidgets.QLineEdit(self)
self.converge5.setText("0.1")
self.converge5.setGeometry(ss_x, offset_ss_y+ss_y*5, 60, 20)
self.converge5_label=QtWidgets.QLabel('PW max (ms)', self)
self.converge5_label.setGeometry(ss_x, offset_ssl_y+(ss_y*5)-15, 100, 20)
self.converge5.hide()
self.converge5_label.hide()

self.converge6 = QtWidgets.QLineEdit(self)
self.converge6.setText("1")
self.converge6.setGeometry(ss_x, offset_ss_y+ss_y*6, 60, 20)
self.converge6_label=QtWidgets.QLabel('Interpulse (ms)', self)
self.converge6_label.setGeometry(ss_x, offset_ssl_y+(ss_y*6)-15, 100, 20)
self.converge6.hide()
self.converge6_label.hide()

self.converge7 = QtWidgets.QLineEdit(self)
self.converge7.setText("5")
self.converge7.setGeometry(ss_x, offset_ss_y+ss_y*7, 60, 20)
self.converge7_label=QtWidgets.QLabel('Rt tolerance (%)', self)
self.converge7_label.setGeometry(ss_x, offset_ssl_y+(ss_y*7)-15, 100, 20)
self.converge7.hide()
self.converge7_label.hide()

self.converge8 = QtWidgets.QLineEdit(self)
self.converge8.setText("10")
self.converge8.setGeometry(ss_x, offset_ss_y+ss_y*8, 60, 20)
self.converge8_label=QtWidgets.QLabel('Ro tolerance (%)', self)
self.converge8_label.setGeometry(ss_x, offset_ssl_y+(ss_y*8)-15, 100, 20)
self.converge8.hide()
self.converge8_label.hide()

self.converge9 = QtWidgets.QLineEdit(self)
self.converge9.setText("0.5")
self.converge9.setGeometry(ss_x, offset_ss_y+ss_y*9, 60, 20)
self.converge9_label=QtWidgets.QLabel('Voltage min (V)', self)
self.converge9_label.setGeometry(ss_x, offset_ssl_y+(ss_y*9)-15, 100, 20)
self.converge9.hide()
self.converge9_label.hide()

self.converge10 = QtWidgets.QLineEdit(self)
self.converge10.setText("0.1")
self.converge10.setGeometry(ss_x, offset_ss_y+ss_y*10, 60, 20)
self.converge10_label=QtWidgets.QLabel('Voltage step (V)', self)
self.converge10_label.setGeometry(ss_x, offset_ssl_y+(ss_y*10)-15, 100, 20)
self.converge10.hide()
self.converge10_label.hide()

self.converge11=QtWidgets.QLineEdit(self)
self.converge11.setText("2.0")
self.converge11.setGeometry(ss_x+110, offset_ss_y+ss_y, 60, 20)
self.converge11_label=QtWidgets.QLabel('Voltage max (V)', self)
self.converge11_label.setGeometry(ss_x+110, offset_ss_y+ss_y-17, 100, 20)
self.converge11.hide()
self.converge11_label.hide()

self.converge12=QtWidgets.QLineEdit(self)
self.converge12.setText("1")
self.converge12.setGeometry(ss_x+110, offset_ss_y+(ss_y*2), 60, 20)
self.converge12_label=QtWidgets.QLabel('Pulses', self)
self.converge12_label.setGeometry(ss_x+110, offset_ss_y+(ss_y*2)-17, 100, 20)
self.converge12_label.hide()
self.converge12.hide()



