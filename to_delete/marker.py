from qgis.gui import QgsVertexMarker,QgsMapToolEmitPoint
from qgis.PyQt.QtGui import QCursor,QColor
from qgis.core import QgsPointXY
from qgis.utils import iface
import inspect 

class chainage_tool():
    def __init__(self,button,spinbox,pi):
        button.clicked.connect(self.from_click)
        self.marker=None
        self.sec=None
        self.spinbox=spinbox
        self.spinbox.valueChanged.connect(self.set_ch)
        self.pi=pi
        self.map_tool=QgsMapToolEmitPoint(iface.mapCanvas())

        
    def from_click(self):
        self.map_tool=QgsMapToolEmitPoint(iface.mapCanvas())
        iface.mapCanvas().setMapTool(self.map_tool)
        self.map_tool.canvasClicked.connect(self.ch_from_point)


    def ch_from_point(self,point):
        q=self.pi.get_query("select xy_to_ch(%s,%s,%s,%s) as ch",[self.sec,point.x(),point.y(),self.crs()])
        self.set_ch(int(q[0]['ch']))


    def set_sec(self,sec):
        if sec!=self.sec:
            self.sec=sec
            self.spinbox.setValue(0)
            self.sec_len=self.pi.get_query("select sec_len(%s)",[self.sec])[0]['sec_len']    
            self.spinbox.setMaximum(self.sec_len+50)
            self.set_ch(0)


    def set_ch(self,ch):
        self.spinbox.setValue(ch)
        self.redraw(self.sec,ch)


    def crs(self):
        return int(iface.mapCanvas().mapSettings().destinationCrs().authid()[5:])

        
    def redraw(self,sec,c):
        if not self.sec is None:
            if self.marker:
                iface.mapCanvas().scene().removeItem(self.marker)
            ch=c
            if c>self.sec_len:
                ch=self.sec_len
            if c<0:
                c=0    
            self.marker=QgsVertexMarker(iface.mapCanvas())
            q=self.pi.get_query('select st_x(p),st_y(p) from ST_Transform(ch_to_point(%s,%s),%s) as p',[self.sec,c,self.crs()])
            p=QgsPointXY(q[0]['st_x'],q[0]['st_y'])
            self.marker.setCenter(p)#marker at point
            self.marker.updatePosition()
            self.marker.setIconSize(15)
            self.marker.setIconType(QgsVertexMarker.ICON_X)
            self.marker.setColor(QColor(255,0,0))
            self.marker.setPenWidth(4)        
            self.marker.updateCanvas()
            self.marker.show()


    def remove(self):
         if self.marker:
                iface.mapCanvas().scene().removeItem(self.marker)
