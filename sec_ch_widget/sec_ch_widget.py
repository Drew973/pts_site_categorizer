from qgis.gui import QgsMapToolEmitPoint,QgsVertexMarker#,gsVertexMarker
from qgis.PyQt.QtGui import QColor

from qgis.PyQt.QtWidgets import QWidget,QCompleter
from PyQt5.QtCore import QStringListModel,pyqtSignal

from qgis.core import QgsPointXY,QgsFieldProxyModel,QgsMapLayerProxyModel,QgsFeatureRequest,QgsGeometry#QgsPoint
from qgis.utils import iface


from .sec_ch_base import Ui_Form

from . import layer_functions

#subclassing QgsMapToolEmitPoint because toMapCoordinates is private in qgis 2.           
class mt(QgsMapToolEmitPoint):            
    def to_map_coords(self,layer,point):
        return self.toMapCoordinates(layer=layer,point=point)
        


class sec_ch_widget(Ui_Form,QWidget):
    sec_changed = pyqtSignal(str,name='sec_changed')
    
    def __init__(self,parent,dd):
        super(sec_ch_widget,self).__init__(parent)
        
        self.setupUi(self)
        #self.from_click_button.clicked.connect(self.from_click)
        #self.from_click.stateChanged.connect(self.from_click_toggled)
        self.marker=None
        self.sec=None
        self.ch_box.valueChanged.connect(self.set_ch)
               
        self.layer_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.sec_field_box,name='sec'))
        self.layer_box.layerChanged.connect(lambda layer:set_to(layer=layer,fb=self.len_field_box,name='meas_len'))
        
        self.sec_field_box.fieldChanged.connect(self.field_changed)
        self.dd=dd
        
        self.go_to_button.clicked.connect(self.set_sec)
        self.sec_edit.textChanged.connect(self.set_sec)
        self.ch_box.setMinimum(-50)
        self.from_layer_button.clicked.connect(self.from_layer)

        self.layer_box.setFilters(QgsMapLayerProxyModel.LineLayer)
        
        self.sec_field_box.setFilters(QgsFieldProxyModel.String)

        set_layer_box_to(self.layer_box,'network')

        self.map_tool=mt(iface.mapCanvas())
        self.map_tool.canvasClicked.connect(self.ch_from_point)
        
        self.from_click_button.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.map_tool,clean=True))


    def ch_from_point(self,pt):
        self.set_ch(int(pt_to_ch(pt,sec=self.sec,
                                 sec_field=self.sec_field_box.currentField(),
                                 len_field=self.len_field_box.currentField(),
                                 layer=self.layer_box.currentLayer()
                                 )))


    def crs(self):
        return int(iface.mapCanvas().mapSettings().destinationCrs().authid()[5:])


    def set_sec(self,sec=None):
        if not sec:
            sec=self.sec_edit.text()
        #if self.dd.sec_exists(sec):
        if sec_exists(sec,self.layer_box.currentLayer(),self.sec_field_box.currentField()):
            if sec!=self.sec:
                self.sec=sec
                self.sec_changed.emit(self.sec)
                self.ch_box.setValue(0)
                self.ch_box.setMaximum(self.sec_to_feature(sec)[self.len_field_box.currentField()]+50)
                self.set_ch(0)            
            layer_functions.select_sections([self.sec],self.layer_box.currentLayer(),self.sec_field_box.currentField(),zoom=True)
            

    def set_ch(self,ch):
        self.ch_box.setValue(ch)
        self.redraw(self.sec,ch)
        
        
    #move marker to sec and c
    def redraw(self,sec,c):
        if not self.sec is None:
            self.remove_marker()
            self.marker=QgsVertexMarker(iface.mapCanvas())
            p=ch_to_pt(sec,ch=c,layer=self.layer_box.currentLayer(),sec_field=self.sec_field_box.currentField(),len_field=self.len_field_box.currentField())
            self.marker.setCenter(p)#marker at point
            self.marker.updatePosition()
            self.marker.setIconSize(15)
            self.marker.setIconType(QgsVertexMarker.ICON_X)
            self.marker.setColor(QColor(255,0,0))
            self.marker.setPenWidth(4)        
            self.marker.updateCanvas()
            self.marker.show()


    def current_sec(self):
        return self.sec


    def current_ch(self):
        return self.ch_box.value()
    

    #removes marker
    def remove_marker(self):
         if self.marker:
                iface.mapCanvas().scene().removeItem(self.marker)


    def field_changed(self,field):
        completer = QCompleter()
        self.sec_edit.setCompleter(completer)
        completer.setModel(to_string_list_model(self.layer_box.currentLayer(),field))


    def from_layer(self):
        sf=self.layer_box.currentLayer().selectedFeatures()
        if len(sf)==0:
            iface.messageBar().pushMessage('no features selected on layer '+self.layer_box.currentLayer().name(),duration=4)
            return
        if len(sf)>1:
            iface.messageBar().pushMessage('>1 feature selected on layer '+self.layer_box.currentLayer().name(),duration=4)
            return
        self.sec_edit.setText(sf[0][self.sec_field_box.currentField()])
        #self.set_sec()


    def sec_to_feature(self,sec):
        return sec_to_feature(sec,self.layer_box.currentLayer(),self.sec_field_box.currentField())
        
        
            
#makes unique values into QStringListModel. field needs to be a string field.
def to_string_list_model(layer,field):
    model=QStringListModel()
    col_index=layer.dataProvider().fieldNameIndex(field)
    model.setStringList(layer.uniqueValues(col_index))      
    return model


#sets layer of fieldbox fb to layer then tries to set fb to field with name name
def set_to(fb,layer,name=None):
    fb.setLayer(layer)
    fb.setField(name)


#set layer of qgsMapLayerComboBox to 1st layer named name if exists
def set_layer_box_to(layer_box,name):
    i=layer_box.findText(name)
    if i!=-1:
        layer_box.setLayer(layer_box.layer(i))



def ch_to_pt(sec,ch,layer,sec_field,len_field):

    f=sec_to_feature(sec,layer,sec_field)
    g=f.geometry()
    sec_len=f[len_field]

    if ch<=0:
        return g.asPolyline()[0]#return start of line

    if ch>=sec_len:
        return g.asPolyline()[-1]#return end of line


    return g.interpolate(g.length()*ch/sec_len).asPoint()#in terms of distance along line.
    #point in crs of layer.


def pt_to_ch(pt,sec,layer,sec_field,len_field):

    pt=QgsGeometry().fromWkt(pt.asWkt())
    f=sec_to_feature(sec,layer,sec_field)
    g=f.geometry()
    sec_len=f[len_field]

    return sec_len*g.lineLocatePoint(pt)/g.length() #takes QgsGeometry not qgspointxy


def sec_exists(sec,layer,sec_field):
    try:
        r=sec_to_feature(sec,layer,sec_field)
        return True
    except:
        return False

    
def sec_to_feature(sec,layer,sec_field):
    e='%s=%s '%(double_quote(sec_field),single_quote(sec))
    request = QgsFeatureRequest().setFilterExpression(e)
    feats=[f for f in layer.getFeatures(request)]

    if len(feats)==0:
        raise KeyError('section %s not found'%(sec))

    if len(feats)>1:
        raise KeyError('multiple features with section label %s'%(sec))
        
    return feats[0]



def single_quote(s):
    return "'%s'"%(s)


def double_quote(s):
    return '"%s"'%(s) 







