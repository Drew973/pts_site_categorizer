# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 08:17:59 2021

@author: Drew.Bennett
"""

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
from . import featureWidget,undoableComboBox
from PyQt5.QtWidgets import QWidgetAction,QHBoxLayout,QWidget


class fieldWidgetAction(QWidgetAction):
    
    #def __init__(self,parent=None):
        #super().__init__(parent)
        
    def createWidget(self,parent):
        w = QWidget()
        w.setLayout(QHBoxLayout())
        self.layout().addWidget(self.layerBox)


def makeWidgetAction(layerBox=None,fieldBox=None,parent=None):
    if not layerBox:
        layerBox = QgsMapLayerComboBox()
        
    if not fieldBox:
        fieldBox = QgsFieldComboBox()
        
    a = QWidgetAction(parent)
    w = QWidget(parent)
    w.setLayout(QHBoxLayout())
    w.layout().addWidget(layerBox)
    w.layout().addWidget(fieldBox)
    a.setDefaultWidget(w)
    return a



def toWidgetAction(widget,parent=None):
    a = QWidgetAction(parent)
    a.setDefaultWidget(widget)
    return a
    
    
class sectionWidget(featureWidget.featureWidget,undoableComboBox.undoableComboBox):
    
    def __init__(self,parent=None,prefix=''):
        super().__init__(parent=parent,prefix=prefix)
        self.lastRow = 0
        
        self.layerBox = QgsMapLayerComboBox()
        self.fieldBox = QgsFieldComboBox()
        
        self.layerBox.layerChanged.connect(self.setLayer)
        self.layerBox.layerChanged.connect(self.fieldBox.setLayer)
        self.fieldBox.fieldChanged.connect(self.setField)
        self.fieldBox.setLayer(self.layerBox.currentLayer())
        
        
        self.layerMenu =  self.menu.addMenu('Layer')
        self.layerMenu.addAction(toWidgetAction(self.layerBox,self))
        
        #layerMenu.addAction(toWidgetAction(self.layerBox))

        #self.menu.addAction(toWidgetAction(self.layerBox,self))
        fieldMenu =  self.menu.addMenu('Field')
        fieldMenu.addAction(toWidgetAction(self.fieldBox,self))

        



if __name__=='__console__':
    
    w = sectionWidget()
    w.show()