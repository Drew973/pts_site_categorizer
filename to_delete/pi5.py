
import psycopg2
from psycopg2.extras import DictCursor
from os import path as osp

class pi:
     
    def __init__(self,host,db_name,user,password='',port='5432'):
        self.host=host
        self.db_name=db_name
        self.user=user
        self.password=password
        self.port=port
        self.connected=False

    def connect(self):
        try:
            self.con=psycopg2.connect(host=self.host,dbname=self.db_name,user=self.user,password=self.password,port=self.port)
            self.curser=self.con.cursor(cursor_factory=DictCursor)
            self.connected=True
            return True
            
        except:
            self.connected=False
            return False

    def disconnect(self):
        self.con.close()
        self.connected=False


    def ex(self,q,args):
         if args!=[]:
            try:
                self.curser.execute(q,tuple(args))
            except: 
                self.connect()
         else:
            try:
                self.curser.execute(q)
            except:
                self.connect()
            
        
    def get_query(self,q,args=[]):
        if self.connected:
            self.ex(q,args)
            try:
                r=self.curser.fetchall()
                return r
            except:
                return None
        else:
            raise ValueError('postgres interface not connected')
  
    def sql(self,q,args=[]):
        if self.connected:
            self.ex(q,args)
            self.con.commit()
            return True
        else:
            raise ValueError('postgres interface not connected')

        

    def run_script(self,path,relpath=True):
        if relpath:
            path=full_path(path)
        with open (path,'r') as f:
            q=f.read()
            #print q
            self.sql(q)
            
    def drop_table(self,table):
        self.sql('DROP TABLE IF EXISTS '+table)
    
        
def full_path(p):
    folder=osp.dirname(osp.realpath(__file__))
    return osp.join(folder,p)

