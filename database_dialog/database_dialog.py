import os
from  qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from  qgis.PyQt.QtCore import QSettings,Qt
#from qgis.PyQt.QtSql import QSqlDatabase,QSqlTableModel,QSqlQuery

from qgis.PyQt.QtSql import QSqlDatabase,QSqlQuery
import psycopg2

from qgis.PyQt.QtCore import pyqtSignal

#for cancellable task(qgis specific)
from PyQt5.QtWidgets import QProgressDialog,QLabel #QProgressBar,QPushButton,
from qgis.utils import iface
from qgis.PyQt.QtCore import pyqtSignal,QObject,QThread

from qgis.core import QgsApplication

from . import sql_tasks


uiPath=os.path.join(os.path.dirname(__file__), 'database_dialog.ui')
FORM_CLASS, _ = uic.loadUiType(uiPath)


def db_to_con(db):
    return psycopg2.connect(host=db.hostName(),dbname=db.databaseName(),user=db.userName(),password=db.password())


class database_dialog(QDialog,FORM_CLASS):
    
    reconnected = pyqtSignal()
    data_changed = pyqtSignal()
    
    def __init__(self,parent=None):
        super(QDialog,self).__init__(parent)
        self.setupUi(self)
        #self.setModal(True)#block other stuff
        self.connections_box.currentIndexChanged.connect(self.get_connection_info)
        self.connect_button.clicked.connect(self.connect)
        self.ok_button.clicked.connect(self.accept)
        self.set_connected(False)
        self.db = QSqlDatabase.addDatabase('QPSQL')
        self.con=None
        self.cur=None
        
        self.connected=False
        self.task=None#QgsTask task. only want to run 1 task at a time.

        self.progress=QProgressDialog(parent=self.parent())#set parent to dockwidget
        self.progress.setWindowModality(Qt.WindowModal)#make modal to prevent multiple tasks at once
        self.progress.canceled.connect(self.task_canceled)
        self.task_canceled()
        self.refresh_connections()
        self.refresh_button.clicked.connect(self.refresh_connections)

            
    def set_values(self,host=None,database=None,user=None,password=None):

        if host:
            self.host.setText(host)
            
        if database:
            self.database.setText(database)

        if user:
            self.user.setText(user)

        if password:
            self.password.setText(password)



    
    def refresh_connections(self):
        self.connections_box.clear()        
        self.connections_box.addItems(get_postgres_connections())
       

        ##returns psycopg2 connection
    def psycopg2_con(self):
        return db_to_con(self.db)

    
    def get_connection_info(self,i):
        settings = QSettings()
        settings.beginGroup( '/PostgreSQL/connections/' )
        settings.beginGroup(self.connections_box.itemText(i))
        self.host.setText(str(settings.value('host')))
        self.database.setText(str(settings.value('database')))
        self.user.setText(str(settings.value('username')))
        self.password.setText(str(settings.value('password')))


    def set_connected(self,connected):
        if connected:
            self.status.setText('Connected')
            self.connected=True
        else:
            self.status.setText('Not Connected')
            self.connected=False
            
    def connect(self):
        #need this for qsqlTableModel etc.
        self.db.setHostName(self.host.text())
        self.db.setDatabaseName(self.database.text())
        self.db.setUserName(self.user.text())
        self.db.setPassword(self.password.text())

        if self.con:
            self.con.close()
        #but psycopg2 better than QSqlQuery


        try:
            self.con=psycopg2.connect(host=self.host.text(),dbname=self.database.text(),user=self.user.text(),password=self.password.text())
            self.db.open()

            self.set_connected(True)
            self.cur=self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            self.reconnected.emit()
      
        except Exception as e:
            self.cur=None
            self.set_connected(False)
            iface.messageBar().pushMessage('fitting tool: failed to connect: '+str(e))
          
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
            #self.con.rollback()
            if script:
                raise ValueError('%s \nrunning: %s \n with args: %s'%(str(e),script,str(args)))

            else:
                raise ValueError('%s\ngiven query: %s\n args:%s,\nattempted query: %s '%(str(e),str(q),str(args),str(self.cur.query)))
        

    def cancel(self):
        self.con.cancel()

        
    def sql_script(self,script,args={}):
        s=script
        if os.path.dirname(script)=='':
            s=os.path.join(os.path.dirname(__file__),script)
            
        with open(s,'r') as f:
            self.sql(f.read(),args,script=s)


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

def get_postgres_connections():
    settings = QSettings()
    settings.beginGroup( '/PostgreSQL/connections/' )
    connections = settings.childGroups() 
    settings.endGroup()
    return connections
