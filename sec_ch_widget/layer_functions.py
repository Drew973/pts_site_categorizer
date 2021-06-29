from qgis.utils import iface
from qgis.core import QgsFeatureRequest

#layer=qgislayer
#section=string,
#field=string


def select_section(section,layer,field):
    if field: 
        try:
            e="%s IN (%s)" %(double_quote(field),single_quote(section))#expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
            #Field names in double quotes, string in single quotes
            layer.selectByExpression(e)
            iface.mapCanvas().setExtent(layer.boundingBoxOfSelected())
            iface.mapCanvas().refresh()
        except Exception as e:
            iface.messageBar().pushMessage('fitting tool:'+repr(e))
    else:
        iface.messageBar().pushMessage('fitting tool: Field not set.')


def single_quote(s):
    return "'%s'"%(s)


def double_quote(s):
    return '"%s"'%(s) 


#sects is list of sections.
def select_sections(sects,layer,field,zoom=False):
    if field: 
        e="%s IN (%s)" %(double_quote(field),','.join([single_quote(s) for s in sects]))#expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
        #Field names in double quotes, string in single quotes
        layer.selectByExpression(e)
        if zoom:
            zoom_to_selected(layer)   
    else:
        iface.messageBar().pushMessage('fitting tool: Field not set.')       
        
#zoom to selected features of layer. Works with any crs
def zoom_to_selected(layer):
    a=iface.activeLayer()
    iface.setActiveLayer(layer)
    iface.actionZoomToSelected().trigger()
    iface.setActiveLayer(a)
    #iface.mapCanvas().setExtent(layer.boundingBoxOfSelected())
    #iface.mapCanvas().refresh()


#returns feature ids of features in run with s<=f_field<=e
def ch_to_id(layer,run_field,run,f_field,s,e):
    e='%s=%s and %d<=%s and %s<=%d'%(double_quote(run_field),single_quote(run),s,double_quote(f_field),double_quote(f_field),e)
    request = QgsFeatureRequest().setFilterExpression(e)
    return [f.id() for f in layer.getFeatures(request)]
        

#"run"='bench mark 01' and 'TEST01'<="f_line" and "f_line"<='12'

#filter layer to only show run
#run=string. run_field=fieldname with run
def filter_by_run(layer,run_field,run):
    layer.setSubsetString("%s = '%s'"%(run_field,run))
    

