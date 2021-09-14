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
    
    def __init__(self,parent=None,model=None,row=None,excess=0):
        super().__init__(parent)
       # super(chainageDelegate,self).__init__(parent=parent,undoStack=undoStack)
        
        self.model = model
        self.row = row
        self.excess = excess
        
        
    def createEditor(self,parent,option,index):
        return chainageWidget.chainageWidget(parent=parent,model=self.model,row=self.row,excess=self.excess)
    

    def setEditorData(self,editor,index):
        editor.setIndex(index)


    def setModelData(self,editor,model,index):
        logging.info('setModelData(%s)'%(index.data()))
        model.setData(index,editor.value())
        

    #clicking map caused widget to lose focus.
    #model with network
    def setModel(self,model):
        logger.info('setModel')
        self.model = model
        
        
    # row of network model
    def setRow(self,row):
        self.row = row