from PyQt5.QtWidgets import QDoubleSpinBox

from qgis.utils import iface


import chainageMarker,chainageTool




#need to set feature to set marker pos.


class chainageWidget(QDoubleSpinBox):
    
    #need to get crs of feature geometry. to display market.
   # only seem to be able to do using layer crs.
    
    def __init__(self,parent=None,canvas=None,layer=None,feature=None,excess=0,lengthField=None):
        super(chainageWidget,self).__init__(parent)
        
        if not canvas:
            canvas = iface.mapCanvas()
            
        self.marker = chainageMarker.chainageMarker(canvas=canvas,layer=layer,feature=feature,lengthField=lengthField)
        self.tool = chainageTool.chainageTool(canvas=canvas,marker=self.marker)
        
        self.excess = excess
        self.setFeature(feature)
        self.setSuffix('m')
        self.setDecimals(0)
        
        self.valueChanged.connect(self.marker.setChainage)
        self.tool.clicked.connect(self.setValue)
        

    def setFeature(self,feature):
        self.marker.setFeature(feature)
        self.setEnds()
        
        
    def setLengthField(self,field):
        self.marker.setLengthField(field)
        
    
    def setLayer(self,layer):
        self.marker.setLayer(layer)
        
        
    def activateTool(self):
        iface.mapCanvas().setMapTool(self.tool)
        

    def focusInEvent(self,event):
        self.activateTool()
        self.marker.setChainage(self.marker.chainage)#will show if hidden.


    def focusOutEvent(self,event):
        self.marker.hide()
        
        
    def setExcess(self,excess):
        self.excess = excess
        self.setEnds()
        
        
    def setEnds(self):
        length =  self.marker.featureLength()
        
        if length:
            self.setMaximum(self.excess+length)
            self.setMinimum(0-self.excess)
            
        else:
            self.setMaximum(0)
            self.setMinimum(0)
    

            
   #this happens when widget closed
    def closeEvent(self,event):
        iface.mapCanvas().scene().removeItem(self.marker)
        self.tool.deactivate()
        #print('close event')
        event.accept()

# def __del__(self):
   #     print('__del__')
    #    iface.mapCanvas().scene().removeItem(self.marker)
    #    iface.mapCanvas().refresh()
      #  super(chainageWidget,self).__del__()
        
        
if __name__=='__console__':
    layer = iface.activeLayer()
   
    if layer.selectedFeatures():
        f = layer.selectedFeatures()[0]
        w =  chainageWidget(excess=50,feature=f,layer=layer)
        w.setFeature(f)
        w.show()