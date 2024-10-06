# Reinforcement learning forming module

ss_x=240
ss_y=45
offset_ss_x=0
offset_ss_y=20
offset_ssl_x=0
offset_ssl_y=18

offset_x_col2=90

self.RILForming1 = QtWidgets.QLineEdit(self)
self.RILForming1.setText("12")
self.RILForming1.setGeometry(ss_x, offset_ss_y+ss_y, 60, 20)
self.RILForming1_label=QtWidgets.QLabel('Max Voltage (V)', self)
self.RILForming1_label.setGeometry(ss_x, offset_ssl_y+ss_y-25, 140, 30)
self.RILForming1.hide()
self.RILForming1_label.hide()

self.RILForming2 = QtWidgets.QLineEdit(self)
self.RILForming2.setText("20")
self.RILForming2.setGeometry(ss_x, offset_ss_y+ss_y*2, 60, 20)
self.RILForming2_label=QtWidgets.QLabel('Max Cycles', self)
self.RILForming2_label.setGeometry(ss_x, offset_ssl_y+(ss_y*2)-25, 140, 30)
self.RILForming2.hide()
self.RILForming2_label.hide()

self.RILForming3 = QtWidgets.QLineEdit(self)
self.RILForming3.setText("120")
self.RILForming3.setGeometry(ss_x, offset_ss_y+ss_y*3, 60, 20)
self.RILForming3_label=QtWidgets.QLabel('Step Voltage', self)
self.RILForming3_label.setGeometry(ss_x, offset_ssl_y+(ss_y*3)-15, 100, 20)
self.RILForming3.hide()
self.RILForming3_label.hide()

self.RILForming4 = QtWidgets.QLineEdit(self)
self.RILForming4.setText("0.0001")
self.RILForming4.setGeometry(ss_x, offset_ss_y+ss_y*4, 60, 20)
self.RILForming4_label=QtWidgets.QLabel('Pulse Width', self)
self.RILForming4_label.setGeometry(ss_x, offset_ssl_y+(ss_y*4)-15, 100, 20)
self.RILForming4.hide()
self.RILForming4_label.hide()

self.RILForming5 = QtWidgets.QLineEdit(self)
self.RILForming5.setText("0.999")
self.RILForming5.setGeometry(ss_x, offset_ss_y+ss_y*5, 60, 20)
self.RILForming5_label=QtWidgets.QLabel('Gamma', self)
self.RILForming5_label.setGeometry(ss_x, offset_ssl_y+(ss_y*5)-15, 100, 20)
self.RILForming5.hide()
self.RILForming5_label.hide()