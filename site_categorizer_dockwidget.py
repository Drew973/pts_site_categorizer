#from  qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl
import os

from PyQt5.QtWidgets import QDataWidgetMapper,QDockWidget,QMenu,QMessageBox,QMenuBar

#from . import marker
#from .sec_ch_widget import sec_ch_widget
from qgis.utils import iface
from qgis.PyQt.QtSql import QSqlTableModel
from PyQt5.QtGui import QDesktopServices
#from .database_dialog.database_dialog import database_dialog

from . import networkModel,jcModel,otherEventsModel,delegates,databaseFunctions,databaseDialog

from .site_categorizer_dockwidget_base import Ui_site_categoriserDockWidgetBase

import chainageDelegate


from PyQt5.QtWidgets import QUndoStack
#from PyQt5.QtWidgets import QUndoView




import logging
logging.basicConfig(filename=r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\site_categorizer\siteCategorizer.log', level=logging.INFO)
logger = logging.getLogger(__name__)



#from secCh import secChWidget

#uiPath=os.path.join(os.path.dirname(__file__), 'site_categorizer_dockwidget_base.ui')
#FORM_CLASS, _ = uic.loadUiType(uiPath)

jcCats = ['Q1','Q2','Q3','K']




#class site_categoriserDockWidget(QDockWidget,FORM_CLASS):
class site_categoriserDockWidget(QDockWidget,Ui_site_categoriserDockWidgetBase):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(site_categoriserDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        
        #self.secChTool = secChWidget.secChWidget(self)
        #self.main_widget.layout().insertWidget(0,self.secChTool)

        #self.secChTool.sec_changed.connect(self.secChanged)

        self.mapper = QDataWidgetMapper(self)
        self.networkModel = None
        self.jcModel = None
        self.otherEventsModel = None
        
        
        self.addBox.addItems(jcCats)

        
        self.connectDialog = databaseDialog.databaseDialog(parent=self,name='site_categorizer_database')
        self.connectDialog.accepted.connect(self.connect)
        
        self.initTopMenu()
        self.initJcMenu()
        self.initOtherEventsMenu()
        
        
        self.connectionDependent = [self.setupAct,self.addJcButton,self.secWidget,self.otherEventsAddButton,self.oneWayBox,self.noteEdit,self.checkedBox,self.addBox]
        self.disconnected()
        self.otherEventsAddButton.clicked.connect(self.addOtherEvent)        
        
        #self.secWidget.currentIndexChanged.connect(self.mapper.setCurrentIndex)#networkModel for both mapper and secWidget
        self.secWidget.currentIndexChanged.connect(self.changeRow)
        
        
        self.addJcButton.clicked.connect(self.addJc)
        #self.secWidget.valueChanged.connect(self.changeSec)
        #self.secWidget.currentIndexChanged.connect(self.chWidget.setRow)
        
        self.chWidget.setExcess(50)
        
        self.chainageDelegate = chainageDelegate.chainageDelegate(excess=50)
        #self.otherEventsView.activated.connect(lambda i: print(i))
        self.undoStack = QUndoStack(self)


    def changeRow(self,row):
        sec = self.secWidget.itemText(row)
        
        if self.jcModel:
            self.jcModel.setSec(sec)
            
        if self.otherEventsModel:    
            self.otherEventsModel.setSec(sec)     
        
        self.mapper.setCurrentIndex (row)
        self.chWidget.setRow(row)
        self.chainageDelegate.setRow(row)    
        self.secWidget.selectOnLayer(warn=False)
        

    def changeSec(self,sec):
            
        print('change sec:%s'%(sec))
        if self.jcModel:
            self.jcModel.setSec(sec)
            
        if self.otherEventsModel:    
            self.otherEventsModel.setSec(sec)
                
        

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
        undoAct = editMenu.addAction('Undo')
        redoAct = editMenu.addAction('Redo')
        
        
        
        
        #help
        helpMenu = topMenu.addMenu("Help")
        openHelpAct = helpMenu.addAction('Open help (in your default web browser)')
        openHelpAct.triggered.connect(self.openHelp)
        
        
        otherEventsMenu = topMenu.addMenu("Other Events")
        autoCurvaturesAct = otherEventsMenu.addAction('recalculate curvatures')
        autoCurvaturesAct.triggered.connect(self.autoCurvatures)
        autoCurvaturesAct2 = otherEventsMenu.addAction('recalculate curvatures and plot')
        autoCurvaturesAct2.triggered.connect(lambda:self.autoCurvatures(plot=True))


    def autoCurvatures(self,plot=False):
        if self.networkModel and self.otherEventsModel:
            self.otherEventsModel.autoCurvatures(networkModel=self.networkModel,row=self.secWidget.currentIndex(),plot=plot)



    def connect(self):
        logger.info('connect')
        
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
            for w in self.connectionDependent:
                w.setEnabled(True)
                
            self.changeRow(self.secWidget.currentIndex())        
   
                    
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
            self.networkModel = networkModel.networkModel(db=db,parent=self)
        else:
            self.networkModel = None
            
        
        self.secWidget.setModel(self.networkModel)
            
        self.chWidget.setModel(self.networkModel)
        self.chainageDelegate.setModel(self.networkModel)    
        
        
        logger.info('mapper')
        self.mapper.setModel(self.networkModel)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
            
        if self.networkModel:    
            self.secWidget.setDisplayColumn(self.networkModel.fieldIndex('sec'))
            self.secWidget.setModelPKColumn(self.networkModel.fieldIndex('sec'))            
            self.mapper.addMapping(self.oneWayBox,self.networkModel.fieldIndex('one_way'))
            self.mapper.addMapping(self.noteEdit,self.networkModel.fieldIndex('note'))
            self.mapper.addMapping(self.checkedBox,self.networkModel.fieldIndex('checked'))
            
           
             
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


    def connectOtherEvents(self,db):
        logger.info('connectOtherEvents(%s)'%(str(db)))
        
        if db.isOpen():
            self.otherEventsModel = otherEventsModel.otherEventsModel(db=db,parent=self)
        else:
             self.otherEventsModel = None
                   
        self.otherEventsView.setModel(self.otherEventsModel)
            
        if self.otherEventsModel:
            self.otherEventsView.hideColumn(self.otherEventsModel.fieldIndex('pk'))
            self.otherEventsView.hideColumn(self.otherEventsModel.fieldIndex('sec'))
            self.otherEventsView.hideColumn(self.otherEventsModel.fieldIndex('geom'))
        
            self.otherEventsView.setItemDelegateForColumn(self.otherEventsModel.fieldIndex('s_ch'), self.chainageDelegate)
            self.otherEventsView.setItemDelegateForColumn(self.otherEventsModel.fieldIndex('e_ch'), self.chainageDelegate)
            
            
    def addOtherEvent(self):
        if self.otherEventsModel:
            sec = self.getSec()
            if sec:
                self.otherEventsModel.add(sec)
            
        
#called when plugin closed?
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


        
#opens help/index.html in default browser
    def openHelp(self):
        help_path = os.path.join(os.path.dirname(__file__),'help','overview.html')
        help_path = 'file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))

        
    def connectJc(self,db):
        
        if db.isOpen():
            self.jcModel = jcModel.jcModel(parent=self,db=db)
        else:
             self.jcModel = None
             
        self.jcView.setModel(self.jcModel)
        
        if self.jcModel:
            self.jcView.hideColumn(self.jcModel.fieldIndex('geom'))
            self.jcView.hideColumn(self.jcModel.fieldIndex('pk'))
            self.jcModel.dataChanged.connect(lambda:self.jcModel.process(sec=self.secChTool.current_sec()))#reprocess section when jc table changed.
            self.jcView.setItemDelegateForColumn(self.jcModel.fieldIndex('category'),delegates.comboboxDelegate(self,items=jcCats))

       
    def addJc(self):
        sec = self.getSec()
        if sec and self.jcModel:
            self.jcModel.add(sec,self.chWidget.value(),self.addBox.currentText())
           
        
    def getSec(self):
        if not self.secWidget.model():
            iface.messageBar().pushMessage("site_categorizer: not connected to database.",duration=4)
        else:
            return self.secWidget.getCurrentPK()

    
    
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
        self.chWidget.setValue(min([i.sibling(i.row(),1).data() for i in self.jcView.selectedIndexes()]))
        


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