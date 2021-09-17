from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl
import os

from PyQt5.QtWidgets import QDataWidgetMapper,QDockWidget,QMenu,QMessageBox,QMenuBar,QUndoStack


from qgis.utils import iface
from qgis.PyQt.QtSql import QSqlTableModel
from PyQt5.QtGui import QDesktopServices

from . import networkModel,otherEventsModel,delegates,databaseFunctions,databaseDialog,commands,chainageDelegate

from .site_categorizer_dockwidget_base import Ui_site_categoriserDockWidgetBase


import logging

logging.basicConfig(filename=r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\site_categorizer\siteCategorizer.log',
                    level=logging.INFO,filemode='w')

logger = logging.getLogger(__name__)



#class site_categoriserDockWidget(QDockWidget,FORM_CLASS):
class site_categoriserDockWidget(QDockWidget,Ui_site_categoriserDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(site_categoriserDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
        
        self.secRow = 0
        
        self.undoStack = QUndoStack(self)
        
        self.connectDialog = databaseDialog.databaseDialog(parent=self,name='site_categorizer_database')
        self.connectDialog.accepted.connect(self.connect)
        
        self.initTopMenu()
        
        self.connectionDependent = [self.setupAct,self.secWidget,self.oneWayBox,self.noteEdit,self.checkedBox,self.otherEventsMenu]
        self.disconnected()
        
        self.secWidget.setUndoStack(self.undoStack)
        self.secWidget.currentIndexChanged.connect(self.setSecRow)#happens 1st?
                
        self.otherEventsView.undoStack = self.undoStack
        


    def setSecRow(self,row):
        logger.info('setSecRow(%s)',str(row))

        if row <= self.secWidget.model().rowCount():
            if row!=self.secWidget.currentIndex():
                self.secWidget.setCurrentIndex(row)
            
            sec = self.secWidget.itemText(row)
            
                
            self.otherEventsView.setSection(sec,self.secWidget.model().geom(row),self.secWidget.model().sectionLength(row))
            logger.info('self.mapper.setCurrentIndex')
            self.mapper.setCurrentIndex (row)#can cause crash
            logger.info('self.secWidget.selectOnLayer(warn=False)')
            self.secWidget.selectOnLayer(warn=False)


    def initTopMenu(self):
        topMenu = QMenuBar()
        self.frame.layout().setMenuBar(topMenu)
        
        #database
        databaseMenu = topMenu.addMenu("Database")
        connectAct = databaseMenu.addAction('Connect to Database...')
        connectAct.triggered.connect(self.connectDialog.show)
        self.setupAct = databaseMenu.addAction('Setup Database for site categories...')
        self.setupAct.triggered.connect(self.setupDatabase)
        
        editMenu = topMenu.addMenu("Edit")
        editMenu.addAction(self.undoStack.createUndoAction(self))
        editMenu.addAction(self.undoStack.createRedoAction(self))
        
        #help
        helpMenu = topMenu.addMenu("Help")
        openHelpAct = helpMenu.addAction('Open help (in your default web browser)')
        openHelpAct.triggered.connect(self.openHelp)
        
        self.otherEventsMenu = topMenu.addMenu("Events")
        
        topMenu.addMenu(self.otherEventsMenu)
        
        addAct = self.otherEventsMenu.addAction('Add empty row')
        addAct.triggered.connect(lambda:self.otherEventsView.model().insertDefault())
        
        
        autoCurvaturesAct = self.otherEventsMenu.addAction('recalculate curvatures')
        autoCurvaturesAct.triggered.connect(self.autoCurvatures)
        autoCurvaturesAct2 = self.otherEventsMenu.addAction('recalculate curvatures and plot')
        autoCurvaturesAct2.triggered.connect(lambda:self.autoCurvatures(plot=True))


    def autoCurvatures(self,plot=False):
        if self.secWidget.model().rowCount()>=0 and self.otherEventsView.model():
            self.otherEventsView.model().autoCurvatures(networkModel=self.secWidget.model(),row=self.secWidget.currentIndex(),plot=plot)


    def connect(self):
        logger.info('connect')
        
        self.undoStack.clear()
        
        db = self.connectDialog.getDb()

        if not db.isOpen():
            db.open()
        
        self.otherEventsView.connectToDatabase(db)
        #these work with closed/invalid database.            
        self.connectCategories(db)
        self.connectNetwork(db)
        
        if db.isOpen():#connected        
            self.setWindowTitle(db.databaseName()+' - site categorizer')       
            for w in self.connectionDependent:
                w.setEnabled(True)
                
            self.setSecRow(self.secWidget.currentIndex())        
 
            
        else:        
            iface.messageBar().pushMessage('site categorizer: could not connect to database',duration=4)
            self.disconnected()

            
     
    def disconnected(self):
        self.setWindowTitle('Not connected - site categorizer')
        for w in self.connectionDependent:
            w.setEnabled(False)


    def connectNetwork(self,db):
        logger.info('connectNetwork(%s)'%(str(db)))
        
        if db.isOpen():
            
            m = networkModel.networkModel(db=db,parent=self.secWidget)
            if not m.select():
                m = None
            
        else:
            m = None
            
                
        logger.info('connect mapper')
        self.mapper.setModel(m)
            
        if m:    
            self.secWidget.setDisplayColumn(m.fieldIndex('sec'))
            self.secWidget.setModelPKColumn(m.fieldIndex('sec')) 
            
            self.mapper.addMapping(self.oneWayBox,m.fieldIndex('one_way'))
            self.mapper.addMapping(self.noteEdit,m.fieldIndex('note'))
            self.mapper.addMapping(self.checkedBox,m.fieldIndex('checked'))
            
        self.secWidget.setModel(m)#triggers setSection. mapper model needs setting before this.
        
             
    def connectCategories(self,db):
        logger.info('connectCategories(%s)'%(str(db)))
        
        if db.isOpen():
            self.policyModel = QSqlTableModel(db=db,parent=self)
        else:
             self.policyModel = None
        
        self.policyView.setModel(self.policyModel)
        
        if self.policyModel:
            self.policyModel.setTable('categorizing.categories')
            self.policyModel.setEditStrategy(QSqlTableModel.OnFieldChange)   
            self.policyModel.setSort(self.policyModel.fieldIndex('pos'),Qt.AscendingOrder)
            self.policyModel.select()


        self.otherEventsView.setItemDelegateForColumn(self.otherEventsView.fieldIndex('category'),
            delegates.comboboxDelegate(self.otherEventsView,self.policyModel,self.policyModel.fieldIndex('cat')))

        
#called when plugin closed?
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

        
#opens help/index.html in default browser
    def openHelp(self):
        help_path = os.path.join(os.path.dirname(__file__),'help','overview.html')
        help_path = 'file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))

                     
    def getSec(self):
        if not self.secWidget.model():
            iface.messageBar().pushMessage("site_categorizer: not connected to database.",duration=4)
        else:
            return self.secWidget.getCurrentPK()
   

    def setupDatabase(self):
        msgBox=QMessageBox();
        msgBox.setText("Perform first time database setup?")
       # msgBox.setInformativeText("Continue?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        i = msgBox.exec_()
        
        if i==QMessageBox.Yes:
            folder = os.path.join(os.path.dirname(__file__),'database')
            file = os.path.join(folder,'setup.txt')
            
            with self.connectDialog.getCon() as con:
                databaseFunctions.runSetupFile(cur=con.cursor(),file=file,printCom=True,recursive=False)
                
            iface.messageBar().pushMessage("site_categoriser: prepared database",duration=4)


