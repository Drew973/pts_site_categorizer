
#sec_field=string
def ch_to_xy(sec,ch,layer,sec_field,len_field):

    feats=sec_to_features(sec,layer,sec_field)
    if len(feats)==0:
        raise KeyError('section %s not found'%(sec))

    if len(feats)>1:
        raise KeyError('multiple features with section label %s'%(sec))
        
    f=feats[0]
    g=f.geometry()
    
    p=g.interpolate(g.length()*ch/f[len_field]).asPoint()#in terms of diatance along line.
    return {'x':p.x(),'y':p.y()}
    

def sec_to_features(sec,layer,sec_field):
    e='%s=%s '%(double_quote(sec_field),single_quote(sec))
    request = QgsFeatureRequest().setFilterExpression(e)
    return [f for f in layer.getFeatures(request)]

def single_quote(s):
    return "'%s'"%(s)

def double_quote(s):
    return '"%s"'%(s)  

    
    
layer=iface.activeLayer()


print(ch_to_xy(r'C2702558/010',0,layer,'sec','meas_len'))

