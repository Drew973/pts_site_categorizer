# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sec_ch_widget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(810, 115)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.sec_edit = QtWidgets.QLineEdit(self.tab)
        self.sec_edit.setObjectName("sec_edit")
        self.gridLayout.addWidget(self.sec_edit, 0, 0, 1, 1)
        self.go_to_button = QtWidgets.QPushButton(self.tab)
        self.go_to_button.setObjectName("go_to_button")
        self.gridLayout.addWidget(self.go_to_button, 0, 1, 1, 1)
        self.from_layer_button = QtWidgets.QPushButton(self.tab)
        self.from_layer_button.setObjectName("from_layer_button")
        self.gridLayout.addWidget(self.from_layer_button, 0, 2, 1, 1)
        self.ch_box = QtWidgets.QSpinBox(self.tab)
        self.ch_box.setMaximum(99999)
        self.ch_box.setObjectName("ch_box")
        self.gridLayout.addWidget(self.ch_box, 1, 0, 1, 1)
        self.from_click_button = QtWidgets.QPushButton(self.tab)
        self.from_click_button.setObjectName("from_click_button")
        self.gridLayout.addWidget(self.from_click_button, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.layer_box = QgsMapLayerComboBox(self.tab_2)
        self.layer_box.setObjectName("layer_box")
        self.horizontalLayout_3.addWidget(self.layer_box)
        self.sec_field_box = QgsFieldComboBox(self.tab_2)
        self.sec_field_box.setObjectName("sec_field_box")
        self.horizontalLayout_3.addWidget(self.sec_field_box)
        self.len_field_box = QgsFieldComboBox(self.tab_2)
        self.len_field_box.setObjectName("len_field_box")
        self.horizontalLayout_3.addWidget(self.len_field_box)
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout_2.addWidget(self.tabWidget)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Find Section"))
        self.sec_edit.setToolTip(_translate("Form", "<html><head/><body><p>Section to find.</p></body></html>"))
        self.go_to_button.setToolTip(_translate("Form", "<html><head/><body><p>Go to section. Selects it on layer.</p></body></html>"))
        self.go_to_button.setText(_translate("Form", "Go To"))
        self.from_layer_button.setToolTip(_translate("Form", "<html><head/><body><p>Set section from selected feature of layer.</p></body></html>"))
        self.from_layer_button.setText(_translate("Form", "From Layer"))
        self.ch_box.setToolTip(_translate("Form", "<html><head/><body><p>Chainage (in direction of section). Changing this moves marker. <br/>From -50 to section length+50.</p></body></html>"))
        self.from_click_button.setToolTip(_translate("Form", "<html><head/><body><p>Moves marker and sets chainage to closest point to click.</p></body></html>"))
        self.from_click_button.setText(_translate("Form", "From Click"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Find"))
        self.layer_box.setToolTip(_translate("Form", "<html><head/><body><p>Layer with road network.</p></body></html>"))
        self.sec_field_box.setToolTip(_translate("Form", "<html><head/><body><p>Field with section label.</p></body></html>"))
        self.len_field_box.setToolTip(_translate("Form", "<html><head/><body><p>Field with section length.</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Layer"))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
