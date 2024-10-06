ss_x=240
ss_y=45
offset_ss_x=0
offset_ss_y=20
offset_ssl_x=0
offset_ssl_y=18

offset_x_col2=90

self.uniformity1 = QtWidgets.QLineEdit(self)
self.uniformity1.setText("1")
self.uniformity1.setGeometry(ss_x, offset_ss_y+ss_y, 40, 20)
self.uniformity1_label=QtWidgets.QLabel('Bins Vread', self)
self.uniformity1_label.setGeometry(ss_x, offset_ssl_y+ss_y-25, 140, 30)
self.uniformity1.hide()
self.uniformity1_label.hide()

self.CB_uniformity2 = QtWidgets.QCheckBox(self)
self.CB_uniformity2.setChecked(False)
self.CB_uniformity2.setGeometry(ss_x, offset_ss_y+ss_y*2, 40, 20)
self.CB_uniformity2_label=QtWidgets.QLabel('Rs leveling', self)
self.CB_uniformity2_label.setGeometry(ss_x, offset_ssl_y+(ss_y*2)-25, 140, 30)
self.CB_uniformity2.hide()
self.CB_uniformity2_label.hide()

self.CB_uniformity3 = QtWidgets.QCheckBox(self)
self.CB_uniformity3.setEnabled(False)
self.CB_uniformity3.setChecked(False)
self.CB_uniformity3.setGeometry(ss_x, offset_ss_y+ss_y*3, 40, 20)
self.CB_uniformity3_label=QtWidgets.QLabel('Vmemristor leveling', self)
self.CB_uniformity3_label.setGeometry(ss_x, offset_ssl_y+(ss_y*3)-15, 150, 20)
self.CB_uniformity3.hide()
self.CB_uniformity3_label.hide()

self.uniformity4 = QtWidgets.QLineEdit(self)
self.uniformity4.setText("1")
self.uniformity4.setGeometry(ss_x, offset_ss_y+ss_y*4, 40, 20)
self.uniformity4_label=QtWidgets.QLabel('R_top', self)
self.uniformity4_label.setGeometry(ss_x, offset_ssl_y+(ss_y*4)-15, 150, 20)
self.uniformity4.hide()
self.uniformity4_label.hide()

self.uniformity5 = QtWidgets.QLineEdit(self)
self.uniformity5.setText("1")
self.uniformity5.setGeometry(ss_x, offset_ss_y+ss_y*5, 40, 20)
self.uniformity5_label=QtWidgets.QLabel('R_bottom', self)
self.uniformity5_label.setGeometry(ss_x, offset_ssl_y+(ss_y*5)-15, 150, 20)
self.uniformity5.hide()
self.uniformity5_label.hide()