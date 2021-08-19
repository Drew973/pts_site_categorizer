from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

import psycopg2


def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())




class otherEventsModel(QSqlTableModel):
    
    def __init__(self,db,parent=None):
        super(otherEventsModel,self).__init__(db=db,parent=parent)
        self.setTable('categorizing.other_events')
        self.setEditStrategy(QSqlTableModel.OnFieldChange) 
        self.setSort(self.fieldIndex('s_ch'),Qt.AscendingOrder)
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
        
        
        
    def add(self,sec,rev=False,s_ch=0,e_ch=0,category='C'):
        q = 'insert into categorizing.other_events(sec,reversed,s_ch,e_ch,category) values(%s,%s,%s,%s,%s)'        

        with dbToCon(self.database()) as con:
            con.cursor().execute(q,(sec,rev,s_ch,e_ch,category))
        self.select()