from PyQt5.QtSql import QSqlTableModel



class networkModel(QSqlTableModel):
    
    def __init__(self,db,parent=None):
        super(networkModel,self).__init__(db=db,parent=parent)
        self.setTable('categorizing.network')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()

        
#returns 1st row where col=val
    def find(self,col,val):
        for r in range(0,self.rowCount()):
            if self.index(r, col).data()==val:
                return r
        #return row index of sec    
    
    
    
    
    
#mapper.setCurrentModelIndex()