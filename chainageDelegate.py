from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import QModelIndex
import chainageWidget



'''
    delegate that doesn't delete current editor and current item.
    intended to be subclassed.
    subclass needs call setCurrent in createEditor

'''
class persistantDelete(QStyledItemDelegate):
    
    def __init__(self,parent=None,currentIndex=QModelIndex(),currentEditor=None):
        super().__init__(parent)    
        self.current = (currentEditor,currentIndex)
        
   
    
    def setCurrent(self,currentIndex,currentEditor):
        new = (currentEditor,currentIndex)
        
        if new != self.current:
            self.destroyEditor(self.current[0],self.current[1])#destroy old editor
            self.current = new
    
        
   
       
    def destroyEditor(self,editor,index):
        if (editor,index) != self.current:
            super().destroyEditor(editor,index)





class chainageDelegate(QStyledItemDelegate):
    
    
    
    def __init__(self,parent=None,model=None,row=None,excess=0):
        super().__init__(parent)
        
        self.model = model
        self.row = row
        self.excess = excess
        
        
        
    def createEditor(self,parent,option,index):
        w = chainageWidget.chainageWidget(parent=parent,model=self.model,row=self.row,excess=self.excess)
        w.valueChanged.connect(lambda:self.setModelData(w,index.model(),index))#w deactivated by clicking map so setModelData not called?
        #self.setCurrent(index,w)
        return w
    

    def setModelData(self,editor,model,index):
        model.setData(index,editor.value())
    
    
    def setEditorData(self,editor, index):
        editor.setValue(index.data())
    
    
    
    
    #clicking map caused widget to lose focus.
    
    def setModel(self,model):
        self.model = model
        
        
    def setRow(self,row):
        self.row = row
        
        