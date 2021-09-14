from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand,QTableView,QUndoStack


'''
command to update QSqlTableModel.
uses primary key(s) to find index and calls QSqlTableModel.setData()
'''
class updateCommand(QUndoCommand):

    def __init__(self,index,value,description='update',parent=None):
        super().__init__(description,parent)
        self.model = index.model()
        self.column = index.column()
        #self.pk = index.model().indexToPk(index)
        self.oldValue = index.data()
        self.newValue = value
        self.primaryVals = index.model().primaryValues(index.row())#values of primary key


    def redo(self):
        index = self.index()
        self.model.setDataCommandLess(index,self.newValue)
        self.primaryVals = index.model().primaryValues(index.row())#might change primary values


    def undo(self):
        index = self.index()
        self.model.setDataCommandLess(index,self.oldValue)
        self.primaryVals = index.model().primaryValues(index.row())#might change primary values


#gets model index from self.primaryVals
    def index(self):
        for i in range(self.model.rowCount()):
            if self.model.primaryValues(i)==self.primaryVals:
                return self.model.index(i,self.column)


class undoableTableModel(QSqlTableModel):
    
    def __init__(self,parent,db,undoStack):
        super().__init__(parent,db)
        self.undoStack = undoStack


#calls QSqlTableModel.setData()
    def setDataCommandLess(self, index, value, role=Qt.EditRole):
        super().setData(index, value,role)

    
    #parent is parent for QUndoCommand to push
    def setData(self, index, value, role=Qt.EditRole,parent=None,description=''):
        if role == Qt.EditRole:
            
            c = updateCommand(index,value,description=description,parent=parent)
            
            if self.undoStack is None:
                c.redo()
            else:
                self.undoStack.push(c)
            
            return True
        
        return QSqlTableModel.setData(self, index, value, role)
 
 
if __name__=='__console__' or __name__=='__main__':
    from PyQt5.QtSql import QSqlDatabase
    QSqlDatabase.removeDatabase('site cat test')
    db = QSqlDatabase('QPSQL')
    db.close()
    db.setHostName('192.168.5.157')
    db.setDatabaseName('pts2157-02_blackburn')
    db.setUserName('stuart')
    print(db.open())

    v = QTableView()
    
    u = QUndoStack()
    m = undoableTableModel(parent=v,db=db,undoStack=u)
    m.setTable('categorizing.other_events')
    m.setEditStrategy(QSqlTableModel.OnFieldChange) 
    m.setSort(m.fieldIndex('sec'),Qt.AscendingOrder)
    m.select()
    
    v.setModel(m)
    
    v.show()