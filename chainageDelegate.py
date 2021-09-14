from PyQt5.QtWidgets import QStyledItemDelegate,QUndoCommand,QStyledItemDelegate

from PyQt5.QtCore import QModelIndex

import logging
logger = logging.getLogger(__name__)

from . import chainageWidget
from . import undoDelegate



class chainageDelegate(QStyledItemDelegate):
    
    '''
    model=model with network
    row=current row of model
    excess=excess for chainageWidget
    '''
    
    def __init__(self,parent=None,model=None,row=None,excess=0,undoStack = None):
        super().__init__(parent)
       # super(chainageDelegate,self).__init__(parent=parent,undoStack=undoStack)
        
        self.model = model
        self.row = row
        self.excess = excess
        self.undoStack = undoStack
        
        
    def createEditor(self,parent,option,index):
        w = chainageWidget.chainageWidget(parent=parent,model=self.model,row=self.row,excess=self.excess)
        w.updateCommand = undoDelegate.updateCommandPk(index)
        #w.valueChanged.connect(lambda:self.setModelData(w,index.model(),index))#w deactivated by clicking map so setModelData not called?
        return w
    

    def setEditorData(self,editor,index):
        #editor.setValue(index.data())
        editor.setIndex(index)


    def setModelData(self,editor,model,index):
        logging.info('setModelData(%s)'%(index.data()))
        #model.setData(index,editor.value())
        
        editor.updateCommand.setNewValue(editor.value())
        
        if not self.undoStack is None:
            self.undoStack.push(editor.updateCommand)
        
        else:
            editor.updateCommand.redo()
        
    
    #clicking map caused widget to lose focus.
    
    #model with network
    def setModel(self,model):
        logger.info('setModel')
        self.model = model
        
        
    # row of network model
    def setRow(self,row):
        self.row = row
        
        
   # def setUndoStack
        