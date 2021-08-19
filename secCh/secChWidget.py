from PyQt5.QtWidgets import QWidget

#imports from qgis console
import sys
folder = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\site_categorizer\secCh'
if not folder in sys.path:
    sys.path.append(folder)
    
import secChBase

class secChWidget(QWidget,secChBase.Ui_Form):
    
    def __init__(self,parent=None):
        super(secChWidget,self).__init__()
        self.setupUi(self)
        self.lengthBox.setAllowEmptyFieldName(True)
        
        self.layerBox.layerChanged.connect(self.secWidget.setLayer)
        self.layerBox.layerChanged.connect(self.chWidget.setLayer)
        
        self.layerBox.layerChanged.connect(self.labelBox.setLayer)
        self.layerBox.layerChanged.connect(self.lengthBox.setLayer)
        
        self.labelBox.fieldChanged.connect(self.secWidget.setField)
        self.lengthBox.fieldChanged.connect(self.chWidget.setLengthField)
        
        self.secWidget.featureChanged.connect(self.chWidget.setFeature)


   
    def setFollowLayer(self,followLayer):
        try:
            w.labelBox.fieldChanged.disconnect(w.secWidget.setModelFromLayer)
        except:
            pass
            
        if followLayer:
            w.labelBox.fieldChanged.connect(w.secWidget.setModelFromLayer)
    
    
    def setCh(self,ch):
        self.chWidget.setCh(ch)
        
    
if __name__=='__console__':
    #layer = iface.activeLayer()
    w = secChWidget()
    #w.layerBox.layerChanged.connect(w.secWidget.setModelFromLayer)
    #m = QStringListModel(['aa','ab','ac'])
    #w.setModel(m)
   # w.setLayer(layer)
    #w.setField('sec')
    #w.setModelFromLayer()
    w.show()
