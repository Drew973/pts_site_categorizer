from PyQt5.QtWidgets import QCompleter,QApplication,QComboBox,QMenu,QAction
from PyQt5.QtCore import Qt,pyqtSignal

#from . import searchableComboBox

from qgis.core import QgsFeatureRequest,QgsFeature
from qgis.utils import iface


def sq(s):
    return "'%s'"%(s)


def dq(s):
    return '"%s"'%(s) 

#zoom to selected features of layer. Works with any crs
def zoomToSelected(layer):
    a=iface.activeLayer()
    iface.setActiveLayer(layer)
    iface.actionZoomToSelected().trigger()
    iface.setActiveLayer(a)
    #iface.mapCanvas().setExtent(layer.boundingBoxOfSelected())
    #iface.mapCanvas().refresh()



class searchableComboBox(QComboBox):
    
    valueChanged = pyqtSignal(str)
    
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        
        # change completion mode of the default completer from InlineCompletion to PopupCompletion
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.lineEdit().editingFinished.connect(self.editingFinished)

        self.currentIndexChanged.connect(self.indexChanged)
        
        
    def indexChanged(self,i):
        self.valueChanged.emit(self.itemText(i))
        self.featureChanged.emit(self.getFeature(warn=False))
        
        
    def editingFinished(self):
      #  print(self.currentData())
        data = self.itemText(self.currentIndex())
        self.lineEdit().setText(data)
        


'''


searchableComboBox for getting feature(s) given layer,field and value
can attempt to set value from seleted features of layer.
focus should try to select features on layer where field==value.?



	map row of QabstractTableModel to feature. using
	primary key of model and primary key of features.
	
	setModel(QabstractTableModel)
	setDisplayColumn(int)
	setModelPK(int)#primary key col of model
	setLayerPK(str)#primary key field of layer.
    

    self.secChTool.secWidget.setModel(self.networkModel)
    self.secChTool.secWidget.setModelColumn(self.networkModel.fieldIndex('sec'))
'''


class featureWidget(searchableComboBox):
    featureChanged = pyqtSignal(object)#any python object. qgs feature or None
    
    def __init__(self,parent=None,prefix='',layer=None,field=None):
        super(featureWidget,self).__init__(parent)
    
        self.prefix = prefix
        
        self.layer = layer#qgis gives has no attribute layer without this. because trying to emit getFeature.
        self.field = field
        
        self.setLayer(layer)
        self.setField(field)

        setFromLayerAct = QAction('Set from layer',self)
        setFromLayerAct.triggered.connect(self.setFromLayer)
        
        selectAct = QAction('Select on layer',self)
        selectAct.triggered.connect(self.selectOnLayer)
        
        self.addAction(setFromLayerAct)
        self.addAction(selectAct)
        
        self.menu = QMenu()
        self.menu.addAction(setFromLayerAct)
        self.menu.addAction(selectAct)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pt:self.menu.exec_(self.mapToGlobal(pt)))
        self.currentIndexChanged.connect(self.emitFeature)



 

    def setLayer(self,layer):
        self.layer = layer
        self.emitFeature()


    def setField(self,field):
        self.field = field
        self.emitFeature()


    def emitFeature(self):
        self.featureChanged.emit(self.getFeature(warn=False))
        

    def getLayer(self,warn=True):
        if self.layer:
            return self.layer
        
        if warn:
            iface.messageBar().pushMessage('%s layer not set'%(self.prefix),duration=4)


    def getField(self,warn=True):
        if self.field:
            return self.field
        
        if warn:
            iface.messageBar().pushMessage('%s field not set'%(self.prefix),duration=4)


    #returns list of features.
    def getFeatures(self,warn=True):
        data = self.itemText(self.currentIndex())
        
        layer = self.getLayer(warn)
        field = self.getField(warn)
        
        if layer and field:
            e = '%s=%s '%(dq(field),sq(data))
            request = QgsFeatureRequest().setFilterExpression(e)
            return [f for f in layer.getFeatures(request)]
        
        return []


    def getFeature(self,warn=True):
        f = self.getFeatures(warn)
        print(f)
 
        if len(f)==0:
            if warn:
                iface.messageBar().pushMessage('%s no features found'%(self.prefix),duration=4)
            return
                
        if len(f)>1:
            if warn:
                iface.messageBar().pushMessage('%s multiple features found'%(self.prefix),duration=4)
            return
                
        return f[0]
            

    #attempt to select item on layer
    def selectOnLayer(self):
        print('select on layer')
        data = self.itemText(self.currentIndex())
        
        layer = self.getLayer()
        field = self.getField()
        
        if layer and field:
            e = '%s=%s '%(dq(field),sq(data))
            layer.selectByExpression(e)

            zoomToSelected(layer)

    #attempt to set item from layer.
    def setFromLayer(self):
        
        layer = self.getLayer()
        field = self.getField()
        
        if layer and field:
            
            vals = [] #distinct values
            
            for f in self.layer.selectedFeatures():
                if not f[self.field] in vals:
                    vals.append(f[self.field])

            #no feature selected
            if not vals:
                iface.messageBar().pushMessage('no values selected on layer %s'%(self.layer.name()),duration=4)
                return
                
              #>1 value
            if len(vals)>1:
                iface.messageBar().pushMessage('>1 value selected on layer %s'%(self.layer.name()),duration=4)
                return
                
            r = self.findText(vals[0])
            if r==-1:
                iface.messageBar().pushMessage('%s not found'%(str(vals[0])),duration=4)
                return
            
            self.setCurrentIndex(r)
           
            
    #adds items from layer and field
    def setModelFromLayer(self):
        layer = self.getLayer()
        field = self.getField()
                
                
        if layer and field:
            self.clear()
            field = layer.fields().indexFromName(field)
            self.addItems([str(v) for v in layer.uniqueValues(field)])
                    

if __name__=='__console__':
    layer = iface.activeLayer()
    w = featureWidget()
    #m = QStringListModel(['aa','ab','ac'])
    #w.setModel(m)
    w.setLayer(layer)
    w.setField('sec')
    w.setModelFromLayer()
    w.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = featureWidget()
    #m = QStringListModel(['aa','ab','ac'])
    #w.setModel(m)
    w.show()
    sys.exit(app.exec_())  

    