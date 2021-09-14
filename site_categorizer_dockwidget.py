from qgis.PyQt.QtCore import pyqtSignal,Qt,QUrl
import os

from PyQt5.QtWidgets import QDataWidgetMapper,QDockWidget,QMenu,QMessageBox,QMenuBar,QUndoStack,QUndoCommand


from qgis.utils import iface
from qgis.PyQt.QtSql import QSqlTableModel
from PyQt5.QtGui import QDesktopServices

from . import networkModel,jcModel,otherEventsModel,delegates,databaseFunctions,databaseDialog,commands,chainageDelegate

from .site_categorizer_dockwidget_base import Ui_site_categoriserDockWidgetBase


import logging

logging.basicConfig(filename=r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\site_categorizer\siteCategorizer.log',
                    level=logging.INFO,filemode='w')

logger = logging.getLogger(__name__)


jcCats = ['Q1','Q2','Q3','K']

'''
change row of QComboBox
'''
class changeRowCommand(QUndoCommand):

    def __init__(self,comboBox,row,description='change row'):
        super().__init__(description)
        self.comboBox = comboBox
        self.newRow = row
        self.oldRow = self.comboBox.currentIndex()
        logger.info('changeRowCommand.__init__;oldRow:%s;newRow:%d'%(self.oldRow,self.newRow))
        
        
    def setRow(self,row):
        self.newRow = row        
        
    def redo(self):
        self.comboBox.setCurrentIndex(self.newRow)
#        logger.info('changeRowCommand.redo;newRow:%d'%(self.newRow))

    def undo(self):
        self.comboBox.setCurrentIndex(self.oldRow)
#        logger.info('changeRowCommand.redo;oldRow:%d'%(self.oldRow))
        

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
        self.jcModel = None
        self.secRow = 0
        
        self.addBox.addItems(jcCats)

        self.undoStack = QUndoStack(self)
        
        self.connectDialog = databaseDialog.databaseDialog(parent=self,name='site_categorizer_database')
        self.connectDialog.accepted.connect(self.connect)
        
        self.initTopMenu()
        self.initJcMenu()
        
        
        self.connectionDependent = [self.setupAct,self.addJcButton,self.secWidget,self.otherEventsAddButton,self.oneWayBox,self.noteEdit,self.checkedBox,self.addBox]
        self.disconnected()
        self.otherEventsAddButton.clicked.connect(self.otherEventsView.addOtherEvent)                
        
        #self.csc = changeRowCommand(self.secWidget,row=0,description='change sec')
       # self.secWidget.currentIndexChanged.connect(lambda row:self.undoStack.push(changeRowCommand(self.secWidget,
             #                                                                            oldRow=self.secRow,
                  #                                                                       newRow=row,
                                                                                        # description='change sec')))
        self.secWidget.currentIndexChanged.connect(self.setSecRow)#happens 1st?
        
        #self.secWidget.currentIndexChanged.connect(self.pushChangeSecCommand)
        
        self.addJcButton.clicked.connect(self.addJc)
        self.chWidget.setExcess(50)
        #self.chainageDelegate = chainageDelegate.chainageDelegate(undoStack=self.undoStack,excess=50)
        self.otherEventsView.undoStack = self.undoStack
        

    def onSecActivated(self,row):
        csc = changeRowCommand()
        self.undoStack.push(csc)



#slot to be called from command
#everything that caused secWidget.currentIndexChanged should have undo
    def setSecRow(self,row):
        #self.csc = changeRowCommand(self.secWidget,row=0,description='change sec')

        if row <= self.secWidget.model().rowCount():
            if row!=self.secWidget.currentIndex():
                self.secWidget.setCurrentIndex(row)
            
            sec = self.secWidget.itemText(row)
            
            if self.jcModel:
                self.jcModel.setSec(sec)
                
                
            self.otherEventsView.setSection(self.secWidget.model(),row,sec)
             
            
            self.mapper.setCurrentIndex (row)
            self.chWidget.setRow(row)
           # self.chainageDelegate.setRow(row)    
            self.secWidget.selectOnLayer(warn=False)
            #self.otherEventsView.closeEditor()


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
        
        
        otherEventsMenu = topMenu.addMenu("Other Events")
        
        otherEventsMenu.addAction(self.otherEventsView.addAct)
        autoCurvaturesAct = otherEventsMenu.addAction('recalculate curvatures')
        autoCurvaturesAct.triggered.connect(self.autoCurvatures)
        autoCurvaturesAct2 = otherEventsMenu.addAction('recalculate curvatures and plot')
        autoCurvaturesAct2.triggered.connect(lambda:self.autoCurvatures(plot=True))


    def autoCurvatures(self,plot=False):
        
        if self.secWidget.model().rowCount>=0 and self.otherEventsView.model():
            self.self.otherEventsView.model().autoCurvatures(networkModel=self.secWidget.model(),row=self.secWidget.currentIndex(),plot=plot)



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
        self.connectJc(db)
        
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
            
        
        self.secWidget.setModel(m)
            
        self.chWidget.setModel(m)
        #self.chainageDelegate.setModel(m)    
        
        
        logger.info('mapper')
        self.mapper.setModel(m)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
            
        if m:    
            self.secWidget.setDisplayColumn(m.fieldIndex('sec'))
            self.secWidget.setModelPKColumn(m.fieldIndex('sec'))            
            self.mapper.addMapping(self.oneWayBox,m.fieldIndex('one_way'))
            self.mapper.addMapping(self.noteEdit,m.fieldIndex('note'))
            self.mapper.addMapping(self.checkedBox,m.fieldIndex('checked'))
            
           
             
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
            c = commands.insertCommand(model=self.jcModel,data={'sec':sec})
            self.undoStack.push(c)
            
            #self.jcModel.add(sec,self.chWidget.value(),self.addBox.currentText())
           
        
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


