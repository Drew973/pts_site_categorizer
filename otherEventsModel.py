from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

import psycopg2
import curvatures
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QUndoCommand,QUndoStack

import undoDelegate


def dbToCon(db):
   # print('user:%s'%(db.userName()))
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


class otherEventsModel(QSqlTableModel):
    
    def __init__(self,db,undoStack=None,parent=None):
        super(otherEventsModel,self).__init__(db=db,parent=parent)
        self.setTable('categorizing.other_events')
        self.setEditStrategy(QSqlTableModel.OnFieldChange) 
        self.setSort(self.fieldIndex('s_ch'),Qt.AscendingOrder)
        self.setFilter("sec=''")
        
        self.select()
        
        self.rowsInserted.connect(self.select)
        self.rowsRemoved.connect(self.select)
        self.undoStack = undoStack
        self.sec = ''


    def rowToPk(self,row):
        return self.index(row,self.fieldIndex('pk')).data()
    
    
    def indexToPk(self,index):
        return index.sibling(index.row(),self.fieldIndex('pk')).data()
     
     
    def pkToIndex(self,pk,col):
        return self.index(self.find(self.fieldIndex('pk'),pk),col)
 
 
    def pkToRow(self,pk):
        return self.find(self.fieldIndex('pk'),pk)
    
    

    def setSec(self,sec):
        
        self.sec = sec
        self.setFilter("sec='%s'"%(sec))
        self.select()

       # c = setSecCommand(self,self.sec,sec)
       # if self.undoStack:
       #     self.undoStack.push(c)
       # else:
       #     c.redo()


#returns 1st row where col=val
    def find(self,col,val):
        for r in range(0,self.rowCount()):
            if self.index(r, col).data()==val:
                return r
        #return row index of sec 
        
        
       #insert row and return pk of new row.
    def insert(self,sec,rev=False,s_ch=0,e_ch=0,category='C'):
        logger.info('insert(%s)'%(sec))
        q = 'insert into categorizing.other_events(sec,reversed,s_ch,e_ch,category) values(%s,%s,%s,%s,%s) returning pk' 

        with dbToCon(self.database()) as con:
            cur = con.cursor()
            cur.execute(q,(sec,rev,s_ch,e_ch,category))
            
        self.select()#change needs commiting before this
        return  cur.fetchone()[0] #pk of new row
    
    
    #inserts list of dict like. returns primary keys.
    def insertMany(self,vals):
        
        #insert_batch only gets last pk. need to do as 1 query
        #more efficient than insert_batch?
        with dbToCon(self.database()) as con:
            cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
            args_str = ','.join([cur.mogrify("(%(sec)s,%(rev)s,%(s_ch)s,%(e_ch)s,%(category)s)",val).decode() for val in vals])
            cur.execute("insert into categorizing.other_events(sec,reversed,s_ch,e_ch,category) VALUES "+args_str +' returning pk;')
        
        self.select()
        return [v[0] for v in cur.fetchall()]
    
    
    def delete(self,pk):
        logger.info('delete(%s)'%(pk))
        q = 'delete from categorizing.other_events where pk=%(pk)s RETURNING sec,reversed as rev,s_ch,e_ch,category'
        
        with dbToCon(self.database()) as con:
            cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
            cur.execute(q,{'pk':pk})
        
        self.select()#commit changes before this
        return cur.fetchone()
    
    
    def deleteMany(self,pks):
        q = 'delete from categorizing.other_events where pk = any(%(pks)s::int[]) RETURNING sec,reversed as rev,s_ch,e_ch,category'
        
        pks = ','.join([str(pk) for pk in pks])
        pks='{'+pks+'}'
        
        with dbToCon(self.database()) as con:
            cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
            cur.execute(q,{'pks':pks})
            
        self.select()#commit changes before this
        return cur.fetchall()
#dictcursor result is displayed like list

    
    def autoCurvatures(self,row,networkModel,plot=False):
        
        speed = float(networkModel.get(row,'speed_limit'))
        sec = networkModel.get(row,'sec')
        length = networkModel.get(row,'meas_len')
        geom = networkModel.geom(row)
        geomLen = geom.length()
        
        if speed>=50:
            pieces = curvatures.getPieces(geom,500)
            print(pieces)
            pieces = [p for p in pieces if not (p.length()<100 and p.min()>250)]
            
        else:
            pieces = curvatures.getPieces(geom,100)

        with dbToCon(self.database()) as con:
            q='select categorizing.add_curvature(%(sec)s,%(start)s,%(end)s)'
            con.cursor().executemany(q,[{'sec':sec,'start':length*p.start/geomLen,'end':length*p.end/geomLen} for p in pieces])
            
            #convert distance to network chainage
        
        self.select()
        
        if plot:
            i = curvatures.sectionInterpolator(geom)
            plt.close()
            i.plot()
            plt.show(block=False)
            


    

if __name__=='__console__':
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
    m = otherEventsModel(db,undoStack=u)
    m.setSec('5010A000677 /00020')
    v.setModel(m)
    
    delegate = undoDelegate.undoDelegatePk(u)
    v.setItemDelegate(delegate)
    v.show()
    
    
   # data = [{'sec':'5010A000677 /00020','rev':False,'s_ch':0, 'e_ch':0, 'category':'C'}]
    #data.append({'sec':'5010A000677 /00020','rev':False,'s_ch':0, 'e_ch':0, 'category':'C'})
    
   # print(m.insertMany(data))
  
    
  
    
  