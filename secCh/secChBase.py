# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'secChWidget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(557, 167)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layerBox = QgsMapLayerComboBox(Form)
        self.layerBox.setObjectName("layerBox")
        self.horizontalLayout.addWidget(self.layerBox)
        self.labelBox = QgsFieldComboBox(Form)
        self.labelBox.setObjectName("labelBox")
        self.horizontalLayout.addWidget(self.labelBox)
        self.lengthBox = QgsFieldComboBox(Form)
        self.lengthBox.setObjectName("lengthBox")
        self.horizontalLayout.addWidget(self.lengthBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.secWidget = featureWidget(Form)
        self.secWidget.setObjectName("secWidget")
        self.horizontalLayout_2.addWidget(self.secWidget)
        self.chWidget = chainageWidget(Form)
        self.chWidget.setObjectName("chWidget")
        self.horizontalLayout_2.addWidget(self.chWidget)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Find Section"))
        self.layerBox.setToolTip(_translate("Form", "<html><head/><body><p>Layer with network.</p></body></html>"))
        self.labelBox.setToolTip(_translate("Form", "<html><head/><body><p>Field with section label.</p></body></html>"))
        self.lengthBox.setToolTip(_translate("Form", "<html><head/><body><p>Field with section length. Leave blank to use geometry.</p></body></html>"))
        self.secWidget.setToolTip(_translate("Form", "<html><head/><body><p>Section to find.</p></body></html>"))
        self.chWidget.setToolTip(_translate("Form", "<html><head/><body><p>Chainage. Change to move marker. Click map to change chainage.</p><p><br/></p></body></html>"))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
from secCh.chainageWidget import chainageWidget
from secCh.featureWidget import featureWidget
