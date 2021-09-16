from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtGui import QColor

from qgis.gui import QgsMapToolEmitPoint,QgsVertexMarker
from qgis.utils import iface


from . import lrsFunctions

import logging
logger = logging.getLogger(__name__)

'''
spinbox that moves marker to chainage.Section given by row of model.
independent of layers. uses model to get geometry.

model = networkModel
row=row of network model

want setting model value to be reversible
holding arrow only counts as 1 change.

'''

class chainageWidget(QDoubleSpinBox):
    
    
    def __init__(self,parent=None,canvas=None,excess=0,geometry=None,sectionLength=None):
        super(chainageWidget,self).__init__(parent)
        
        if not canvas:
            canvas = iface.mapCanvas()
            
        self.index = None    
        self.excess = excess
        
        
        self.marker = QgsVertexMarker(canvas)
        self.marker.setIconSize(15)
        self.marker.setIconType(QgsVertexMarker.ICON_X)
        self.marker.setColor(QColor(255,0,0))
        self.marker.setPenWidth(4)      
        
        self.setSuffix('m')
        self.setDecimals(0)
        
        self.valueChanged.connect(self.onValueChanged)
        
        self.tool = QgsMapToolEmitPoint(canvas=canvas)
        self.tool.canvasClicked.connect(self.setFromPoint)
        
        self.setSection(geometry,sectionLength)
        self.onValueChanged()


    def setIndex(self,index):
        self.index = index
        self.setValue(index.data())
        
        
    def onValueChanged(self,value=None): 
        
        if value is None:
            value = self.value()
        
        if self.geometry and not self.sectionLength is None:
            self.marker.setCenter(lrsFunctions.chainageToPoint(value,self.geometry,self.sectionLength))
            
            
        if not self.index is None:
            self.index.model().setData(self.index,value)    
    
        
    def setFromPoint(self,point):
        logger.info('setFromPoint(%s)'%(point))
        if self.geometry and not self.sectionLength is None:
            self.setValue(lrsFunctions.pointToChainage(point,self.geometry,self.sectionLength))
 
        
    
    def setSection(self,geometry,sectionLength):
        self.geometry = geometry
        self.sectionLength = sectionLength
        self.setEnabled(True)
        
        if not sectionLength is None:
            self.setMaximum(sectionLength+self.excess)
        
        self.setMinimum(0-self.excess)
        self.setValue(0)
    
    
    def setLayer(self,layer):
        self.marker.setLayer(layer)
        
        
    def activateTool(self):
        iface.mapCanvas().setMapTool(self.tool)
        

    def focusInEvent(self,event):
        self.activateTool()
        self.marker.show()
            
        
    def setExcess(self,excess):
        self.excess = excess
        

   #this happens when widget closed
    def closeEvent(self,event):        
        iface.mapCanvas().scene().removeItem(self.marker)
        self.tool.deactivate()
        event.accept()


    def __del__(self):
        iface.mapCanvas().scene().removeItem(self.marker)
        self.tool.deactivate()


if __name__=='__console__':
    from PyQt5.QtSql import QSqlDatabase
    import sys
    folder = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\site_categorizer'
    if not folder in sys.path:
        sys.path.append(folder)
        
    import networkModel

    db = QSqlDatabase.addDatabase('QPSQL','site cat test')
    db.setHostName('192.168.5.157')
    db.setDatabaseName('pts2157-02_blackburn')
    db.setUserName('stuart')
    print(db.open())
    m = networkModel.networkModel(db)
    
    w = chainageWidget(model=m,row=0)
    w.show()
    