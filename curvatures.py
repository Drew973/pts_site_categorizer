from scipy import interpolate
import numpy as np

from qgis.core import QgsLineString,QgsGeometry,QgsPointXY
import math
import sys
import matplotlib.pyplot as plt

import logging


logger = logging.getLogger(__name__)


#returns dict of {x,y,ch} of vertices.
#ch is cartesian chainage
def vertices(geom):
    ch = 0
    last = None
    
    for v in geom.vertices():#iterator of QgsPoint
        if last:
            ch += v.distance(last)
        yield{'x':v.x(),'y':v.y(),'ch':ch}
        last = v
    
#returns new linestring with points seperated by spacing

#curvature from parametric function.
#x1=x',x2=x'',y1=y',y2=y''
#https://www.math24.net/curvature-radius

def curvature(x1,x2,y1,y2):
    return abs((x1*y2-y2*x2))*math.pow(x1*x1+y1*y1,-3/2)



class sectionInterpolator:
    #s is smoothing factor. s=0 means no smoothing. None for default smoothing
    def __init__(self,geom,s=None):
        self.xSpline = None
        self.ySpline = None
        
        self.x = [v['x'] for v in vertices(geom)]
        self.y = [v['y'] for v in vertices(geom)]
        self.ch = [v['ch'] for v in vertices(geom)]
        self.length = geom.length()
    
        if len(self.ch)>3:#need > 3 points to fit cublic spline

            self.xSpline = interpolate.UnivariateSpline(self.ch, self.x,s=s)
            self.ySpline = interpolate.UnivariateSpline(self.ch, self.y,s=s)
            
            
    def interpolatedGeom(self,spacing):
        ch = np.append(np.arange(0,self.length,spacing),self.length)
        return QgsGeometry(QgsLineString(self.xSpline(ch),self.ySpline(ch)))
        
        
#https://www.math24.net/curvature-radius
#curvature=1/radius of curvature
    def curvature(self,ch):
       
        x1 = self.xSpline.derivative(1)(ch)#x'
        x2 =  self.xSpline.derivative(2)(ch)#x''
        y1 = self.ySpline.derivative(1)(ch)#y'
        y2 =  self.ySpline.derivative(2)(ch)#y''
        return abs((x1*y2-y2*x2))*math.pow(x1*x1+y1*y1,-3/2)
    
    
    #https://www.math24.net/curvature-radius
    def curvatures(self,chainages):
        x1 = self.xSpline(chainages,1)#x'
        x2 =  self.xSpline(chainages,2)
        y1 = self.ySpline(chainages,1)#y'
        y2 =  self.ySpline(chainages,2)#y''
                
        return np.multiply(np.absolute(np.subtract(np.multiply(x1,y2),np.multiply(y2,x2))),
        np.power(np.add(np.multiply(x1,x1),np.multiply(y1,y1)),-3/2))
        
    def radi(self,chainages):
        return np.divide(1,self.curvatures(chainages))

    def interpolateX(self,chainages):
        return interpolate.splev(chainages,self.xSpline,ext=2)

    def interpolateY(self,chainages):
        return interpolate.splev(chainages,self.ySpline,ext=2)
        
    def point(self,ch):
        self.checkChainage(ch)
        return QgsGeometry.fromPointXY(QgsPointXY(self.interpolate.splev(ch),self.ySpline(ch)))


    def plot(self):
        
        fig1, (ax1,ax2) = plt.subplots(nrows=2, ncols=1)
        ax1.plot(self.x,self.y,'x',label='points')
        chainages = np.arange(0,max(self.ch))
        
        x = self.xSpline(chainages)#scipy.interpolate.interpolate.interp1d
        y = self.ySpline(chainages)
        #plt.plot(self.interpolateX(chainages),self.interpolateX(chainages),label='fit')
        ax1.plot(x,y,label='fit')
        
        ax1.set_xlabel('x')
        ax2.set_ylabel('y')
        
        ax2.set_ylim(top=1000)
        
        fig1.legend()
        ax2.set_xlabel('chainage')
        ax2.set_ylabel('roc(m)')
        ax2.grid(which='both')
        ax2.set_yticks(np.arange(0,1000,50),minor=True)
        ax2.plot(chainages,self.radi(chainages),label='radi')
    



class piece:
    def __init__(self,start=0):
        self.start = start
        self.end = start 
        self.vals = []
        
    def append(self,distance,roc):
        self.vals.append(roc)
        self.end = distance
        
        
    def __repr__(self):
        return 'piece: start:%d,end:%d,min:%f'%(self.start,self.end,min(self.vals))
        
    def length(self):
        return self.end-self.start
        
    def min(self):
        return min(self.vals)
        
    def __getitem__(self,key):
        if key=='start':
            return self.start
            
        if key=='end':
            return self.end
        
#return list of pieces where roc<threshold
def getPieces(geom,threshold):
    
    logger.info('getPieces(%s,%s)',geom,threshold)
    
    i = sectionInterpolator(geom)
    
    if i.xSpline is None:#not enough points
        return []
    
    distances = np.arange(0,max(i.ch))#every 1m. could change. accuracy vs performance?
    rocs = i.radi(distances)
    #print('distances:%s,rocs:%s'%(distances,rocs))
    
    pieces = []
    
    for i,v in enumerate(distances):
            
        if rocs[i]<=threshold:
            if pieces and v==pieces[-1].end+1:
                pieces[-1].append(distance=v,roc=rocs[i])
                
            else:
                pieces.append(piece(start=v))
                
    return pieces


 
if __name__ =='__console__':
    #'5010C614 1/00090'. 60mph
    geom = QgsGeometry.fromWkt('LINESTRING(373769.2399 421382.61685,373651.41905 421535.8511,373634.83115 421571.2657,373605.99115 421661.0918,373535.92255 421797.3045,373514.04895 421846.0363,373503.80795 421876.84175,373498.041 421919.7229,373499.89285 421950.15005,373511.00605 421999.8913,373514.97505 422036.1392,373532.173 422075.42975,373584.71605 422145.8072,373579.03135 422169.02,373537.7289 422231.4018,373507.8151 422268.81775,373462.0218 422301.5043,373394.3241 422336.1779,373298.4129 422390.6817,373232.39905 422428.5169,373211.2321 422442.54,373165.856 422480.1113,373143.89595 422529.3241,373115.1879 422615.70975,373057.90585 422901.4608,373040.17905 422972.63385,373009.08995 423097.25315,372987.79105 423188.27005,372961.862 423268.04195)')
    
    i =sectionInterpolator(geom)
    plt.close()
    i.plot()
    plt.show(block=False)
    
    autoCurvatures(geom,60)

    
#feature.setGeometry
    
    #print(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    
