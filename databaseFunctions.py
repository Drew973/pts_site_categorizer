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
 
 
 
def runSetupFile(cur,file,printCom=False):
    
    folder = os.path.dirname(file) 
    
    with open(file) as f:
        
        for c in f.read().split(';'):
            com = c.strip()
            f = os.path.join(folder,com)
            if com:
                if printCom:
                    print(com)
                
                if os.path.exists(f):
                    #runScript(con,f)
                    runSetupFile(cur,f,printCom)
                else:
                    if com:
                        cur.execute(com) 
 
    
 
def runScript(con,script,args={}):
        s = script
        
        if os.path.dirname(script)=='':
            s = os.path.join(os.path.dirname(__file__),script)
    
        with open(s,'r') as f:
            if args:
                con.cursor().execute(f.read(),args)
            else:
                con.cursor().execute(f.read())
                
          