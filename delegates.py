
from PyQt5.QtSql import QSqlRelationalDelegate
from PyQt5.QtWidgets import QComboBox,QLineEdit,QCompleter,QStyledItemDelegate
from PyQt5.QtGui import QStandardItemModel

#from . import secWidget
#from . import chainageWidget



#read only delegate ro display label
class readOnlyText(QStyledItemDelegate):
    
    def createEditor(self,parent,option,index):
        edit = QLineEdit(parent)
        edit.setReadOnly(True)
        return edit





#read only delegate ro display label
class comboboxDelegate(QStyledItemDelegate):
    
    
    def __init__(self,parent,model=None,column=None,items=[]):
        super(comboboxDelegate,self).__init__(parent)
        self.model = model
        self.column = column
        self.items = items
            
        
    def createEditor(self,parent,option,index):
        b = QComboBox(parent)
        
        if self.model:
            b.setModel(self.model)
            
            if self.column:
                b.setModelColumn(self.column)
        
        if self.items:
            b.addItems(self.items)
            
        return b


    def setItems(self,items):
        self.items = items

    def setModel(self,model):
        self.model = model


    def setColumn(self,column):
        self.column = column



class searchableRelationalDelegate(QSqlRelationalDelegate):
    
    
    def createEditor(self,parent,option,index):
        box = super(searchableRelationalDelegate,self).createEditor(parent,option,index)
        makeSearchable(box)
        return box




class lineEditRelationalDelegate(QSqlRelationalDelegate):
    
    
    def createEditor(self,parent,option,index):
        box = super(lineEditRelationalDelegate,self).createEditor(parent,option,index)
               
        edit = QLineEdit(parent)

        c = QCompleter(edit)
        c.setModel(box.model())
        c.setCompletionColumn(box.modelColumn())
        
        edit.setCompleter(c)
        return edit



'''
class secWidgetDelegate(QStyledItemDelegate):
    
    def __init__(self,fw,model,column,parent=None):
        super(secWidgetDelegate,self).__init__(parent)
        self.fw = fw
        self.model = model
        self.column = column
        
        
    def createEditor(self,parent,option,index):
        w = secWidget.secWidget(fw=self.fw,parent=parent,model=self.model,column=self.column)
        return w
'''



#The setEditorData() function is called when an editor is created to initialize it with data from the model:
#default fine


#spatial index per widget. performance seem ok.
#might be better to 


class chainageWidgetDelegate(QStyledItemDelegate):
    
    def __init__(self,fw,parent=None):
        super(chainageWidgetDelegate,self).__init__(parent)
        self.fw = fw
        
        
#clicking map causes delegate to lose focus and widget to stop existing,meaning setValue doesn't do anything?
#get around this with lamdba function
        
    def createEditor(self,parent,option,index):
        w = chainageWidget.runChainageWidget(parent=parent,layer=self.fw['readings'],field=self.fw['s_ch'])
        w.tool.chainageFound.connect(lambda val:index.model().setData(index,val))
        
        
        return w


 #   def setLayer(self,layer):
     #   self.layer = layer
    #    #symbolFeatureCountMapChanged
     #   self.index = QgsSpatialIndex(layer.getFeatures(),None,QgsSpatialIndex.FlagStoreFeatureGeometries )


#The setModelData() function is called to commit data from the editor to the model when editing is finished:
   #default works.
   # def setModelData(self,editor,model,index):
    #    model.setData(index,editor.value())



# makes qComboBox b searchable
def makeSearchable(b):
    b.setEditable(True)
    b.setInsertPolicy(QComboBox.NoInsert)
    b.lineEdit().editingFinished.connect(lambda:b.setCurrentText(b.itemText(b.currentIndex())))
    
   # b.lineEdit().setCompleter()
    #editing finished triggered when lineEdit loses focus.
    #b.Model()
    #modelColumn()
    
    
   # QCompleter.setModel()
    #QCompleter.setCompletionColumn#column of model to use
    
    
