# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Alin\Desktop\arc1_pyqt\uis\pf.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PFParent(object):
    def setupUi(self, PFParent):
        PFParent.setObjectName("PFParent")
        PFParent.resize(610, 377)
        self.gridLayout = QtWidgets.QGridLayout(PFParent)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.applyOneButton = QtWidgets.QPushButton(PFParent)
        self.applyOneButton.setObjectName("applyOneButton")
        self.horizontalLayout.addWidget(self.applyOneButton)
        self.applyRangeButton = QtWidgets.QPushButton(PFParent)
        self.applyRangeButton.setObjectName("applyRangeButton")
        self.horizontalLayout.addWidget(self.applyRangeButton)
        self.applyAllButton = QtWidgets.QPushButton(PFParent)
        self.applyAllButton.setObjectName("applyAllButton")
        self.horizontalLayout.addWidget(self.applyAllButton)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 3)
        self.descriptionLabel = QtWidgets.QLabel(PFParent)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.gridLayout.addWidget(self.descriptionLabel, 1, 0, 1, 2)
        self.titleLabel = QtWidgets.QLabel(PFParent)
        self.titleLabel.setObjectName("titleLabel")
        self.gridLayout.addWidget(self.titleLabel, 0, 0, 1, 2)
        self.scrollArea = QtWidgets.QScrollArea(PFParent)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -14, 576, 298))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_13 = QtWidgets.QLabel(self.frame)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 6, 0, 1, 1)
        self.IVTypeCombo = QtWidgets.QComboBox(self.frame)
        self.IVTypeCombo.setObjectName("IVTypeCombo")
        self.gridLayout_2.addWidget(self.IVTypeCombo, 6, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.frame)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 5, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 14, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.nrPulsesEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nrPulsesEdit.sizePolicy().hasHeightForWidth())
        self.nrPulsesEdit.setSizePolicy(sizePolicy)
        self.nrPulsesEdit.setObjectName("nrPulsesEdit")
        self.gridLayout_2.addWidget(self.nrPulsesEdit, 1, 1, 1, 1)
        self.interpulseEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.interpulseEdit.sizePolicy().hasHeightForWidth())
        self.interpulseEdit.setSizePolicy(sizePolicy)
        self.interpulseEdit.setObjectName("interpulseEdit")
        self.gridLayout_2.addWidget(self.interpulseEdit, 3, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.frame)
        self.label_8.setObjectName("label_8")
        self.gridLayout_2.addWidget(self.label_8, 3, 0, 1, 1)
        self.pulseWidthEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pulseWidthEdit.sizePolicy().hasHeightForWidth())
        self.pulseWidthEdit.setSizePolicy(sizePolicy)
        self.pulseWidthEdit.setObjectName("pulseWidthEdit")
        self.gridLayout_2.addWidget(self.pulseWidthEdit, 2, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 2, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.frame)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 4, 0, 1, 1)
        self.IVPwEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IVPwEdit.sizePolicy().hasHeightForWidth())
        self.IVPwEdit.setSizePolicy(sizePolicy)
        self.IVPwEdit.setObjectName("IVPwEdit")
        self.gridLayout_2.addWidget(self.IVPwEdit, 5, 1, 1, 1)
        self.IVInterpulseEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IVInterpulseEdit.sizePolicy().hasHeightForWidth())
        self.IVInterpulseEdit.setSizePolicy(sizePolicy)
        self.IVInterpulseEdit.setObjectName("IVInterpulseEdit")
        self.gridLayout_2.addWidget(self.IVInterpulseEdit, 4, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.frame)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 8, 0, 1, 1)
        self.IVStepEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IVStepEdit.sizePolicy().hasHeightForWidth())
        self.IVStepEdit.setSizePolicy(sizePolicy)
        self.IVStepEdit.setObjectName("IVStepEdit")
        self.gridLayout_2.addWidget(self.IVStepEdit, 8, 1, 1, 1)
        self.VStartPosEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VStartPosEdit.sizePolicy().hasHeightForWidth())
        self.VStartPosEdit.setSizePolicy(sizePolicy)
        self.VStartPosEdit.setObjectName("VStartPosEdit")
        self.gridLayout_2.addWidget(self.VStartPosEdit, 1, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 2, 1, 1)
        self.VStepPosEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VStepPosEdit.sizePolicy().hasHeightForWidth())
        self.VStepPosEdit.setSizePolicy(sizePolicy)
        self.VStepPosEdit.setObjectName("VStepPosEdit")
        self.gridLayout_2.addWidget(self.VStepPosEdit, 2, 3, 1, 1)
        self.VStopNegEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VStopNegEdit.sizePolicy().hasHeightForWidth())
        self.VStopNegEdit.setSizePolicy(sizePolicy)
        self.VStopNegEdit.setObjectName("VStopNegEdit")
        self.gridLayout_2.addWidget(self.VStopNegEdit, 3, 4, 1, 1)
        self.VStopPosEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VStopPosEdit.sizePolicy().hasHeightForWidth())
        self.VStopPosEdit.setSizePolicy(sizePolicy)
        self.VStopPosEdit.setObjectName("VStopPosEdit")
        self.gridLayout_2.addWidget(self.VStopPosEdit, 3, 3, 1, 1)
        self.VStepNegEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VStepNegEdit.sizePolicy().hasHeightForWidth())
        self.VStepNegEdit.setSizePolicy(sizePolicy)
        self.VStepNegEdit.setObjectName("VStepNegEdit")
        self.gridLayout_2.addWidget(self.VStepNegEdit, 2, 4, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 2, 1, 1)
        self.IVStopNegEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IVStopNegEdit.sizePolicy().hasHeightForWidth())
        self.IVStopNegEdit.setSizePolicy(sizePolicy)
        self.IVStopNegEdit.setObjectName("IVStopNegEdit")
        self.gridLayout_2.addWidget(self.IVStopNegEdit, 8, 4, 1, 1)
        self.IVStopPosEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IVStopPosEdit.sizePolicy().hasHeightForWidth())
        self.IVStopPosEdit.setSizePolicy(sizePolicy)
        self.IVStopPosEdit.setObjectName("IVStopPosEdit")
        self.gridLayout_2.addWidget(self.IVStopPosEdit, 8, 3, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.frame)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 8, 2, 1, 1)
        self.IVStartEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IVStartEdit.sizePolicy().hasHeightForWidth())
        self.IVStartEdit.setSizePolicy(sizePolicy)
        self.IVStartEdit.setObjectName("IVStartEdit")
        self.gridLayout_2.addWidget(self.IVStartEdit, 7, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 7, 0, 1, 1)
        self.noIVCheckBox = QtWidgets.QCheckBox(self.frame)
        self.noIVCheckBox.setObjectName("noIVCheckBox")
        self.gridLayout_2.addWidget(self.noIVCheckBox, 9, 0, 1, 1)
        self.VStartNegEdit = QtWidgets.QLineEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VStartNegEdit.sizePolicy().hasHeightForWidth())
        self.VStartNegEdit.setSizePolicy(sizePolicy)
        self.VStartNegEdit.setObjectName("VStartNegEdit")
        self.gridLayout_2.addWidget(self.VStartNegEdit, 1, 4, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setStyleSheet("font-weight:bold;")
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 4, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setStyleSheet("font-weight:bold;")
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 2, 5, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 2, 0, 1, 3)

        self.retranslateUi(PFParent)
        QtCore.QMetaObject.connectSlotsByName(PFParent)
        PFParent.setTabOrder(self.nrPulsesEdit, self.pulseWidthEdit)
        PFParent.setTabOrder(self.pulseWidthEdit, self.interpulseEdit)
        PFParent.setTabOrder(self.interpulseEdit, self.applyOneButton)
        PFParent.setTabOrder(self.applyOneButton, self.applyRangeButton)
        PFParent.setTabOrder(self.applyRangeButton, self.applyAllButton)

    def retranslateUi(self, PFParent):
        _translate = QtCore.QCoreApplication.translate
        PFParent.setWindowTitle(_translate("PFParent", "Form"))
        self.applyOneButton.setText(_translate("PFParent", "Apply to One"))
        self.applyRangeButton.setText(_translate("PFParent", "Apply to Range"))
        self.applyAllButton.setText(_translate("PFParent", "Apply to All"))
        self.descriptionLabel.setText(_translate("PFParent", "Fit a stimulus model to memristive response"))
        self.titleLabel.setText(_translate("PFParent", "Parameter Fit"))
        self.label_13.setText(_translate("PFParent", "I-V Type"))
        self.label_14.setText(_translate("PFParent", "I-V pulse width (ms)"))
        self.label.setText(_translate("PFParent", "Pulses"))
        self.nrPulsesEdit.setText(_translate("PFParent", "500"))
        self.interpulseEdit.setText(_translate("PFParent", "10"))
        self.label_8.setText(_translate("PFParent", "Bias Interpulse (ms)"))
        self.pulseWidthEdit.setText(_translate("PFParent", "100"))
        self.label_7.setText(_translate("PFParent", "Pulse width (us)"))
        self.label_12.setText(_translate("PFParent", "I-V Interpulse (ms)"))
        self.IVPwEdit.setText(_translate("PFParent", "1"))
        self.IVInterpulseEdit.setText(_translate("PFParent", "10"))
        self.label_10.setText(_translate("PFParent", "I-V step (V)"))
        self.IVStepEdit.setText(_translate("PFParent", "0.1"))
        self.VStartPosEdit.setText(_translate("PFParent", "1.0"))
        self.label_3.setText(_translate("PFParent", "V step (V)"))
        self.VStepPosEdit.setText(_translate("PFParent", "0.1"))
        self.VStopNegEdit.setText(_translate("PFParent", "2.0"))
        self.VStopPosEdit.setText(_translate("PFParent", "2.0"))
        self.VStepNegEdit.setText(_translate("PFParent", "0.1"))
        self.label_4.setText(_translate("PFParent", "V stop (V)"))
        self.IVStopNegEdit.setText(_translate("PFParent", "0.5"))
        self.IVStopPosEdit.setText(_translate("PFParent", "0.5"))
        self.label_11.setText(_translate("PFParent", "I-V stop (V)"))
        self.IVStartEdit.setText(_translate("PFParent", "0.1"))
        self.label_9.setText(_translate("PFParent", "I-V start (V)"))
        self.noIVCheckBox.setText(_translate("PFParent", "Don\'t run I-V"))
        self.VStartNegEdit.setText(_translate("PFParent", "1.0"))
        self.label_2.setText(_translate("PFParent", "V start (V)"))
        self.label_6.setText(_translate("PFParent", "Negative Polarity"))
        self.label_5.setText(_translate("PFParent", "Positive polarity"))
