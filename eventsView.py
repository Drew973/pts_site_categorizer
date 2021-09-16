from PyQt5.QtWidgets import QTableView,QMenu,QStyledItemDelegate,QAction
from PyQt5.QtCore import Qt

import logging

logger = logging.getLogger(__name__)

from . import commands,chainageWidget,chainageDelegate,otherEventsModel


#parent has getSec()
#parent has undoStack

class eventsView(QTableView):
    
    
    def __init__(self,parent):
        super().__init__(parent)
        
        self.menu = QMenu(self)
        self.dropAct = self.menu.addAction('drop selected rows')
        self.dropAct.triggered.connect(self.dropSelectedRows)
        

        
        
        #dropAct.triggered.connect(self.otherEventsRemove)

        #setChAct = self.jc_menu.addAction('set chainage from selected rows.')
       # setChAct.triggered.connect(self.setCh)

        self.setContextMenuPolicy(Qt.CustomContextMenu);
        #self.jcView.customContextMenuRequested.connect(lambda pt:self.jc_menu.exec_(self.mapToGlobal(pt)))
        self.customContextMenuRequested.connect(lambda pt:self.menu.exec_(self.mapToGlobal(pt)))
        
        self.undoStack = None
        
        #self.cw = chainageWidget.chainageWidget(parent=self)
        self.delegate = chainageDelegate.chainageDelegate(excess=50)
        
        
    def connectToDatabase(self,db):
        if db.isOpen():
            self.setModel(otherEventsModel.otherEventsModel(db=db,parent=self,undoStack=self.undoStack))
        else:
             self.setModel(None)        
        
        
    def setSection(self,sec,geometry,sectionLength):
        if not self.model() is None:
            self.model().setSec(sec) 
            self.delegate.setSection(geometry,sectionLength)
            
        
    def setUndoStack(self,undoStack):
        self.undoStack = undoStack
    
        
    def runUndoCommand(self,command):
        if self.undoStack is None:
            command.redo()
        else:
            self.undoStack.push(command)
        
        
    def fieldIndex(self,v):
        return self.model().fieldIndex(v)
    
        
    def setModel(self,model):
        super().setModel(model)
         
        if model:
            self.hideColumn(self.fieldIndex('pk'))
            self.hideColumn(self.fieldIndex('sec'))
            self.hideColumn(self.fieldIndex('geom'))
            self.setEnabled(True)
            self.setItemDelegateForColumn(self.fieldIndex('s_ch'),self.delegate)
            self.setItemDelegateForColumn(self.fieldIndex('e_ch'),self.delegate)
        
        else:
            self.setEnabled(False)
        
    
    #move to undoableTableModel
    def dropSelectedRows(self):
        logger.info('dropSelectedRows()')

        if self.model():
            pkCol = self.fieldIndex('pk')
            pks = [index.sibling(index.row(),pkCol).data() for index in self.selectedIndexes()]
            self.runUndoCommand(commands.deleteCommand(model=self.model(),pks=pks,description='delete selected rows'))
            
