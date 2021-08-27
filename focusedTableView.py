
from PyQt5.QtWidgets import QTableView
#from PyQt5.QtCore import QEvent




class focusedTableView(QTableView):


    def currentChanged(self,current,previous):
        self.closePersistentEditor(previous)
        self.openPersistentEditor(current)
        super().currentChanged(current,previous)
    
    #self.openPersistentEditor(index)
    
    #self.closePersistentEditor(index)