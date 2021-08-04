from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

import psycopg2


def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())




class jcModel(QSqlTableModel):
    
    def __init__(self,db,parent=None):
        super(jcModel,self).__init__(db=db,parent=parent)
        self.setTable('categorizing.jc')
        self.setEditStrategy(QSqlTableModel.OnFieldChange) 
        self.setSort(self.fieldIndex('ch'),Qt.AscendingOrder)
        self.setFilter("sec=''")
        
        self.select()
        

        

    def setSec(self,sec):
        self.setFilter("sec='%s'"%(sec))
        self.select()


#returns 1st row where col=val
    def find(self,col,val):
        for r in range(0,self.rowCount()):
            if self.index(r, col).data()==val:
                return r
        #return row index of sec 
        
        
        
        
    def add(self,sec,ch,cat):
        with dbToCon(self.database()) as con:
            con.cursor().execute('insert into categorizing.jc(sec,ch,category,geom) values (%(sec)s,%(ch)s,%(cat)s,categorizing.ch_to_point(%(sec)s,%(ch)s))',{'sec':sec,'ch':ch,'cat':cat})
            con.cursor().execute('select categorizing.process(%(sec)s)',{'sec':sec})
        self.select()
        
        
        
    def process(self,sec,cur=None):
        with dbToCon(self.database()) as con:
            con.cursor().execute('select categorizing.process(%(sec)s)',{'sec':sec})
            