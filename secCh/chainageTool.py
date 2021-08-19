from qgis.gui import QgsMapTool
from PyQt5.QtCore import pyqtSignal
#import sys


#folder = r'C:\Users\drew.bennett\Documents\PyQgis\chainage_tool'
#if not folder in sys.path:
#    sys.path.append(folder)
    
#import chainageMarker

 
class chainageTool(QgsMapTool):
    
    clicked = pyqtSignal(float)
   
    def __init__(self,canvas,marker):
        self.canvas = canvas
        super(QgsMapTool,self).__init__(canvas)
        self.marker = marker
        
        
    def canvasPressEvent(self, event):
        #toLayerCoordinates(self.marker.layer,(event.mapPoint())
        self.marker.setFromPoint(self.toLayerCoordinates(self.marker.layer,event.mapPoint()))
        #self.marker.setFromPoint(event.mapPoint())
        self.clicked.emit(self.marker.chainage)
        
        
    #def canvasReleaseEvent(self, event):
       # pass
        #print('release event')
                
  #  def deactivate(self):
   #     iface.mapCanvas().scene().removeItem(self.marker)

       

if __name__=='__console__':
    layer = iface.activeLayer()
   
    if layer.selectedFeatures():
        f = layer.selectedFeatures()[0]
        m = chainageMarker.chainageMarker(canvas=iface.mapCanvas(),layer=layer,feature=f)
        t = chainageTool(iface.mapCanvas(),marker=m)
        iface.mapCanvas().setMapTool(t)
       