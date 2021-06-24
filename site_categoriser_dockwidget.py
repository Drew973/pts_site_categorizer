from  qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QSettings,QUrl
import os
from qgis.PyQt.QtWidgets import QDockWidget,QMenu,QMessageBox,QMenuBar
#from . import marker
from .sec_ch_widget import sec_ch_widget
from.site_cat_dd import site_cat_dd
from qgis.utils import iface
from qgis.PyQt.QtSql import QSqlTableModel
from PyQt5.QtGui import QDesktopServices
from .database_dialog.database_dialog import database_dialog




def fixHeaders(path):
    with open(path) as f:
        t=f.read()

    r={'qgsfieldcombobox.h':'qgis.gui','qgsmaplayercombobox.h':'qgis.gui'}
    for i in r:
        t=t.replace(i,r[i])

    with open(path, "w") as f:
        f.write(t)


uiPath=os.path.join(os.path.dirname(__file__), 'site_categoriser_dockwidget_base.ui')
fixHeaders(uiPath)
FORM_CLASS, _ = uic.loadUiType(uiPath)


class site_categoriserDockWidget(QDockWidget,FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(site_categoriserDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.add_button.clicked.connect(self.add)

        self.dd=None#database_interface subclass
        
        self.ch_tool=sec_ch_widget.sec_ch_widget(self)
        self.main_widget.layout().insertWidget(0,self.ch_tool)

        self.ch_tool.sec_changed.connect(self.sec_changed)
        self.init_jc_menu()      
        self.initTopMenu()
        

    def initTopMenu(self):
        topMenu = QMenuBar()
        self.main_widget.layout().setMenuBar(topMenu)
        
        #help
        helpMenu = topMenu.addMenu("Help")

        openHelpAct = helpMenu.addAction('Open help (in your default web browser)')
        openHelpAct.triggered.connect(self.openHelp)
        
        #database
        databaseMenu = topMenu.addMenu("Database")
        connectAct = databaseMenu.addAction('Connect to Database...')
        connectAct.triggered.connect(self.connect)
        setupAct = databaseMenu.addAction('Setup Database for site categories...')
        setupAct.triggered.connect(self.setupDatabase)

        
        
    def connect(self):
        db=database_dialog(self).exec_()
        try:
            self.dd=site_cat_dd(db)
            self.setup_jc()
            self.note_edit.textChanged.connect(lambda note:self.dd.set_note(self.ch_tool.current_sec(),note))#will these signals stay connected if  db changed? move to init and add if?
            self.one_way_box.stateChanged.connect(lambda:self.dd.set_one_way(self.ch_tool.current_sec(),self.one_way_box.isChecked()))
            self.checked_box.stateChanged.connect(lambda:self.dd.set_checked(self.ch_tool.current_sec(),self.checked_box.isChecked()))
            #self.setup_op()
            self.dd.sql('set search_path to categorizing,public;')
            self.setWindowTitle(self.dd.db_name()+' - site categorizer')
            
            
        except Exception as e:
            iface.messageBar().pushMessage("could not connect to database. %s"%(str(e)),duration=4)
            self.database_label.setText('Not Connected')            
            self.dd=None


#when is this called?   
    def closeEvent(self, event):
        if self.dd:
            self.dd.disconnect()


        self.closingPlugin.emit()
        event.accept()


        
#opens help/index.html in default browser
    def openHelp(self):
        help_path=os.path.join(os.path.dirname(__file__),'help','overview.html')
        help_path='file:///'+os.path.abspath(help_path)
        QDesktopServices.openUrl(QUrl(help_path))

        
    def setup_jc(self):
        self.jc_model = QSqlTableModel(db=self.dd.db)
        self.jc_model.setTable('categorizing.jc')
        self.jc_model.setEditStrategy(QSqlTableModel.OnFieldChange)       
        self.jc_model.setSort(1,Qt.AscendingOrder)#columns 0 indexed?
        self.jc_model.setFilter("sec=''")
        self.jc_view.setModel(self.jc_model)
        self.jc_view.hideColumn(3)#hide geom column
        self.jc_view.hideColumn(4)#hide pk column
        self.jc_model.select()

        self.jc_model.dataChanged.connect(lambda:self.dd.process_section(self.ch_tool.current_sec()))#reprocess section when jc table changed.
        print('setup_jc')
         
    def sec_changed(self,sec):
        print(sec)
        if self.dd:
            if not self.dd.sec_exists(sec):
                iface.messageBar().pushMessage('section %s not found in database'%(sec),duration=4)

                #lookup if section checked and set checkbox to this 
                #self.checked_box.setChecked(self.con.get_query("select checked from sects where sec=%s limit 1",[self.sec])[0]['checked'])
            self.jc_model.setFilter("sec='%s'"%(sec))
            self.jc_model.select()
            self.note_edit.setText(self.dd.get_note(sec))

            self.one_way_box.setChecked(self.dd.is_one_way(sec))
            self.checked_box.setChecked(self.dd.is_checked(sec))
  

    #def set_checked(self):
     #   if self.check_section_exists(self.section.text()):
      #      self.con.sql("update sects set checked=%s where sec=%s",[self.checked_box.isChecked(),self.sec])

       
    def add(self):
        sec=self.ch_tool.current_sec()
        if sec is None:
            iface.messageBar().pushMessage("site_categoriser: select a valid section before adding events.",duration=4)
            return


        if self.dd:
            self.dd.add_to_jc(sec,self.ch_tool.current_ch(),self.cat_combo.currentText())
            self.update_section()
            
        else:
            #self.con.sql("select add_to_jc(%s,%s,%s) ",[sec,self.ch_tool.current_ch(),self.cat_combo.currentText()])
            self.dd.add_to_jc(sec,self.ch_tool.current_ch(),self.cat_combo.currentText())
            self.update_section()
        

    def remove(self):
        rows = []
        for index in self.jc_view.selectedIndexes():
            rows.append(index.row())
        rows.sort(reverse=True)
        for row in rows:
            self.jc_view.model().removeRow(row, self.jc_view.rootIndex())
        self.update_section()

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


    def update_section(self):
        self.dd.process_section(self.ch_tool.current_sec())#
        self.jc_model.select()
        

    def setupDatabase(self):
        msgBox=QMessageBox();
        msgBox.setText("Perform first time database setup.");
        msgBox.setInformativeText("Continue?");
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
        msgBox.setDefaultButton(QMessageBox.No);
        i=msgBox.exec_()
        if i==QMessageBox.Yes:
            self.dd.setup()
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

        








        
