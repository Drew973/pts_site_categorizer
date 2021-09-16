from PyQt5.QtSql import QSqlTableModel

from qgis.core import QgsProject,QgsGeometry,QgsCoordinateTransform,QgsCoordinateReferenceSystem




from PyQt5.QtCore import Qt
# geom in osgb 27700

import psycopg2


def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())
    
class networkModel(QSqlTableModel):
    
    def __init__(self,db,parent=None):
        super(networkModel,self).__init__(db=db,parent=parent)
        self.setTable('categorizing.network')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setSort(self.fieldIndex('sec'),Qt.AscendingOrder)
        self.currentRow = None
        self.select()
        
         

#returns 1st row omdex where col=val
    def find(self,col,val):
        for r in range(0,self.rowCount()):
            if self.index(r, col).data()==val:
                return r
        #return row index of sec    
    
    
    
    def sectionLength(self,row=None):
        
        if row is None:
            if not self.currentRow is None:
                row = self.currentRow
                
                
        return self.index(row,self.fieldIndex('meas_len')).data()
    
    
    def geom(self,row=None):
        if row is None:
            if not self.currentRow is None:
                row = self.currentRow
                
        return QgsGeometry.fromWkt(self.index(row,self.fieldIndex('wkt')).data())
    
    

    def get(self,row,col):
        if isinstance(col,str):
            col = self.fieldIndex(col)
        
        return self.index(row,col).data()

#key like (row,col)
   # def __getitem__(self,key):
    #    self.index(key,c).data()
        

        
if __name__=='__console__':
    from PyQt5.QtSql import QSqlDatabase
    db = QSqlDatabase.addDatabase('QPSQL','site cat test')
    db.setHostName('192.168.5.157')
    db.setDatabaseName('pts2157-02_blackburn')
    db.setUserName('stuart')
    print(db.open())

    m = networkModel(db)
   # v = QTableView()
   # v.setModel(m)
   # v.show()