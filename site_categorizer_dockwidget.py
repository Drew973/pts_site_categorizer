from  qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QSettings,QUrl
import os

from PyQt5.QtWidgets import QDataWidgetMapper,QDockWidget,QMenu,QMessageBox,QMenuBar

#from . import marker
from .sec_ch_widget import sec_ch_widget
from.site_cat_dd import site_cat_dd
from qgis.utils import iface
from qgis.PyQt.QtSql import QSqlTableModel
from PyQt5.QtGui import QDesktopServices
from .database_dialog.database_dialog import database_dialog



from . import networkModel,jcModel,delegates,databaseFunctions


uiPath=os.path.join(os.path.dirname(__file__), 'site_categorizer_dockwidget_base.ui')
FORM_CLASS, _ = uic.loadUiType(uiPath)


jcCats = ['Q1','Q2','Q3','K']


class site_categoriserDockWidget(QDockWidget,FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(site_categoriserDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.add_button.clicked.connect(self.add)

        self.dd=None#database_interface subclass
        
        self.ch_tool=sec_ch_widget.sec_ch_widget(self)
        self.main_widget.layout().insertWidget(0,self.ch_tool)

        self.ch_tool.sec_changed.connect(self.secChanged)
        self.init_jc_menu()      
        self.initTopMenu()
        self.setWindowTitle('not connected - site categorizer')
        self.networkModel = None
        self.addBox.addItems(jcCats)


    def initTopMenu(self):
        topMenu = QMenuBar()
        self.main_widget.layout().setMenuBar(topMenu)
        
        #database
        databaseMenu = topMenu.addMenu("Database")
        connectAct = databaseMenu.addAction('Connect to Database...')
        connectAct.triggered.connect(self.connect)
        setupAct = databaseMenu.addAction('Setup Database for site categories...')
        setupAct.triggered.connect(self.setupDatabase)
        
        #help
        helpMenu = topMenu.addMenu("Help")
        openHelpAct = helpMenu.addAction('Open help (in your default web browser)')
        openHelpAct.triggered.connect(self.openHelp)
        


    def connect(self):
        db=database_dialog(self).exec_()
        
        try:
            self.dd = site_cat_dd(db)
            
            self.dd.sql('set search_path to categorizing,public;')
            self.setWindowTitle(db.databaseName()+' - site categorizer')
            self.connectCategories(db)
            
            self.networkModel = networkModel.networkModel(db=db,parent=self)
            self.setupJc(db)
            
            
            
            self.mapper = QDataWidgetMapper(self)
            self.mapper.setModel(self.networkModel)
            
            self.mapper.addMapping(self.one_way_box,self.networkModel.fieldIndex('one_way'))
            self.mapper.addMapping(self.note_edit,self.networkModel.fieldIndex('note'))
            self.mapper.addMapping(self.checked_box,self.networkModel.fieldIndex('checked'))
            
    
            
            
        except Exception as e:
            iface.messageBar().pushMessage("could not connect to database. %s"%(str(e)),duration=4)
            self.setWindowTitle('not connected - site categorizer')           
            self.dd = None



    def connectCategories(self,db):
        self.policyModel = QSqlTableModel(db=db)
        self.policyView.setModel(self.policyModel)
        self.policyModel.setTable('categorizing.categories')
        self.policyModel.setEditStrategy(QSqlTableModel.OnFieldChange)   
        self.policyModel.setSort(self.policyModel.fieldIndex('pos'),Qt.AscendingOrder)
        self.policyModel.select()


#when is this called?   
    def closeEvent(self, event):
        print('closing plugin')
        if self.dd:
            self.dd.disconnect()
            
        del self.ch_tool

        self.closingPlugin.emit()
        event.accept()


        
#opens help/index.html in default browser
    def openHelp(self):
        help_path=os.path.join(os.path.dirname(__file__),'help','overview.html')
        help_path='file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))

        
    def setupJc(self,db):
        self.jc_model = jcModel.jcModel(parent=self,db=db)
        self.jc_view.setModel(self.jc_model)
        self.jc_view.hideColumn(self.jc_model.fieldIndex('geom'))
        self.jc_view.hideColumn(self.jc_model.fieldIndex('pk'))
        self.jc_model.dataChanged.connect(lambda:self.jc_model.process_section(sec=self.ch_tool.current_sec()))#reprocess section when jc table changed.
        
        self.jc_view.setItemDelegateForColumn(self.jc_model.fieldIndex('category'),delegates.comboboxDelegate(self,items=jcCats))
        
        if self.ch_tool.current_sec():
            self.secChanged(self.ch_tool.current_sec())
       
        
    def secChanged(self,sec):
        
        print(sec)
        
        if self.networkModel:#connected if this not None
        
            self.jc_model.setFilter("sec='%s'"%(sec))
            self.jc_model.select()
        
            row = self.networkModel.find(self.networkModel.fieldIndex('sec'),sec)
        
            if row:
                self.mapper.setCurrentIndex(row)
            else:
                iface.messageBar().pushMessage('site categorizer: section %s not found in database'%(sec),duration=4)
                
  
        else:
            iface.messageBar().pushMessage('site categorizer: not connected to database',duration=4)


       
    def add(self):
        sec = self.getSec()
        if sec and self.jc_model:
            self.jc_model.add(sec,self.ch_tool.current_ch(),self.addBox.currentText())
           
        
    def getSec(self):
        sec=self.ch_tool.current_sec()
        if sec:
            return sec
        iface.messageBar().pushMessage("site_categorizer: select a valid section before adding events.",duration=4)


    def processSec(self):
        sec = self.getSec()
        dd = self.getDbInterface()
        if sec and dd:
            dd.process_section(sec)
            self.jc_model.select()
    
    
    def processAll(self):
        dd = self.getDbInterface()
        if dd:
            dd.process_all()
            self.jc_model.select()
    
    
    def remove(self):
        rows = []
        for index in self.jc_view.selectedIndexes():
            rows.append(index.row())
        rows.sort(reverse=True)
        for row in rows:
            self.jc_view.model().removeRow(row, self.jc_view.rootIndex())

        self.jc_view.model().select()
        
        
        
#sets ch of sec_ch widget to minimum chainage of selected rows of jc_view
    def set_ch(self):
        self.ch_tool.set_ch(min([i.sibling(i.row(),1).data() for i in self.jc_view.selectedIndexes()]))
        

    def layer_set(self):
        layer=self.layer_box.currentLayer().name()
        QSettings('pts', 'site_cats').setValue('layer',layer)


    def refresh_layer(self):
        layer=self.op_combobox.currentLayer()
        layer.dataProvider().forceReload()
        layer.triggerRepaint()


    def setupDatabase(self):
        msgBox=QMessageBox();
        msgBox.setText("Perform first time database setup.")
        msgBox.setInformativeText("Continue?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        i = msgBox.exec_()
        if i==QMessageBox.Yes:
            #self.dd.setup()
            folder = os.path.join(os.path.dirname(__file__),'database')
            file = os.path.join(folder,'setup.txt')
            
            
            with databaseFunctions.dbToCon(self.dd.db) as con:
                databaseFunctions.runSetupFile(cur=con.cursor(),file=file,folder=folder,printCom=True)
                
            iface.messageBar().pushMessage("site_categoriser: prepared database",duration=4)


#for requested view
    def init_jc_menu(self):
        self.jc_menu = QMenu()
        drop_act=self.jc_menu.addAction('drop selected rows')
        drop_act.triggered.connect(self.remove)

        set_ch_act=self.jc_menu.addAction('set chainage from selected rows.')
        set_ch_act.triggered.connect(self.set_ch)

        self.jc_view.setContextMenuPolicy(Qt.CustomContextMenu);
        #self.jc_view.customContextMenuRequested.connect(lambda pt:self.jc_menu.exec_(self.mapToGlobal(pt)))
        self.jc_view.customContextMenuRequested.connect(lambda pt:self.jc_menu.exec_(self.jc_view.mapToGlobal(pt)))

        








        
