# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'site_categorizer_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_site_categoriserDockWidgetBase(object):
    def setupUi(self, site_categoriserDockWidgetBase):
        site_categoriserDockWidgetBase.setObjectName("site_categoriserDockWidgetBase")
        site_categoriserDockWidgetBase.resize(966, 677)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.main_widget = QtWidgets.QWidget(self.dockWidgetContents)
        self.main_widget.setObjectName("main_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.main_widget)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(2)
        self.frame.setMidLineWidth(2)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.secWidget = sectionWidget(self.frame)
        self.secWidget.setObjectName("secWidget")
        self.horizontalLayout_2.addWidget(self.secWidget)
        self.chWidget = chainageWidget(self.frame)
        self.chWidget.setObjectName("chWidget")
        self.horizontalLayout_2.addWidget(self.chWidget)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.oneWayBox = QtWidgets.QCheckBox(self.frame)
        self.oneWayBox.setObjectName("oneWayBox")
        self.horizontalLayout_3.addWidget(self.oneWayBox)
        self.noteEdit = QtWidgets.QLineEdit(self.frame)
        self.noteEdit.setObjectName("noteEdit")
        self.horizontalLayout_3.addWidget(self.noteEdit)
        self.checkedBox = QtWidgets.QCheckBox(self.frame)
        self.checkedBox.setObjectName("checkedBox")
        self.horizontalLayout_3.addWidget(self.checkedBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.tabWidget = QtWidgets.QTabWidget(self.frame)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.otherEventsAddButton = QtWidgets.QPushButton(self.tab)
        self.otherEventsAddButton.setObjectName("otherEventsAddButton")
        self.verticalLayout_5.addWidget(self.otherEventsAddButton)
        self.otherEventsView = focusedTableView(self.tab)
        self.otherEventsView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.otherEventsView.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.otherEventsView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.otherEventsView.setSortingEnabled(True)
        self.otherEventsView.setObjectName("otherEventsView")
        self.verticalLayout_5.addWidget(self.otherEventsView)
        self.tabWidget.addTab(self.tab, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_4)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.tab_4)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.addBox = QtWidgets.QComboBox(self.tab_4)
        self.addBox.setObjectName("addBox")
        self.horizontalLayout.addWidget(self.addBox)
        self.addJcButton = QtWidgets.QPushButton(self.tab_4)
        self.addJcButton.setObjectName("addJcButton")
        self.horizontalLayout.addWidget(self.addJcButton)
        self.verticalLayout_6.addLayout(self.horizontalLayout)
        self.jcView = QtWidgets.QTableView(self.tab_4)
        self.jcView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.jcView.setObjectName("jcView")
        self.verticalLayout_6.addWidget(self.jcView)
        self.tabWidget.addTab(self.tab_4, "")
        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName("widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.policyView = QtWidgets.QTableView(self.widget)
        self.policyView.setObjectName("policyView")
        self.verticalLayout_4.addWidget(self.policyView)
        self.tabWidget.addTab(self.widget, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.undoView = QtWidgets.QUndoView(self.tab_2)
        self.undoView.setObjectName("undoView")
        self.verticalLayout_7.addWidget(self.undoView)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout_3.addWidget(self.main_widget)
        site_categoriserDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(site_categoriserDockWidgetBase)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(site_categoriserDockWidgetBase)

    def retranslateUi(self, site_categoriserDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        site_categoriserDockWidgetBase.setWindowTitle(_translate("site_categoriserDockWidgetBase", "site categoriser"))
        self.oneWayBox.setToolTip(_translate("site_categoriserDockWidgetBase", "<html><head/><body><p>Mark section as one way.</p></body></html>"))
        self.oneWayBox.setText(_translate("site_categoriserDockWidgetBase", "One way"))
        self.noteEdit.setToolTip(_translate("site_categoriserDockWidgetBase", "<html><head/><body><p>note for section.</p></body></html>"))
        self.checkedBox.setToolTip(_translate("site_categoriserDockWidgetBase", "<html><head/><body><p>Mark section as checked.</p></body></html>"))
        self.checkedBox.setText(_translate("site_categoriserDockWidgetBase", "Checked"))
        self.otherEventsAddButton.setText(_translate("site_categoriserDockWidgetBase", "Add empty row"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("site_categoriserDockWidgetBase", "Other Events"))
        self.label.setText(_translate("site_categoriserDockWidgetBase", "add:"))
        self.addBox.setToolTip(_translate("site_categoriserDockWidgetBase", "<html><head/><body><p>Category to add.</p><p>Q1=minor junction,</p><p>Q2=major junction,</p><p>Q3=junction with roundabout</p><p>K=crossing</p></body></html>"))
        self.addJcButton.setToolTip(_translate("site_categoriserDockWidgetBase", "<html><head/><body><p>Add junction or crossing with selected section,chainage and category.</p></body></html>"))
        self.addJcButton.setText(_translate("site_categoriserDockWidgetBase", "Add"))
        self.jcView.setToolTip(_translate("site_categoriserDockWidgetBase", "<html><head/><body><p>Junctions and crossings table. right click on rows for options. </p><p>&lt;50m before section should be added with negative chainage. </p><p>&lt;50m after section with chainage&gt;section length.</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("site_categoriserDockWidgetBase", "Junctions/Crossings"))
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.tab_4), _translate("site_categoriserDockWidgetBase", "jc table"))
        self.policyView.setToolTip(_translate("site_categoriserDockWidgetBase", "<html><head/><body><p>policy/categories table. Where a location is affected by multiple events the event with the lower pos will take precedence. Pos should increase as irl decreases.</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.widget), _translate("site_categoriserDockWidgetBase", "Categories"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("site_categoriserDockWidgetBase", "Page"))
from chainageWidget import chainageWidget
from focusedTableView import focusedTableView
from sectionWidget import sectionWidget
