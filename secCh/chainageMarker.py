from qgis.gui import QgsVertexMarker
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal

from qgis.core import QgsProject,QgsGeometry,QgsCoordinateTransform
from qgis.utils import iface

#PyQt5.QtWidgets.QGraphicsItem-->qgsMapCanvasItem-->QgsVertexMarker

#QGraphicsItem does not inherit from QObject, therefore it is not possible to emit a signal from an instance of QGraphicsItem.
#You can solve this by subclassing QGraphicsObject instead of QGraphicsItem

#from PyQt5.QtWidgets import QGraphicsObject
#inheriting from QgsVertexMarker and QGraphicsObject causes crash.

#need feature and layer to display of set from click.


#get length from model?
#add setLength method?



class chainageMarker(QgsVertexMarker):
    
    #chainageSet = pyqtSignal(float)
    
    def __init__(self,canvas,layer=None,feature=None,lengthField=None):
    
        print('canvas:%s'%(str(canvas)))
        super().__init__(canvas)
        #super(QgsVertexMarker,self).__init__(canvas)#no documentation for constructor?
        self.setIconSize(15)
        self.setIconType(QgsVertexMarker.ICON_X)
        self.setColor(QColor(255,0,0))
        self.setPenWidth(4) 
        
        self.layer = layer
        self.lengthField = lengthField
        self.chainage = 0
        
        self.setFeature(feature)
        self.lengthField = lengthField
        self.canvas = canvas
        
        
    def setFeature(self,feature):
        self.feature = feature
        self.setChainage(0)
        
    
    
    def setLayer(self,layer):
        self.layer = layer
    
    
    def setLengthField(self,lengthField):
        self.lengthField = lengthField
    
    
    def __del__(self):
        self.canvas.removeItem(self)
        super().__del__

    
    def dragEnterEvent(self,event):
        print('draging marker')

    
    def mousePressEvent(self,event):
        print('mouse press')

    
    def featureLength(self,feature=None):
        if not feature:
            feature = self.feature
        
        if not self.feature:
            return
            
        if self.lengthField:
            return self.feature[self.lengthField]
            
        else:
            return feature.geometry().length()
            
            
    def setChainage(self,chainage):
        self.chainage = chainage
        #self.chainageSet.emit(chainage)
        
        if self.feature and self.layer:
            pt = self.chainageToPt(chainage)
            print(pt)
            if pt:
                self.setCenter(pt)
                self.show()
                self.updateCanvas()
                return
    
        self.hide()
            
        
    #pt in crs of layer
    def setFromPoint(self,pt):
        
        if self.layer and self.feature:
            g = self.feature.geometry()
            #transform pt from to layer crs
           # t = QgsCoordinateTransform(iface.mapCanvas().mapSettings().destinationCrs(),self.layer.sourceCrs(),QgsProject.instance())#documentation says only need source and destination. lies.    
           # pt = t.transform(pt)#transform takes qgspoint xy
            pt = QgsGeometry().fromPointXY(pt)
            self.setChainage(g.lineLocatePoint(pt)*self.featureLength(self.feature)/g.length()) #takes QgsGeometry not qgspointxy


    def chainageToPt(self,ch):
        if self.layer:
            t = QgsCoordinateTransform(self.layer.sourceCrs(),iface.mapCanvas().mapSettings().destinationCrs(),QgsProject.instance())
            #transform from layer crs to display crs
            #documentation says only need source and destination. lies.
            
            #transform takes qgspoint xy
            g = self.feature.geometry()
            length = self.featureLength(self.feature)
            
            if ch<=0:
                return t.transform(g.asPolyline()[0])#return start of line
    
            if ch>=length:
                return t.transform(g.asPolyline()[-1])#return end of line
    
            return t.transform(g.interpolate(g.length()*ch/length).asPoint())
            
        
        
        
if __name__=='__console__':
    layer = iface.activeLayer()
   
    if layer.selectedFeatures():
        f = layer.selectedFeatures()[0]
        m = chainageMarker(canvas=iface.mapCanvas(),layer=layer,feature=f)
        #iface.mapCanvas().scene().removeItem(m)
        