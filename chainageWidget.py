from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtGui import QColor

from qgis.gui import QgsMapToolEmitPoint,QgsVertexMarker
from qgis.utils import iface

'''
spinbox that moves marker to chainage.Section given by row of model.
independent of layers. uses model to get geometry.

'''

class chainageWidget(QDoubleSpinBox):
    
    
    def __init__(self,parent=None,canvas=None,excess=0,model=None,row=0):
        super(chainageWidget,self).__init__(parent)
        
        if not canvas:
            canvas = iface.mapCanvas()
            
        self.marker = QgsVertexMarker(canvas)
        self.marker.setIconSize(15)
        self.marker.setIconType(QgsVertexMarker.ICON_X)
        self.marker.setColor(QColor(255,0,0))
        self.marker.setPenWidth(4) 
        self.tool = QgsMapToolEmitPoint(canvas=canvas)
        
        self.excess = excess
        self.setModel(model)
        self.setRow(row)
        self.setSuffix('m')
        self.setDecimals(0)
        
        self.valueChanged.connect(self.moveMarker)
        self.tool.canvasClicked.connect(self.setFromPoint)
        

    def moveMarker(self):
        if self.model:
            self.marker.setCenter(self.model.chainageToPoint(row=self.row,chainage=self.value(),crs=iface.mapCanvas().mapSettings().destinationCrs()))
            #canvas.mapRenderer().destinationCrs() in qgis 2
            self.marker.show()
            
    
    def setRow(self,row):
        self.row = row
        self.fixEnds()
        self.setValue(0)
        
        
    def fixEnds(self):
        self.setMinimum(0-self.excess)
        if self.model:
            L = self.model.sectionLength(self.row)
            if not L is None:
                self.setMaximum(L+self.excess)
                return
        self.setMaximum(0)
        
        
    def setFromPoint(self,point):
        if self.model:
            self.setValue(self.model.pointToChainage(row=self.row,point=point,crs=iface.mapCanvas().mapSettings().destinationCrs()))
            #canvas.mapRenderer().destinationCrs() in qgis 2
    
    def setModel(self,model):
        self.model = model
        self.setRow(0)
        
        if self.model:
            self.setEnabled(True)
        else:
            self.setEnabled(False)
    
    
    def setLayer(self,layer):
        self.marker.setLayer(layer)
        
        
    def activateTool(self):
        iface.mapCanvas().setMapTool(self.tool)
        

    def focusInEvent(self,event):
        self.activateTool()
        self.marker.show()


    def removeMarker(self):
        self.marker.hide()
        

    def focusOutEvent(self,event):
        self.removeMarker()
        
        
    def setExcess(self,excess):
        self.excess = excess
        self.fixEnds()
        

   #this happens when widget closed
    def closeEvent(self,event):
        iface.mapCanvas().scene().removeItem(self.marker)
        self.tool.deactivate()
        event.accept()


    def __del__(self):
        iface.mapCanvas().scene().removeItem(self.marker)
        self.tool.deactivate()
        super(chainageWidget,self).__del__()


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
    