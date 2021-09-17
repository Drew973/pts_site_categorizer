from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

import psycopg2
import curvatures
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QUndoCommand,QUndoStack

from . import undoableTableModel,commands


def dbToCon(db):
   # print('user:%s'%(db.userName()))
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


COLS = ['sec','s_ch','e_ch','category']

class otherEventsModel(undoableTableModel.undoableTableModel):
    
    def __init__(self,db,undoStack,parent=None):
        super().__init__(db=db,parent=parent,undoStack=undoStack)
        self.setTable('categorizing.events')
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

    
    def pkToRow(self,pk):
        return self.find(self.fieldIndex('pk'),pk)

    
    def indexToPk(self,index):
        return index.sibling(index.row(),self.fieldIndex('pk')).data()
     
     
    def pkToIndex(self,pk,col):
        return self.index(self.find(self.fieldIndex('pk'),pk),col) 
    

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
        
        
    #inserts list of dict like.
   # [{sec,rev,s_ch,e_ch,category}]
   # returns primary keys.
    def insert(self,vals):
        if not vals:
            return []
        
        #insert_batch only gets last pk. doing as 1 query
        #more efficient than insert_batch?
        with dbToCon(self.database()) as con:
            cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
            a = ','.join(['%('+col+')s' for col in COLS ])
            logger.info(a)
            args_str = ','.join([cur.mogrify("("+a+")",val).decode() for val in vals])
            q = "insert into categorizing.events(%s) VALUES %s returning pk;"%(','.join(COLS),args_str)
            cur.execute(q)
                    
        self.select()
        return [v[0] for v in cur.fetchall()]
    
    
    def delete(self,pks):
        q = 'delete from categorizing.events where pk = any(%(pks)s::int[]) RETURNING ' + ','.join(COLS)
        
        pks = ','.join([str(pk) for pk in pks])
        pks='{'+pks+'}'
        
        with dbToCon(self.database()) as con:
            cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
            cur.execute(q,{'pks':pks})
            
        self.select()#commit changes before this
        return cur.fetchall()
#dictcursor result is displayed like list

    
#add event using default values
    def insertDefault(self):
         if self.sec:
             self.runUndoCommand(commands.insertCommand(model=self,
                data=[{'sec':self.sec,'rev':False,'s_ch':0,'e_ch':0,'category':'C'}],description='add empty row'))
            


    def autoCurvatures(self,row,networkModel,plot=False):
        logger.info('autoCurvatures(%s,%s%s)',str(row),str(networkModel),str(plot))
        
        speed = float(networkModel.get(row,'speed_limit'))
        
        sec = networkModel.get(row,'sec')
        secLength = networkModel.get(row,'meas_len')
        
        geom = networkModel.geom(row)
        geomLen = geom.length()
        
        if speed>=50:
            pieces = curvatures.getPieces(geom,500)
            pieces = [p for p in pieces if not (p.length()<100 and p.min()>250)]
            
        else:
            pieces = curvatures.getPieces(geom,100)
        
        #S1 for 1 way, S2 for 2 way
            
        if networkModel.get(row,'one_way'):
            d = [{'sec':sec,'rev':False,'category':'S1','s_ch':p.start*secLength/geomLen,'e_ch':p.end*secLength/geomLen} for p in pieces]
        else:
            d = [{'sec':sec,'rev':False,'category':'S2','s_ch':p.start*secLength/geomLen,'e_ch':p.end*secLength/geomLen} for p in pieces]
            d += [{'sec':sec,'rev':True,'category':'S2','e_ch':p.start*secLength/geomLen,'s_ch':p.end*secLength/geomLen} for p in pieces]
        
        self.runUndoCommand(commands.insertCommand(model=self,data=d,description='recalculate curvatures'))
        
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
    
    v.show()
    
    
   # data = [{'sec':'5010A000677 /00020','rev':False,'s_ch':0, 'e_ch':0, 'category':'C'}]
    #data.append({'sec':'5010A000677 /00020','rev':False,'s_ch':0, 'e_ch':0, 'category':'C'})
    
   # print(m.insertMany(data))