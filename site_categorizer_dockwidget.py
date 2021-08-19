#from  qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QSettings,QUrl
import os

from PyQt5.QtWidgets import QDataWidgetMapper,QDockWidget,QMenu,QMessageBox,QMenuBar

#from . import marker
from .sec_ch_widget import sec_ch_widget
from qgis.utils import iface
from qgis.PyQt.QtSql import QSqlTableModel
from PyQt5.QtGui import QDesktopServices
#from .database_dialog.database_dialog import database_dialog

from . import networkModel,jcModel,otherEventsModel,delegates,databaseFunctions,databaseDialog

from .site_categorizer_dockwidget_base import Ui_site_categoriserDockWidgetBase



from secCh import secChWidget

#uiPath=os.path.join(os.path.dirname(__file__), 'site_categorizer_dockwidget_base.ui')
#FORM_CLASS, _ = uic.loadUiType(uiPath)

jcCats = ['Q1','Q2','Q3','K']




#class site_categoriserDockWidget(QDockWidget,FORM_CLASS):
class site_categoriserDockWidget(QDockWidget,Ui_site_categoriserDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(site_categoriserDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        
        self.secChTool = secChWidget.secChWidget(self)
        self.main_widget.layout().insertWidget(0,self.secChTool)

        #self.secChTool.sec_changed.connect(self.secChanged)

        self.mapper = QDataWidgetMapper(self)
        self.networkModel = None
        self.jcModel = None
        self.otherEventsModel = None
        
        self.addBox.addItems(jcCats)

        self.initJcMenu()
        self.initOtherEventsMenu()
        
        self.connectDialog = databaseDialog.databaseDialog(parent=self,name='site_categorizer_database')
        self.connectDialog.accepted.connect(self.connect)
        self.initTopMenu()
        self.disconnected()
        self.otherEventsAddButton.clicked.connect(self.addOtherEvent)        
        
        self.secChTool.secWidget.currentIndexChanged.connect(self.mapper.setCurrentIndex)#networkModel for both mapper and secWidget
        
       # self.addButton.clicked.connect(self.add)
        self.secChTool.secWidget.valueChanged.connect(self.changeSec)
        

    def changeSec(self,sec):
            
        print('change sec:%s'%(sec))
        if self.jcModel:
            self.jcModel.setSec(sec)
            
        if self.otherEventsModel:    
            self.otherEventsModel.setSec(sec)
                
        

    def initTopMenu(self):
        topMenu = QMenuBar()
        self.main_widget.layout().setMenuBar(topMenu)
        
        #database
        databaseMenu = topMenu.addMenu("Database")
        connectAct = databaseMenu.addAction('Connect to Database...')
        connectAct.triggered.connect(self.connectDialog.show)
        self.setupAct = databaseMenu.addAction('Setup Database for site categories...')
        self.setupAct.triggered.connect(self.setupDatabase)
        
        #help
        helpMenu = topMenu.addMenu("Help")
        openHelpAct = helpMenu.addAction('Open help (in your default web browser)')
        openHelpAct.triggered.connect(self.openHelp)
        


    def connect(self):

        db = self.connectDialog.getDb()

        if not db.isOpen():
            db.open()
        
        #these work with closed/invalid database.            
        self.connectCategories(db)
        self.connectNetwork(db)
        self.connectJc(db)
        self.connectOtherEvents(db)    
        
        
        if db.isOpen():#connected        
            self.setWindowTitle(db.databaseName()+' - site categorizer')       
            self.setupAct.setEnabled(True)
            self.addButton.setEnabled(True)
        
   
                    
        else:        
            iface.messageBar().pushMessage('site categorizer: could not connect to database',duration=4)
            self.disconnected()

            
     
    def disconnected(self):
        self.setWindowTitle('Not connected - site categorizer')
        self.setupAct.setEnabled(False)
        self.addButton.setEnabled(False)
     

    def connectNetwork(self,db):
        self.networkModel = networkModel.networkModel(db=db,parent=self)
        
        self.secChTool.secWidget.setModel(self.networkModel)
        self.secChTool.secWidget.setModelColumn(self.networkModel.fieldIndex('sec'))
        
        self.mapper.setModel(self.networkModel)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
        
        self.mapper.addMapping(self.one_way_box,self.networkModel.fieldIndex('one_way'))
        self.mapper.addMapping(self.note_edit,self.networkModel.fieldIndex('note'))
        self.mapper.addMapping(self.checked_box,self.networkModel.fieldIndex('checked'))
            

    def connectCategories(self,db):
        self.policyModel = QSqlTableModel(db=db,parent=self)
        self.policyView.setModel(self.policyModel)
        self.policyModel.setTable('categorizing.categories')
        self.policyModel.setEditStrategy(QSqlTableModel.OnFieldChange)   
        self.policyModel.setSort(self.policyModel.fieldIndex('pos'),Qt.AscendingOrder)
        self.policyModel.select()


    def connectOtherEvents(self,db):
        
        self.otherEventsModel = otherEventsModel.otherEventsModel(db=db,parent=self)
        self.otherEventsView.setModel(self.otherEventsModel)
        self.otherEventsView.hideColumn(self.otherEventsModel.fieldIndex('pk'))
        self.otherEventsView.hideColumn(self.otherEventsModel.fieldIndex('sec'))
        self.otherEventsView.hideColumn(self.otherEventsModel.fieldIndex('geom'))

        #self.secChTool.sec_changed.connect(self.otherEventsModel.setSec)
        
        #if self.secChTool.current_sec():
         #   self.otherEventsModel.setSec(self.secChTool.current_sec())
        
        
        
    def addOtherEvent(self):
        if self.otherEventsModel:
            sec = self.getSec()
            if sec:
                self.otherEventsModel.add(sec)
            
        
#called when plugin closed?
    def closeEvent(self, event):
        self.closingPlugin.emit()
        del self.secChTool.chWidget.marker
        event.accept()


        
#opens help/index.html in default browser
    def openHelp(self):
        help_path = os.path.join(os.path.dirname(__file__),'help','overview.html')
        help_path = 'file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))

        
    def connectJc(self,db):
        self.jcModel = jcModel.jcModel(parent=self,db=db)
        self.jcView.setModel(self.jcModel)
        self.jcView.hideColumn(self.jcModel.fieldIndex('geom'))
        self.jcView.hideColumn(self.jcModel.fieldIndex('pk'))
        self.jcModel.dataChanged.connect(lambda:self.jcModel.process(sec=self.secChTool.current_sec()))#reprocess section when jc table changed.
        self.jcView.setItemDelegateForColumn(self.jcModel.fieldIndex('category'),delegates.comboboxDelegate(self,items=jcCats))

       
    def add(self):
        sec = self.getSec()
        if sec and self.jcModel:
            self.jcModel.add(sec,self.secChTool.current_ch(),self.addBox.currentText())
           
        
    def getSec(self):
        sec = self.secChTool.current_sec()
        if sec:
            return sec
        iface.messageBar().pushMessage("site_categorizer: select a valid section before adding events.",duration=4)
    
    
    def remove(self):
        rows = []
        for index in self.jcView.selectedIndexes():
            rows.append(index.row())
        rows.sort(reverse=True)
        for row in rows:
            self.jcView.model().removeRow(row, self.jcView.rootIndex())

        self.jcView.model().select()
   
        
   
    def otherEventsRemove(self):
        rows = []
        for index in self.otherEventsView.selectedIndexes():
            rows.append(index.row())
        rows.sort(reverse=True)
        for row in rows:
            self.otherEventsView.model().removeRow(row, self.otherEventsView.rootIndex())

        self.otherEventsView.model().select()
        
        
#sets ch of sec_ch widget to minimum chainage of selected rows of jcView
    def setCh(self):
        self.secChTool.setCh(min([i.sibling(i.row(),1).data() for i in self.jcView.selectedIndexes()]))
        


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


#for requested view
    def initJcMenu(self):
        self.jc_menu = QMenu()
        drop_act = self.jc_menu.addAction('drop selected rows')
        drop_act.triggered.connect(self.remove)

        setChAct = self.jc_menu.addAction('set chainage from selected rows.')
        setChAct.triggered.connect(self.setCh)

        self.jcView.setContextMenuPolicy(Qt.CustomContextMenu);
        #self.jcView.customContextMenuRequested.connect(lambda pt:self.jc_menu.exec_(self.mapToGlobal(pt)))
        self.jcView.customContextMenuRequested.connect(lambda pt:self.jc_menu.exec_(self.jcView.mapToGlobal(pt)))


    def initOtherEventsMenu(self):
        self.otherEventsMenu = QMenu()
        dropAct = self.otherEventsMenu.addAction('drop selected rows')
        dropAct.triggered.connect(self.otherEventsRemove)

        #setChAct = self.jc_menu.addAction('set chainage from selected rows.')
       # setChAct.triggered.connect(self.setCh)

        self.otherEventsView.setContextMenuPolicy(Qt.CustomContextMenu);
        #self.jcView.customContextMenuRequested.connect(lambda pt:self.jc_menu.exec_(self.mapToGlobal(pt)))
        self.otherEventsView.customContextMenuRequested.connect(lambda pt:self.otherEventsMenu.exec_(self.otherEventsView.mapToGlobal(pt)))