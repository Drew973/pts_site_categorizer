from PyQt5.QtWidgets import QCompleter,QApplication,QComboBox
from PyQt5.QtCore import QStringListModel
import sys


class searchableComboBox(QComboBox):

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        
        # change completion mode of the default completer from InlineCompletion to PopupCompletion
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.lineEdit().editingFinished.connect(self.editingFinished)


    def editingFinished(self):
      #  print(self.currentData())
        data = self.itemText(self.currentIndex())
        self.lineEdit().setText(data)
        




if __name__=='__console__':
    #layer = iface.activeLayer()
    w = searchableComboBox()
    m = QStringListModel(['aa','ab','ac'])
    w.setModel(m)
    w.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = searchableComboBox()
    m = QStringListModel(['aa','ab','ac'])
    w.setModel(m)
    w.show()
    
    sys.exit(app.exec_())  
   
    