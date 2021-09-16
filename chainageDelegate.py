from PyQt5.QtWidgets import QStyledItemDelegate,QUndoCommand,QStyledItemDelegate

from PyQt5.QtCore import QModelIndex

import logging
logger = logging.getLogger(__name__)

from . import chainageWidget



class chainageDelegate(QStyledItemDelegate):
    
    '''
    model=model with network
    row=current row of model
    excess=excess for chainageWidget
    '''
    
    def __init__(self,parent=None,geometry=None,sectionLength=None,excess=50):
        super().__init__(parent)
       # super(chainageDelegate,self).__init__(parent=parent,undoStack=undoStack)
        
        self.geometry = geometry
        self.sectionLength = sectionLength
        self.excess = excess
        
        
    def createEditor(self,parent,option,index):
        return chainageWidget.chainageWidget(parent=parent,geometry=self.geometry,sectionLength=self.sectionLength,excess=self.excess)
    

    def setEditorData(self,editor,index):
        editor.setIndex(index)


    def setModelData(self,editor,model,index):
        logging.info('setModelData(%s)'%(index.data()))
        model.setData(index,editor.value())
        


    def setSection(self,geometry,sectionLength):
        logger.info('setSection')
        self.geometry = geometry
        self.sectionLength = sectionLength