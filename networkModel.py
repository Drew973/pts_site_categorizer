from PyQt5.QtSql import QSqlTableModel

from qgis.core import QgsProject,QgsGeometry,QgsCoordinateTransform,QgsCoordinateReferenceSystem
from PyQt5.QtSql import QSqlDatabase

# geom in osgb 27700


class networkModel(QSqlTableModel):
    
    def __init__(self,db,parent=None):
        super(networkModel,self).__init__(db=db,parent=parent)
        self.setTable('categorizing.network')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()

       

    
#returns 1st row omdex where col=val
    def find(self,col,val):
        for r in range(0,self.rowCount()):
            if self.index(r, col).data()==val:
                return r
        #return row index of sec    
    
    
    
    def sectionLength(self,row):
        return self.index(row,self.fieldIndex('meas_len')).data()
    
    
    def geom(self,row):
        return QgsGeometry.fromWkt(self.index(row,self.fieldIndex('wkt')).data())
    
    
    #row is int
    #ch in terms of given length
    #crs is QgsCoordinateReferenceSystem to transform to
    #returns qgspointxy
    
    def chainageToPoint(self,row,chainage,crs):
        crs = QgsCoordinateReferenceSystem.fromEpsgId(27700)
        
        t = QgsCoordinateTransform(QgsCoordinateReferenceSystem.fromEpsgId(27700),crs,QgsProject.instance())#documentation says only need source and destination. lies.
            
        #transform takes qgspointxy
        g = self.geom(row)
        length = self.sectionLength(row)
        
        if chainage<=0:
            return t.transform(g.asPolyline()[0])#return start of line
    
        if chainage>=length:
            return t.transform(g.asPolyline()[-1])#return end of line
    
        return t.transform(g.interpolate(g.length()*chainage/length).asPoint())

    #crs is crs of point
    def pointToChainage(self,row,point,crs):
        t = QgsCoordinateTransform(crs,QgsCoordinateReferenceSystem.fromEpsgId(27700),QgsProject.instance())#documentation says only need source and destination. lies.
        point = t.transform(point)
        point = QgsGeometry().fromPointXY(point)
        return self.geom(row).lineLocatePoint(point)*self.sectionLength(row)/self.geom(row).length()
        
        
if __name__=='__console__':
    db = QSqlDatabase.addDatabase('QPSQL','site cat test')
    db.setHostName('192.168.5.157')
    db.setDatabaseName('pts2157-02_blackburn')
    db.setUserName('stuart')
    print(db.open())

    m = networkModel(db)
    v = QTableView()
    v.setModel(m)
    v.show()
    
    m.chToPoint(0,10,iface.mapCanvas().mapSettings())
    
    
    