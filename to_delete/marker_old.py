from qgis.gui import QgsVertexMarker,QgsMapToolEmitPoint
from qgis.PyQt.QtGui import QCursor,QColor
from qgis.core import QgsPointXY
from qgis.utils import iface
import inspect 

class chainage_tool():
    def __init__(self,button,spinbox,layer,pi):
        button.clicked.connect(self.from_click)
        self.marker=None
        self.sec=None
        self.spinbox=spinbox
        self.spinbox.valueChanged.connect(self.set_ch)
        self.pi=pi
        self.layer=layer
        self.map_tool=QgsMapToolEmitPoint(iface.mapCanvas())
        
    def from_click(self):
        self.map_tool=QgsMapToolEmitPoint(iface.mapCanvas())
        iface.mapCanvas().setMapTool(self.map_tool)
        self.map_tool.canvasClicked.connect(self.ch_from_point)


    def ch_from_point(self,point):
        #make sure in layer crs ie osgb36
        p=self.map_tool.toLayerCoordinates(layer=self.layer,point=point) #convert from screen to osgb.
        q=self.pi.get_query("select xy_to_ch(%s,%s,%s) as ch",[self.sec,p.x(),p.y()])
        ch=int(q[0]['ch'])
        self.spinbox.setValue(ch)
        self.set_ch(ch)


    def set_sec(self,sec):
        if sec!=self.sec:
            self.sec=sec
            self.spinbox.setValue(0)
            self.sec_len=self.pi.get_query("select sec_len(%s)",[self.sec])[0]['sec_len']    
            self.spinbox.setMaximum(self.sec_len+50)
            self.set_ch(0)


    def set_ch(self,ch):
        self.redraw(self.sec,ch)

    
    def redraw(self,sec,c):
        if not self.sec is None:

            if self.marker:
                iface.mapCanvas().scene().removeItem(self.marker)
            ch=c
            if c>self.sec_len:
                ch=self.sec_len
            if c<0:
                c=0    
            
           # print(p[0]['x'],p[0]['y'])
            self.marker=QgsVertexMarker(iface.mapCanvas())
            p=self.pi.get_query("select ST_X(ch_to_point(%s,%s)) as x,ST_y(ch_to_point(%s,%s)) as y",[self.sec,c,self.sec,c])
            
           # p1=self.map_tool.toCanvasCoordinates(layer=self.layer,point=QgsPointXY(p[0]['x'],p[0]['y']))#convert point from osgb crs to map coordinates.
            
            p1=self.map_tool.toMapCoordinates(layer=self.layer,point=QgsPointXY(p[0]['x'],p[0]['y']))#convert from layer coords to map coords
            self.marker.setCenter(QgsPointXY(p1.x(),p1.y()))
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
                

