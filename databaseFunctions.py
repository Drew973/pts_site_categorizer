import os 
import psycopg2

#from PyQt5.QtSql import QSqlDatabase


#reads text file, splits into sql files or sql commands seperated by ; then runs them in order.
 #try/except in file with gui
 
'''

go through ; seperated pieces of file.

prints if printCom True

if existing file then runSetupFile() on it
else run as sql command.

scripts need to be given as relative paths to file.
'''
 


 
# QSqlDatabase to psycopg2 connection
def dbToCon(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password()) 
 
 
 
 
 #functions can have ; part way through
def runSetupFile(cur,file,printCom=False,recursive=True):
    
    folder = os.path.dirname(file) 
    
    with open(file) as f:
        
        for c in f.read().split(';'):
            com = c.strip()
            f = os.path.join(folder,com)
            if com:
                if printCom:
                    print(com)
                
                if os.path.exists(f):
                    if recursive:
                       runSetupFile(cur,f,printCom) 
                    else:
                        runScript(cur,f)
                    
                else:
                    if com:
                        cur.execute(com) 
 
    
 
def runScript(cur,script,args={}):
        s = script
        
        if os.path.dirname(script)=='':
            s = os.path.join(os.path.dirname(__file__),script)
    
        with open(s,'r') as f:
            if args:
                cur.execute(f.read(),args)
            else:
                cur.execute(f.read())
                
          