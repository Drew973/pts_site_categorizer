from qgis.core import QgsProject,QgsGeometry,QgsCoordinateTransform,QgsCoordinateReferenceSystem
from qgis.utils import iface


#crs is crs for point
def chainageToPoint(chainage,geometry,sectionLength=None,pointCrs=None,geometryCrs=None):
    
    
    if geometryCrs is None:
        geometryCrs = QgsCoordinateReferenceSystem.fromEpsgId(27700)
                               
    if pointCrs is None:
        pointCrs = iface.mapCanvas().mapSettings().destinationCrs()##canvas.mapRenderer().destinationCrs() in qgis 2
        
    if sectionLength is None:
        sectionLength = geometry.length()
    
            
    t = QgsCoordinateTransform(geometryCrs,pointCrs,QgsProject.instance())#documentation says only need source and destination. lies.
            
    #transform takes qgspointxy

        
    if chainage<=0:
        return t.transform(geometry.asPolyline()[0])#return start of line
    
    if chainage>=sectionLength:
        return t.transform(geometry.asPolyline()[-1])#return end of line
    
    return t.transform(geometry.interpolate(geometry.length()*chainage/sectionLength).asPoint())





   #crs is crs of point
def pointToChainage(point,geometry,sectionLength=None,pointCrs=None,geometryCrs=None):
    
    
    if pointCrs is None:
        pointCrs = iface.mapCanvas().mapSettings().destinationCrs()
        
    if sectionLength is None:
        sectionLength = geometry.length()
        
    if geometryCrs is None:
        geometryCrs = QgsCoordinateReferenceSystem.fromEpsgId(27700)
    
    t = QgsCoordinateTransform(pointCrs,geometryCrs,QgsProject.instance())#documentation says only need source and destination. lies.
    point = t.transform(point)
    point = QgsGeometry().fromPointXY(point)
    
    return geometry.lineLocatePoint(point)*sectionLength/geometry.length()
