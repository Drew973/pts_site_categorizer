from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import QModelIndex

import logging
logger = logging.getLogger(__name__)

from . import chainageWidget
from . import undoDelegate



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





class chainageDelegate(undoDelegate.undoDelegatePk):
    
    
    '''
    model=model with network
    row=current row of model
    excess=excess for chainageWidget
    '''
    def __init__(self,undoStack,parent=None,model=None,row=None,excess=0):
        super(chainageDelegate,self).__init__(parent=parent,undoStack=undoStack)
        
        self.model = model
        self.row = row
        self.excess = excess
        
        
    def createEditor(self,parent,option,index):
        w = chainageWidget.chainageWidget(parent=parent,model=self.model,row=self.row,excess=self.excess)
        w.updateCommand = undoDelegate.updateCommandPk(index)
        #w.valueChanged.connect(lambda:self.setModelData(w,index.model(),index))#w deactivated by clicking map so setModelData not called?
        #don't 
        return w
    

    def setEditorData(self,editor,index):
        #editor.setValue(index.data())
        editor.setIndex(index)


    def setModelData(self,editor,model,index):
        logging.info('setModelData(%s)'%(index.data()))
        model.setData(index,editor.value())
        
    
    #clicking map caused widget to lose focus.
    
    def setModel(self,model):
        logger.info('setModel')
        self.model = model
        
        
    def setRow(self,row):
        self.row = row
        
        