from PyQt5.QtWidgets import QCompleter,QApplication,QComboBox,QMenu,QAction
from PyQt5.QtCore import Qt,QStringListModel

#from . import searchableComboBox

from qgis.core import QgsFeatureRequest
from qgis.utils import iface

import logging
logger = logging.getLogger(__name__)

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
        
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        
        # change completion mode of the default completer from InlineCompletion to PopupCompletion
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.lineEdit().editingFinished.connect(self.editingFinished)

        
    def editingFinished(self):
      #  print(self.currentData())
        data = self.itemText(self.currentIndex())
        self.lineEdit().setText(data)
        


'''


searchableComboBox for getting feature(s) given layer,field and value
can attempt to set value from seleted features of layer.
focus should try to select features on layer where field==value.?

map row of QabstractTableModel to feature. using primary key of model and primary key of features.
	
setModel(QabstractTableModel)
setDisplayColumn(int)
setModelPK(int)#primary key col of model
setLayerPK(str)#primary key field of layer.
    

self.secChTool.secWidget.setModel(self.networkModel)
self.secChTool.secWidget.setModelColumn(self.networkModel.fieldIndex('sec'))


needs to be parent of model or crashes when calling setModel for 2nd time.

'''


class featureWidget(searchableComboBox):
    
    def __init__(self,parent=None,prefix='',layer=None,field=None,model=None,modelPKColumn=None):
        super(featureWidget,self).__init__(parent)
    
        self.prefix = prefix
        
        self.layer = layer#qgis gives has no attribute layer without this. because trying to emit getFeature.
        self.field = field
        self.modelPKColumn = modelPKColumn
        
        self.menu = QMenu()
        
        setFromLayerAct = QAction('Set from layer',self)        
        selectAct = QAction('Select on layer',self)
        self.addAction(setFromLayerAct)
        self.addAction(selectAct)        
        
        
        self.menu.addAction(setFromLayerAct)
        self.menu.addAction(selectAct)        
        
        
        self.setLayer(layer)
        self.setField(field)
        self.setModel(model)


        setFromLayerAct.triggered.connect(self.setFromLayer)
        selectAct.triggered.connect(self.selectOnLayer)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pt:self.menu.exec_(self.mapToGlobal(pt)))


    #set column of model with primary key
    def setModelPKColumn(self,col):
        self.modelPKColumn = col

 
    #set column of model to display
    #col is int 
    def setDisplayColumn(self,col):
        super().setModelColumn(col)


    def setModel(self,model):
        logger.info('setModel(%s)'%(str(model)))
                
        if model:
            logger.info('super().setModel()')
            super().setModel(model)
            self.setEnabled(True)
            
        else:
            logger.info('reset model')
            super().setModel(QStringListModel([]))#crashes on 2nd time.
            #'cannot be null pointer'. clear will clear external model. don;t want this.
            self.setEnabled(False)

        logger.info('finished setModel(%s)'%(self.model()))


    def setEnabled(self,enabled):
        super().setEnabled(enabled)
        for a in self.actions():
            a.setEnabled(enabled)



    def setLayer(self,layer):
        self.layer = layer


    #set field with primary key
    def setField(self,field):
        self.field = field


    def getLayer(self,warn=True):
        if self.layer:
            return self.layer
        
        if warn:
            iface.messageBar().pushMessage('%s layer not set'%(self.prefix),duration=4)


    def getField(self,warn=True):
        if self.field:
            return self.field
        
        if warn:
            iface.messageBar().pushMessage('%s layer field not set'%(self.prefix),duration=4)



    def getCurrentPK(self,warn=True):
        if self.modelPKColumn is None:
            if warn:
                iface.messageBar().pushMessage('%s model primary key column not set'%(self.prefix),duration=4)
            return
        
        if not self.currentIndex() is None:
            return self.model().index(self.currentIndex(),self.modelPKColumn).data()
        else:
            if warn:
                iface.messageBar().pushMessage('%s no item selected'%(self.prefix),duration=4)
        

    #returns list of features.
    def getFeatures(self,warn=True):
        data = self.getCurrentPK(warn)
        layer = self.getLayer(warn)
        field = self.getField(warn)
        
        if layer and field and data:
            e = '%s=%s '%(dq(field),sq(data))
            request = QgsFeatureRequest().setFilterExpression(e)
            return [f for f in layer.getFeatures(request)]
        
        return []


    def getFeature(self,warn=True):
        f = self.getFeatures(warn)
        print(f)
 
        if not f:
            if warn:
                iface.messageBar().pushMessage('%s no features found'%(self.prefix),duration=4)
            return
                
        if len(f)>1:
            if warn:
                iface.messageBar().pushMessage('%s multiple features found'%(self.prefix),duration=4)
            return
                
        return f[0]
            

    #attempt to select item on layer
    def selectOnLayer(self,warn=True):
        logger.info('select on layer')
        data = self.itemText(self.currentIndex())
        
        layer = self.getLayer(warn)
        field = self.getField(warn)
        
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
            

if __name__=='__console__':
    layer = iface.activeLayer()
    w = featureWidget()
    m = QStringListModel(['aa','ab','ac'])
    w.setModel(m)
    w.setLayer(layer)
    w.setField('sec')
    w.show()


