from qgis.gui import QgsVertexMarker
from PyQt5.QtWidgets import QGraphicsItem


class movableMarker(QgsVertexMarker):

    def __init__(self,canvas):
        super(QgsVertexMarker,self).__init__(canvas)
        
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        
        
if __name__=='__console__':
    
    m = movableMarker(iface.mapCanvas())
    m.setIconSize(15)
    m.setIconType(QgsVertexMarker.ICON_X)
    m.setColor(QColor(255,0,0))
    m.setPenWidth(4) 
    m.setCenter(QgsPointXY(-267974,7112933))
    m.show()
    m.updateCanvas()
    
    
    