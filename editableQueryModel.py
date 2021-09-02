
from PyQt5.QtSql import QSqlDatabase,QSqlQueryModel,QSqlQuery
from PyQt5.QtCore import Qt
    
    
class editableQueryModel(QSqlQueryModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.queries = {}
        
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


    def database(self):
        return self.db
    
    
    def setUpdateQuery(self,col,query,bindCols,colPlaceholder=None):
        col = self.fieldIndex(col)
        
        if colPlaceholder:
            query = query.replace(colPlaceholder,self.fieldName(col))
    
        self.queries[col] = {'query':query,'bindCols':bindCols}


    #update categorizing.other_events set :col=:value where pk=:pk
    def updateQueriesFromPk(self,query,pkCol,cols=[]):
        pkCol = self.fieldIndex(pkCol)
        
        if not cols:
            cols = [i for i in range(self.columnCount()) if not i==pkCol]
            
        self.setUpdateQuery(i,query,)
        

    def select(self):
        self.setQuery(query=self.query().executedQuery(),database=self.database())


    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            
            col = index.column()
            if col in self.queries:
                
                #print(self.queries[col]['query'])
                q = QSqlQuery(self.database())#tries to execute immediately if specify text
                q.prepare(self.queries[col]['query'])
                
                q.bindValue(':value',value)
                
                bindings = self.queries[col]['bindCols']
                
                for k in bindings:
                    q.bindValue(k,index.sibling(index.row(),self.fieldIndex(bindings[k])).data())
                
                #print(q.boundValues())
                result = q.exec()
                
                if result:
                    self.select()
                    return result
                        
                print(q.executedQuery())
                print(q.lastError().text())
                    
        return QSqlQueryModel.setData(self, index, value, role)
        #return False

  #model.index(0, 0).data()
  
  
    def flags(self, index):
        fl = QSqlQueryModel.flags(self, index)
        if index.column() in self.queries:
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

    model =  editableQueryModel()
    model.setQuery("SELECT sec,reversed,s_ch,e_ch,category,pk from categorizing.other_events order by pk",database=db)
    
    model.setUpdateQuery(col=1,query='update categorizing.other_events set :col=:value where pk=:pk',bindCols={':pk':'pk'},colPlaceholder=':col')

    view =  QTableView()

    view.setModel(model)
    view.show()
    
    
    