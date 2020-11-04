from  qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal,Qt,QSettings
import os
from qgis.PyQt.QtWidgets import QDockWidget,QMenu
#from . import marker
from .sec_ch_widget import sec_ch_widget
from.site_cat_dd import site_cat_dd
from qgis.utils import iface
from qgis.PyQt.QtSql import QSqlDatabase,QSqlTableModel


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

        self.dd=site_cat_dd(self)
        
        self.ch_tool=sec_ch_widget.sec_ch_widget(self,self.dd)
        self.main_widget.layout().insertWidget(1,self.ch_tool)

        self.connect_button.clicked.connect(self.connect)
        self.ch_tool.sec_changed.connect(self.sec_changed)
        self.prepare_database_button.clicked.connect(self.setup_database)
        
        self.init_jc_menu()


        
    def closeEvent(self, event):
        self.dd.disconnect()
        self.ch_tool.remove_marker()
        self.closingPlugin.emit()
        event.accept()


    def connect(self):
        if self.dd.exec_():
            if self.dd.connected:
                self.database_label.setText('Connected to %s'%(self.dd.db.databaseName()))
                self.setup_jc()
                #self.setup_op()

                try:
                    self.dd.sql('set search_path to categorizing,public;')

                except:
                    pass
            else:
                self.database_label.setText('Not Connected')
        
           
    def setup_jc(self):
        self.jc_model = QSqlTableModel(db=self.dd.db)
        self.jc_model.setTable('categorizing.jc')
        self.jc_model.setEditStrategy(QSqlTableModel.OnFieldChange)       
        self.jc_model.setSort(1,Qt.AscendingOrder)#columns 0 indexed?
        self.jc_model.setFilter("sec=''")
        self.jc_model.select()
        self.jc_view.setModel(self.jc_model)
        self.jc_view.hideColumn(3)
 

    def setup_op(self):
        self.op_model = QSqlTableModel(db=self.dd.db)
        self.op_model.setTable('categorizing.op')
        #self.events_model.setHeaderData(1, Qt.Horizontal, "cat")
        self.op_model.setEditStrategy(QSqlTableModel.OnFieldChange)       
        #self.op_model.setSort(1,Qt.AscendingOrder)#columns 0 indexed?
        self.op_model.setFilter("sec=''")
        self.op_model.select()
        self.op_table.setModel(self.op_model)
        #self.op_table.hideColumn(0)
        #self.op_table.hideColumn(6)
        
         
    def sec_changed(self,sec):
        if self.dd.connected:
            if not self.dd.sec_exists(sec):
                iface.messageBar().pushMessage('section %s not found in database'%(sec),duration=4)

                #lookup if section checked and set checkbox to this 
                #self.checked_box.setChecked(self.con.get_query("select checked from sects where sec=%s limit 1",[self.sec])[0]['checked'])
                #select and zoom to section
            self.jc_model.setFilter("sec='%s'"%(sec))
            self.jc_model.select()
            #self.op_model.setFilter("sec='%s'"%(sec))
            #self.op_model.select()


    #def set_checked(self):
     #   if self.check_section_exists(self.section.text()):
      #      self.con.sql("update sects set checked=%s where sec=%s",[self.checked_box.isChecked(),self.sec])

       
    def add(self):
        sec=self.ch_tool.current_sec()
        if sec is None:
            iface.messageBar().pushMessage("site_categoriser: select a valid section before adding events.",duration=4)
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


    def layer_set(self):
        layer=self.layer_box.currentLayer().name()
        QSettings('pts', 'site_cats').setValue('layer',layer)


    def refresh_layer(self):
        layer=self.op_combobox.currentLayer()
        layer.dataProvider().forceReload()
        layer.triggerRepaint()


    def update_section(self):
       # self.con.sql("select update_events(%s);",[self.sec])
        #self.con.sql("select process_section(%s);",[self.sec])
        #self.con.sql("select process_section_r(%s);",[self.sec])
        self.dd.process_section(self.ch_tool.current_sec())#

        self.jc_model.select()
        #self.op_model.select()
        

    def setup_database(self):
        self.dd.setup()
        iface.messageBar().pushMessage("site_categoriser: prepared database",duration=4)

#for requested view
    def init_jc_menu(self):
        self.jc_menu = QMenu()
        drop_act=self.jc_menu.addAction('drop selected rows')
        drop_act.triggered.connect(self.remove)

        self.jc_view.setContextMenuPolicy(Qt.CustomContextMenu);
        self.jc_view.customContextMenuRequested.connect(lambda pt:self.jc_menu.exec_(self.mapToGlobal(pt)))

        








        
