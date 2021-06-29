import os

from PyQt5 import uic
from PyQt5.QtCore import Qt,QSettings
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QAction,QDialog#,QShortcut #

#dialog to return QSqlDatabase. can get psycopyg2 connection from this.


uiPath=os.path.join(os.path.dirname(__file__), 'database_dialog.ui')
FORM_CLASS, _ = uic.loadUiType(uiPath)


class database_dialog(QDialog,FORM_CLASS):

    def __init__(self,parent=None):
        super(QDialog,self).__init__(parent)
        self.setupUi(self)
        self.connections_box.currentIndexChanged.connect(self.get_connection_info)
        self.set_connected(False)
       # self.task=None#QgsTask task. only want to run 1 task at a time.
        #self.progress=QProgressDialog(parent=self.parent())#set parent to dockwidget

        #self.progress.setWindowModality(Qt.WindowModal)#make modal to prevent multiple tasks at once
        #self.progress.canceled.connect(self.task_canceled)
        #self.task_canceled()

        self.refresh_connections()
        self.refresh_button.clicked.connect(self.refresh_connections)

        self.connect_act=QAction(self);
        self.connect_act.setShortcut(Qt.Key_Return)
        self.connect_act.triggered.connect(self.accept)

        #self.ok_button.clicked.connect(self.accept)
        self.test_button.clicked.connect(self.test_connection)
        self.close_button.clicked.connect(self.close)

#sets text edits
    def set_values(self,host=None,database=None,user=None,password=None):

        if host:
            self.host.setText(host)

        if database:
            self.database.setText(database)

        if user:
            self.user.setText(user)

        if password:
            self.password.setText(password)

#refreshes list of connections.
    def refresh_connections(self):
        self.connections_box.clear()
        self.connections_box.addItems(get_postgres_connections())


    def exec_(self):
        super(database_dialog, self).exec_()
        return self.get_db()


    def get_connection_info(self,i):
        settings = QSettings()
        settings.beginGroup( '/PostgreSQL/connections/' )
        settings.beginGroup(self.connections_box.itemText(i))
        self.host.setText(str(settings.value('host')))
        self.database.setText(str(settings.value('database')))
        self.user.setText(str(settings.value('username')))
        self.password.setText(str(settings.value('password')))


    def test_connection(self):
        db=self.get_db()
        if db.open():
            self.set_connected(True)
        else:
            self.set_connected(False)

            
    def set_connected(self,connected):
        if connected:
            self.status.setText('Connected')
        else:
            self.status.setText('Not Connected')


#create QSqlDatabase from text edits 
    def get_db(self):
        db=QSqlDatabase.addDatabase('QPSQL')
        db.setHostName(self.host.text())
        db.setDatabaseName(self.database.text())
        db.setUserName(self.user.text())
        db.setPassword(self.password.text())
        return db
        
#finds postgres connections in qgis settings.
def get_postgres_connections():
    settings = QSettings()
    settings.beginGroup( '/PostgreSQL/connections/' )
    connections = settings.childGroups()
    settings.endGroup()
    return connections


if __name__=='__main__':
    d=database_dialog()
    d.exec_()
