from PyQt5.QtWidgets import QUndoCommand,QComboBox

from PyQt5.QtCore import pyqtSignal

'''
command to undo change to currentIndex of combobox
no reason can't be pushed AFTER the actual change.
'''
class changeIndexCommand(QUndoCommand):

    def __init__(self,comboBox,oldIndex,newIndex,description='change item'):
        super().__init__(description)
        self.box = comboBox
        self.oldIndex = oldIndex
        self.newIndex = newIndex

    def redo(self):
        self.box.createCommand = False
        self.box.setCurrentIndex(self.newIndex)
        self.box.createCommand = True

    def undo(self):
        self.box.createCommand = False
        self.box.setCurrentIndex(self.oldIndex)
        self.box.createCommand = True
        

'''
QCombobox doesn't seem to have overwritable method called when value changed.
createCommand variable defines if changing index should create command.
'''
class undoableComboBox(QComboBox):
   # indexChange = pyqtSignal(int,int)#old index,new index
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.undoStack = None
        self.currentIndexChanged.connect(self.onIndexChanged) 
        self.oldIndex = self.currentIndex()
        self.createCommand = True
        
    #set undoStack and remember currentIndex
    def setUndoStack(self,undoStack):
        self.undoStack = undoStack
        self.oldIndex = self.currentIndex()
   
   #index = new index = currentValue()
    def onIndexChanged(self,index):
        if index != self.oldIndex:
            #print(self.oldIndex,index)
            #self.indexChange.emit(self.oldIndex,index)
            
            if self.createCommand and not self.undoStack is None:
                self.undoStack.push(changeIndexCommand(self,self.oldIndex,index))

            self.oldIndex = index

  
if __name__ =='__console__':
    u = QUndoStack()
    b = undoableComboBox()
    b.addItems(['a','b','c'])
    b.setUndoStack(u)
    b.show()