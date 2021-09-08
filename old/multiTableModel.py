from PyQt5.QtSql import QSqlDatabase,QSqlQueryModel,QSqlQuery
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoCommand,QUndoStack

#run qsqlQuery and raise error if failed
def runQuery(q):
    if q.exec():
        return True
    raise ValueError('update query failed. query %s,values:%s,error:'%(q.executedQuery(),q.boundValues(),qlastError().text()))

    
def generateUpdateQuery(database,table,pkCol,pk,valueCol,value):
    q = QSqlQuery(database)#tries to execute immediately if specify text
    text = 'update %s set %s = :value where %s=:pk'%(table,valueCol,pkCol)
    q.prepare(text)
    q.bindValue(':value',value)
    q.bindValue(':pk',pk)
    return q
    
    
class updateCommand(QUndoCommand):

    def __init__(self, database,table,pkCol,pk,valueCol,oldValue,newValue,model=None,description='update'):
        super(updateCommand, self).__init__(description)
        
        self.query = generateUpdateQuery(database,table,pkCol,pk,valueCol,newValue)
        self.inverse = generateUpdateQuery(database,table,pkCol,pk,valueCol,oldValue)
        self.model = model

    def redo(self):
        runQuery(self.query)
        if self.model:
            self.model.select()
        
    def undo(self):
        runQuery(self.inverse)
        if self.model:
            self.model.select()
    

'''
requirements:
column names unique
column names in source tables same as model
'''
class multiTableModel(QSqlQueryModel):
    
    def __init__(self,parent=None,undoStack=None):
        super().__init__(parent)
        self.sources = {}
        self.undoStack = undoStack
        
    #which column of model mapped to field of table
    def fieldIndex(self,field):
        if isinstance(field,int):
            return field
        return self.record().indexOf(field)
        
 
    def fieldName(self,column):
        return self.record().field(column).name()


#this disables setQuery(query)
    def setQuery(self,query,database):
        self.db = database
        super().setQuery(query,database)


    #QUndoStack to push changes to
    def setUndoStack(self,undoStack):
        self.undoStack = undoStack


    def database(self):
        return self.db
    
    '''
    sets source for cols.
    leave cols unset to set source for all columns
    pkCol is column of table. pkCol is column with primary key. assumed to have same name in model.
    update table set col=value
    '''
    def setSource(self,table,pkCol,cols=[]):
        pkCol = self.fieldIndex(pkCol)
        
        if not cols:
            cols = [i for i in range(self.columnCount())]
        #to integers
        
        cols = [self.fieldIndex(col) for col in cols]
        
        cols = [col for col in cols if not col==pkCol]#don't want pk col to be editable
        
        for col in cols:
            self.sources[col]={'table':table,'pkCol':pkCol}
            

    def select(self):
        self.setQuery(query=self.query().executedQuery(),database=self.database())


    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            col = index.column()
            if col in self.sources:
                s = self.sources[col]
                
                c = updateCommand(database=self.database(),
                    table=s['table'],
                    pkCol='pk',
                    pk=index.sibling(index.row(),s['pkCol']).data(),
                    valueCol=self.fieldName(col),
                    oldValue=index.data(),
                    newValue=value,
                    model=self)
                
                if self.undoStack:
                    self.undoStack.push(c)
                else:
                    c.redo()
                
                self.select()
                return True
                    
        return QSqlQueryModel.setData(self, index, value, role)

  #model.index(0, 0).data()
  
  
    def flags(self, index):
        fl = QSqlQueryModel.flags(self, index)
        if index.column() in self.sources:
            fl |= Qt.ItemIsEditable
        return fl
    
    
if __name__=='__console__':
    
    QSqlDatabase.removeDatabase('site cat test')
    db = QSqlDatabase('QPSQL')
    db.close()
    db.setHostName('192.168.5.157')
    db.setDatabaseName('pts2157-02_blackburn')
    db.setUserName('stuart')
    print('connected:',str(db.open()))

    model =  multiTableModel()
    model.setQuery("SELECT sec,reversed,s_ch,e_ch,category,pk from categorizing.other_events order by pk",database=db)
    
    model.setSource(table='categorizing.other_events',pkCol='pk')
    undoStack = QUndoStack()
    model.setUndoStack(undoStack)
    view =  QTableView()

    view.setModel(model)
    view.show()
    
    #q = generateUpdateQuery(db,'categorizing.other_events','pk',4230,'reversed',True)
    #q = generateUpdateQuery(db,'categorizing.other_events','pk',4230,'reversed',False)
    
    