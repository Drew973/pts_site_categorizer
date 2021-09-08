import logging
logger = logging.getLogger(__name__)


from PyQt5.QtWidgets import QUndoCommand,QStyledItemDelegate


def getValue(widget):
    return widget.property(widget.metaObject().userProperty().name())
    

def setValue(widget,value):
    widget.setProperty(widget.metaObject().userProperty().name(),value)

'''
    command to update model.
    Uses a primary key rather than index to aviod problems with deleted indexes
    eg after QSqlTableModel.select()
    model needs indexToPk(index) and pkToIndex(pk,col) methods
'''
    
class updateCommandPk(QUndoCommand):

    def __init__(self,index,description='update'):
        super().__init__(description)
        self.model = index.model()
        self.col = index.column()
        self.pk = index.model().indexToPk(index)
        self.oldValue = index.data()


    def redo(self):
        self.model.setData(self.model.pkToIndex(self.pk,self.col),self.newValue)


    def undo(self):
        logger.info('updateCommandPk.undo')
        self.model.setData(self.model.pkToIndex(self.pk,self.col),self.oldValue)


    def setNewValue(self,value):
        self.newValue = value
        
        
        
class undoDelegatePk(QStyledItemDelegate):
 
    def __init__(self,undoStack,parent=None):
        super().__init__(parent)
        self.undoStack = undoStack


    def createEditor(self,parent,option,index):
        w = super().createEditor(parent,option,index)
        w.updateCommand = updateCommandPk(index)
        return w
    

    def setModelData(self,editor,model,index):
        editor.updateCommand.setNewValue(getValue(editor))
        self.undoStack.push(editor.updateCommand)
    
    
    def setEditorData(self,editor, index):
        setValue(editor,index.data())

