from PyQt5.QtWidgets import QUndoCommand
import psycopg2


class insertCommand(QUndoCommand):

    '''
    command to insert multiple rows.
    pkCol= name of primary key column
    cols = list of column names. 
    data = list of lists. same order as cols.
    
    '''
    def __init__(self,con,table,pkCol,cols,data,description='insert'):
        super().__init__(description)
        self.con = con
        self.table = table
        self.pkCol = pkCol
        self.cols = cols
        self.data = data
        

#use copy_from and csv like string as data?
    def redo(self):
        cur = self.con.cursor()
        p = '(%s)'%(','.join( ['%s' for c in self.cols]))
        vals = ','.join([cur.mogrify(p,d).decode() for d in self.data])
        cur.execute("insert into %s (%s) VALUES %s returning pk;"%(self.table,','.join(self.cols),vals))
        self.pks = [str(v[0]) for v in cur.fetchall()]#primary keys of inserted rows


    def undo(self):    
        q = 'delete from %s where pk in  (%s)'%(self.table,','.join(self.pks))
        cur = self.con.cursor()
        cur.execute(q)
        
        
        
        
class deleteCommand(QUndoCommand):

    '''
    command to insert multiple rows.
    pkCol= name of primary key column
    pks = list of primary keys to delete 
    '''
    def __init__(self,con,table,pkCol,pks,description='delete'):
        super().__init__(description)
        self.con = con
        self.table = table
        self.pkCol = pkCol
        self.pks = [str(pk) for pk in pks]
        

#use copy_from and csv like string as data?
    def redo(self):
        
        cur = self.con.cursor()
        q = 'delete from %s where pk in  (%s) returning *'%(self.table,','.join(self.pks))
        cur.execute(q)          
        self.data = cur.fetchall()
        self.cols = [desc[0] for desc in cur.description]#column names
        

    def undo(self):    
        cur = self.con.cursor()
        p = '(%s)'%(','.join( ['%s' for c in self.cols]))
        vals = ','.join([cur.mogrify(p,d).decode() for d in self.data])
        cur.execute("insert into %s VALUES %s;"%(self.table,vals))
        
        
        
class updateCommand(QUndoCommand):

    '''
    cannot handle change to pk
    pkCol= name of primary key column
    cols = list of column names. 
    data = dict of col:value
    '''
    def __init__(self,con,table,pkCol,pk,values,description='update'):
        super().__init__(description)
        self.con = con
        self.table = table
        self.pkCol = pkCol
        self.values = values
        self.pk = pk
        

#use copy_from and csv like string as data?
    def redo(self):
        
        cur = self.con.cursor()
        q = 'select %s from %s where %s = %s'%(','.join([k for k in self.values]),self.table,self.pkCol,'%(_pk)s')
        cur.execute(q,{'_pk':self.pk})
        self.oldValues = cur.fetchone()[0]
        
        
        valStr = ','.join(['{v}=%({v})s'.format(v=v) for v in self.values])
        q = 'update %s set %s where %s=%s'%(self.table,valStr,self.pkCol,'%(_pk)s')
        print(q)
        vals = self.values.copy()
        vals.update({'_pk':self.pk})
        cur.execute(q,vals)
        
        

    def undo(self):    
        cur = self.con.cursor()
        #p = '(%s)'%(','.join( ['%s' for c in self.cols]))
        #vals = ','.join([cur.mogrify(p,d).decode() for d in self.data])
        #cur.execute("insert into %s VALUES %s;"%(self.table,vals))        
        
       
        
       
if __name__ == '__main__' or __name__=='__console__':
    con = psycopg2.connect(host='192.168.5.157',dbname='pts2157-02_blackburn',user='stuart',password='pts')
    d = [['5010A000677 /00020',False,0,10,'C'],['5010A000677 /00020',False,10,20,'C']]
    #c = insertCommand(con,'categorizing.other_events','pk',cols=['sec','reversed','s_ch','e_ch','category'],data=d)
    #c = deleteCommand(con,'categorizing.other_events','pk',pks=[5441,5373])
    c = updateCommand(con,'categorizing.other_events','pk','5441',{'reversed':True})
    
    c.redo()