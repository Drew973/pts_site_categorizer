from qgis.PyQt.QtSql import QSqlDatabase,QSqlQuery
import psycopg2


def db_to_con(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())



#interface for postgres database

class database_interface:
#qdatabase
    def __init__(self,db):
        self.db =db #psycopg2 better than QSqlDatabase but need this for qsqltablemodels etc.
        if not self.db.isOpen():
            self.db.open()
        self.con=db_to_con(db)
        self.cur=self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)


    def disconnect(self):
        self.db.close()
        if self.con:
            self.con.close()


#script=filename to give in error message when failed to run script
    def sql(self,q,args={},ret=False,script=None):
        try:
            with self.con:
                if args:
                    self.cur.execute(q,args)
                else:
                    self.cur.execute(q)#with makes con commit here
                if ret:
                    return self.cur.fetchall()


        except psycopg2.ProgrammingError as e:
            #exq=str(cur.query)#cur.query() gives type error because cur.query is a (bytes)string.
            self.con.rollback()
            if script:
                raise ValueError('%s \nrunning: %s \n with args: %s'%(str(e),script,str(args)))

            else:
                raise ValueError('%s\ngiven query: %s\n args:%s,\nattempted query: %s '%(str(e),str(q),str(args),str(self.cur.query)))

    def sql_script(self,script,args={}):
        s=script
        if os.path.dirname(script)=='':
            s=os.path.join(os.path.dirname(__file__),script)
            
        with open(s,'r') as f:
            try:
                self.sql(f.read(),args,script=s)
            except psycopg2.ProgrammingError as e:
                raise ValueError('%s \nrunning: %s \n with args: %s'%(str(e),script,str(args)))

                

    def query_to_csv(self,query,to,args=None,force_quote=None):
        with open(to,'w') as f:
            #)##SQL_for_file_output = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(s)
            if force_quote:
                self.cur.copy_expert("COPY (%s) TO STDOUT WITH (FORMAT CSV,HEADER,FORCE_QUOTE%s)"%(query,force_quote),f)
            else:
                self.cur.copy_expert("COPY (%s) TO STDOUT WITH (FORMAT CSV,HEADER)"%(query),f)
                
    
    def disconnect(self):
        self.db.close()
        if self.con:
            self.con.close()


    #reads text file, splits into sql files or sql commands seperated by ; then runs them in order.
    def run_setup_file(self,file,folder):
        with open(os.path.join(folder,file)) as f:
            for c in f.read().split(';'):
                com=c.strip()
                f=os.path.join(folder,com)
                if com:
                    if os.path.exists(f):
                        print(f)
                        self.sql_script(f)
                    else:
                        print(com)
                        self.sql(com)

    def __del__(self):
        self.db.close()
        if self.con:
            self.con.close()


    
    def cancel(self):
        self.con.cancel()




# use psycopg2 to run query with args. show progress dialog and cancel button.
#want modal progressbar

    def cancelable_query(self,q,args,text='running task',sucess_message=''):        
        if self.task:
            iface.messageBar().pushMessage('fitting tool: already running task')
            
        else:
            self.progress.setLabel(QLabel(text=text))
            self.task = sql_tasks.cancelable_sql(self.con,q,args,sucess_message=sucess_message)
           # self.task.setDescription(text)
            self.task.taskCompleted.connect(self.task_canceled)
            self.task.taskTerminated.connect(self.task_canceled)

            self.progress.canceled.connect(self.task.cancel)
        
            self.progress.show()
            QgsApplication.taskManager().addTask(self.task)#priority 0, happens after other tasks. displaying message/widget is task?
            #task.run()#happens imediatly. no progressbar/dialog displayed





# use psycopg2 to run query with args. show progress dialog and cancel button.
#want modal progressbar

#qgis specific. 
    def cancelable_queries(self,queries,args,text='running task',sucess_message=''):        
        if self.task:
            iface.messageBar().pushMessage('fitting tool: already running task')
            
        else:
            self.progress.setLabel(QLabel(text=text))
            self.progress.setMaximum(100)

            self.task = sql_tasks.cancelable_queries(self.con,queries,args,sucess_message=sucess_message)
            self.task.progressChanged.connect(self.progress.setValue)
           # self.task.setDescription(text)
            self.task.taskCompleted.connect(self.task_canceled)
            self.task.taskTerminated.connect(self.task_canceled)

            self.progress.canceled.connect(self.task.cancel)
              
            self.progress.show()
            QgsApplication.taskManager().addTask(self.task)#priority 0, happens after other tasks. displaying message/widget is task?
            #task.run()#happens imediatly. no progressbar/dialog displayed


    def cancelable_queries(self,queries,args,text='running task',sucess_message=''):        
        if self.task:
            iface.messageBar().pushMessage('fitting tool: already running task')
            
        else:
            self.progress.setLabel(QLabel(text=text))
            self.progress.setMaximum(100)

            self.task = sql_tasks.cancelable_queries(self.con,queries,args,sucess_message=sucess_message)
            self.task.progressChanged.connect(self.progress.setValue)
           # self.task.setDescription(text)
            self.task.taskCompleted.connect(self.task_canceled)
            self.task.taskTerminated.connect(self.task_canceled)

            self.progress.canceled.connect(self.task.cancel)
              
            self.progress.show()
            QgsApplication.taskManager().addTask(self.task)#priority 0, happens after other tasks. displaying message/widget is task?
            #task.run()#happens imediatly. no progressbar/dialog displayed


    def cancelable_batch_queries(self,queries,args,text='running task',sucess_message=''):
        #args is list of dicts/lists here
        if self.task:
            iface.messageBar().pushMessage('fitting tool: already running task')
            
        else:
            self.progress.setLabel(QLabel(text=text))
            self.progress.setMaximum(100)

            self.task = sql_tasks.cancelable_batches(self.con,queries,args,sucess_message=sucess_message)
            self.task.progressChanged.connect(self.progress.setValue)
           # self.task.setDescription(text)
            self.task.taskCompleted.connect(self.task_canceled)
            self.task.taskTerminated.connect(self.task_canceled)

            self.progress.canceled.connect(self.task.cancel)
              
            self.progress.show()
            QgsApplication.taskManager().addTask(self.task)#priority 0, happens after other tasks. displaying message/widget is task?
            #task.run()#happens imediatly. no progressbar/dialog displayed

  
    def task_canceled(self):
        self.task=None
        self.progress.reset()
        self.progress.hide()
        self.progress.setMinimum(0)#qprogressbar will show busy indicator when min and max set to 0
        self.progress.setMaximum(0)



