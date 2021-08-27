from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

import psycopg2
import curvatures
import matplotlib.pyplot as plt



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
            
            