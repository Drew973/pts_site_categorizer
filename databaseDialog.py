import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt,QSettings,pyqtSignal
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QAction,QDialog,QApplication#,QShortcut #



import psycopg2

#dialog to return QSqlDatabase. can get psycopyg2 connection from this.


if __name__=='__console__':
    uiPath = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\hsrrprocessor\database_dialog\database_dialog.ui' 
else:
    uiPath = os.path.join(os.path.dirname(__file__), 'databaseDialog.ui')


FORM_CLASS, _ = uic.loadUiType(uiPath)


'''
dialog to emit QSqlDatabase signal when accepted.
when accepted 
exec() returns QSqlDatabase
'''


class databaseDialog(QDialog,FORM_CLASS):
    connected = pyqtSignal(QSqlDatabase)

    def __init__(self,parent=None,name='databaseName'):
        super(QDialog,self).__init__(parent)
        self.setupUi(self)
        self.connections_box.currentIndexChanged.connect(self.get_connection_info)
        self.setConnected(False)
       # self.task=None#QgsTask task. only want to run 1 task at a time.
        #self.progress=QProgressDialog(parent=self.parent())#set parent to dockwidget

        #self.progress.setWindowModality(Qt.WindowModal)#make modal to prevent multiple tasks at once
        #self.progress.canceled.connect(self.task_canceled)
        #self.task_canceled()

        self.refreshConnections()
        self.refresh_button.clicked.connect(self.refreshConnections)

        self.connectAct=QAction(self);
        self.connectAct.setShortcut(Qt.Key_Return)
        self.connectAct.triggered.connect(self.accept)

        #self.ok_button.clicked.connect(self.accept)
        self.test_button.clicked.connect(self.connect)
        
        self.OkButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.name = name



#sets text edits
    def setValues(self,host=None,database=None,user=None,password=None):

        if host:
            self.host.setText(host)

        if database:
            self.database.setText(database)

        if user:
            self.user.setText(user)

        if password:
            self.password.setText(password)

#refreshes list of connections.
    def refreshConnections(self):
        self.connections_box.clear()
        self.connections_box.addItems(getPostgresConnections())

    def exec_(self):
        super(databaseDialog, self).exec_()
        return self.getDb()

    def get_connection_info(self,i):
        settings = QSettings()
        settings.beginGroup( '/PostgreSQL/connections/' )
        settings.beginGroup(self.connections_box.itemText(i))
        self.host.setText(str(settings.value('host')))
        self.database.setText(str(settings.value('database')))
        self.user.setText(str(settings.value('username')))
        self.password.setText(str(settings.value('password')))

    def accept(self):
        self.connected.emit(self.getDb())
        super(databaseDialog,self).accept()


    def connect(self):
        db = self.getDb()
        if db.open():
            self.setConnected(True,db)
        else:
            self.setConnected(False,db)
            
            
    def setConnected(self,connected,db=None):
        if connected:
            self.status.setText('Connected')
            if db:
                self.setWindowTitle('Connected to %s'%(db.databaseName()))
        else:
            self.status.setText('Not Connected')
            self.setWindowTitle('Connect to database')


    #create unopened QSqlDatabase from text edits 
    def getDb(self):
        db = QSqlDatabase.addDatabase('QPSQL',self.name)
        db.setHostName(self.host.text())
        db.setDatabaseName(self.database.text())
        db.setUserName(self.user.text())
        db.setPassword(self.password.text())
        return db
   

    def getCon(self):
        return psycopg2.connect(host=self.host.text(),dbname=self.database.text(),user=self.user.text(),password=self.password.text())
   
     
#finds postgres connections in qgis settings.
def getPostgresConnections():
    settings = QSettings()
    settings.beginGroup( '/PostgreSQL/connections/' )
    connections = settings.childGroups()
    settings.endGroup()
    return connections


if __name__=='__main__':
    app = QApplication(sys.argv)
   
    d=databaseDialog()
    d.connected.connect(lambda:print('connected'))
    d.setValues('localhost','hsrr_test','postgres','')

    d.exec_()

    sys.exit(app.exec())
    
    
if __name__=='__console__':
    d = databaseDialog()
    d.connected.connect(lambda:print('connected'))
    d.setValues('localhost','hsrr_test','postgres','')

    d.exec_()

