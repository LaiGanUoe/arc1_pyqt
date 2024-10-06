ss_x=240
ss_y=45
offset_ss_x=0
offset_ss_y=20
offset_ssl_x=0
offset_ssl_y=18

offset_x_col2=90

self.parameterfit1 = QtWidgets.QLineEdit(self)
self.parameterfit1.setText("1.0")
self.parameterfit1.setGeometry(ss_x, offset_ss_y+ss_y, 60, 20)
self.parameterfit1_label=QtWidgets.QLabel('V start+ (V)', self)
self.parameterfit1_label.setGeometry(ss_x, offset_ssl_y+ss_y-25, 140, 30)
self.parameterfit1.hide()
self.parameterfit1_label.hide()

self.parameterfit2 = QtWidgets.QLineEdit(self)
self.parameterfit2.setText("0.1")
self.parameterfit2.setGeometry(ss_x, offset_ss_y+ss_y*2, 60, 20)
self.parameterfit2_label=QtWidgets.QLabel('V step (V)+', self)
self.parameterfit2_label.setGeometry(ss_x, offset_ssl_y+(ss_y*2)-25, 140, 30)
self.parameterfit2.hide()
self.parameterfit2_label.hide()

self.parameterfit3 = QtWidgets.QLineEdit(self)
self.parameterfit3.setText("2.0")
self.parameterfit3.setGeometry(ss_x, offset_ss_y+ss_y*3, 60, 20)
self.parameterfit3_label=QtWidgets.QLabel('V stop (V)+', self)
self.parameterfit3_label.setGeometry(ss_x, offset_ssl_y+(ss_y*3)-15, 100, 20)
self.parameterfit3.hide()
self.parameterfit3_label.hide()

self.parameterfit4 = QtWidgets.QLineEdit(self)
self.parameterfit4.setText("100")
self.parameterfit4.setGeometry(ss_x, offset_ss_y+ss_y*4, 60, 20)
self.parameterfit4_label=QtWidgets.QLabel('Pulses', self)
self.parameterfit4_label.setGeometry(ss_x, offset_ssl_y+(ss_y*4)-15, 100, 20)
self.parameterfit4.hide()
self.parameterfit4_label.hide()

self.parameterfit5 = QtWidgets.QLineEdit(self)
self.parameterfit5.setText("100")
self.parameterfit5.setGeometry(ss_x, offset_ss_y+ss_y*5, 60, 20)
self.parameterfit5_label=QtWidgets.QLabel('Pulse width', self)
self.parameterfit5_label.setGeometry(ss_x, offset_ssl_y+(ss_y*5)-15, 100, 20)
self.parameterfit5.hide()
self.parameterfit5_label.hide()

self.parameterfit6 = QtWidgets.QLineEdit(self)
self.parameterfit6.setText("10")
self.parameterfit6.setGeometry(ss_x, offset_ss_y+ss_y*6, 60, 20)
self.parameterfit6_label=QtWidgets.QLabel('Bias Interpulse (ms)', self)
self.parameterfit6_label.setGeometry(ss_x, offset_ssl_y+(ss_y*6)-15, 100, 20)
self.parameterfit6.hide()
self.parameterfit6_label.hide()

self.parameterfit7 = QtWidgets.QLineEdit(self)
self.parameterfit7.setText("1.0")
self.parameterfit7.setGeometry(ss_x+offset_x_col2, offset_ss_y+ss_y*1, 60, 20)
self.parameterfit7_label=QtWidgets.QLabel('V start (V)-', self)
self.parameterfit7_label.setGeometry(ss_x+offset_x_col2, offset_ssl_y+(ss_y*1)-15, 100, 20)
self.parameterfit7.hide()
self.parameterfit7_label.hide()

self.parameterfit8 = QtWidgets.QLineEdit(self)
self.parameterfit8.setText("0.1")
self.parameterfit8.setGeometry(ss_x+offset_x_col2, offset_ss_y+ss_y*2, 60, 20)
self.parameterfit8_label=QtWidgets.QLabel('V step (V)-', self)
self.parameterfit8_label.setGeometry(ss_x+offset_x_col2, offset_ssl_y+(ss_y*2)-25, 140, 30)
self.parameterfit8.hide()
self.parameterfit8_label.hide()

self.parameterfit9 = QtWidgets.QLineEdit(self)
self.parameterfit9.setText("2.0")
self.parameterfit9.setGeometry(ss_x+offset_x_col2, offset_ss_y+ss_y*3, 60, 20)
self.parameterfit9_label=QtWidgets.QLabel('V stop (V)-', self)
self.parameterfit9_label.setGeometry(ss_x+offset_x_col2, offset_ssl_y+(ss_y*3)-25, 140, 30)
self.parameterfit9.hide()
self.parameterfit9_label.hide()

self.parameterfit10 = QtWidgets.QLineEdit(self)
self.parameterfit10.setText("100")
self.parameterfit10.setGeometry(ss_x+offset_x_col2, offset_ss_y+ss_y*4, 60, 20)
self.parameterfit10_label=QtWidgets.QLabel('InterForming Readings', self)
self.parameterfit10_label.setGeometry(ss_x+offset_x_col2, offset_ssl_y+(ss_y*4)-25, 140, 30)
self.parameterfit10.hide()
self.parameterfit10_label.hide()

self.CB_parameterfit1 = QtWidgets.QCheckBox(self)
self.CB_parameterfit1.setChecked(False)
self.CB_parameterfit1.setGeometry(QtCore.QRect(ss_x+offset_x_col2, offset_ss_y+(ss_y*5)-20, 100, 20))
self.CB_parameterfit1_label=QtWidgets.QLabel('Extract param.\nauto', self)
self.CB_parameterfit1_label.setGeometry(ss_x+offset_x_col2+15, offset_ss_y+(ss_y*5)-25, 100, 30)
self.CB_parameterfit1.hide()
self.CB_parameterfit1_label.hide()



