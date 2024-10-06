# Retention module

self.every_dropDown = QtWidgets.QComboBox(self)
self.every_dropDown.setGeometry(350, 60, 40, 20)
self.every_dropDown.hide()
self.duration_dropDown=QtWidgets.QComboBox(self)
self.duration_dropDown.setGeometry(350, 90, 40, 20)
self.duration_dropDown.hide()
self.unitsFull = [['s', 1], ['min', 60], ['hrs', 3600]]
self.units = [e[0] for e in self.unitsFull]
self.multiply = [e[1] for e in self.unitsFull]
self.every_dropDown.insertItems(1, self.units)
self.every_dropDown.setCurrentIndex(0)
self.registerPropertyWidget(self.every_dropDown, "interval_multiplier")
self.duration_dropDown.insertItems(1, self.units)
self.duration_dropDown.setCurrentIndex(0)
self.registerPropertyWidget(self.duration_dropDown, "duration_multiplier")

self.lineEdit_every = QtWidgets.QLineEdit(self)
self.lineEdit_every.setText("1")
self.lineEdit_every.setGeometry(300, 60, 40, 20)
self.lineEdit_every.hide()
self.lineEdit_duration = QtWidgets.QLineEdit(self)
self.lineEdit_duration.setText("1")
self.lineEdit_duration.setGeometry(300, 90, 40, 20)
self.lineEdit_duration.hide()
self.every_label=QtWidgets.QLabel('Read every:', self)
self.every_label.setGeometry(230, 60, 80, 20)
self.every_label.hide()
self.duration_label=QtWidgets.QLabel('Read for:', self)
self.duration_label.setGeometry(230, 90, 80, 20)
self.duration_label.hide()