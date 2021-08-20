
    
def parseSource(layer):
    r = {}
    s = layer.source()
    print(s)
    L = s.split(' ')
    
    for i in L:
        row = i.split('=')
        if len(row)>=2:
            r.update({row[0].strip('" "'):row[1]})
        else:
            r.update({row[0]:''})
            
    return r
            
        #host
        #dbname
        #table

    print(L)
    #return {i.split('=')[0]:i.split('=')[1] for i in L}

L = ["dbname='pts2157-02_blackburn'", 'host=192.168.5.157', 'port=5432', "user='stuart'", "password='pts'", 'sslmode=disable', "key='sec'", 'srid=27700', 'type=LineString', 'table="categorizing"."network"', '(geom)', 'sql=']




if __name__=='__console__':
    layer = iface.activeLayer()
    

    
    print(parseSource(layer))
