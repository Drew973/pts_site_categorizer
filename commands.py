from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt



import logging
logger = logging.getLogger(__name__)


'''
QUndoCommand subclasses for controlling models
'''



'''
model needs insert method(...) that returns primary key of new row.

model needs delete(pk) method that
returns dict like of insert() arguments to reinsert deleted row

data is dict of args to model.insert() .Only args without default necessary.
'''
class insertCommand(QUndoCommand):

    def __init__(self,model,data, description='insert'):
        super(insertCommand, self).__init__(description)
        self.model = model
        self.data = data
       # self.pk = None
        

    def redo(self):
        logger.info('insertCommand.redo;data:%s'%(str(self.data)))
        self.pk = self.model.insert(**self.data)


    def undo(self):
        logger.info('insertCommand.undo;pk:%s'%(str(self.pk)))
        self.data = self.model.delete(self.pk)




class updateCommand(QUndoCommand):

    def __init__(self,model,data, description='insert'):
        super(insertCommand, self).__init__(description)
        self.model = model
        self.data = data
       # self.pk = None
        

    def redo(self):
        self.oldValue=0
        self.model.update(self.pk,self.newValue)


    def undo(self):
        self.data = self.model.delete(self.pk)




class deleteCommand(QUndoCommand):

    def __init__(self,model,pk, description='delete'):
        super(deleteCommand, self).__init__(description)
        self.model = model
        self.pk = pk
     

    def redo(self):
        self.data = self.model.delete(self.pk)


    def undo(self):
        self.pk = self.model.insert(**self.data)



#same as deleteCommand but with insertMany(data) method
class deleteManyCommand(QUndoCommand):

    def __init__(self,model,pks, description='delete many'):
        super(deleteManyCommand, self).__init__(description)
        self.model = model
        self.pks = pks
     

    def redo(self):
        logger.info('deleteManyCommand.redo();pks:%s'%(self.pks))
        self.data = self.model.deleteMany(self.pks)


    def undo(self):
        logger.info('deleteManyCommand.undo();data:%s'%(self.data))
        self.pks = self.model.insertMany(self.data)






class modelUpdateCommand(QUndoCommand):

    def __init__(self,model,index,value,role=Qt.EditRole, description='update'):
        super(deleteCommand, self).__init__(description)
        self.model = model
        self.index = index
        self.newValue = value
        self.role = role
     

    def redo(self):
        self.oldValue = self.model.data(self.index,self.role)
        self.model.setData(self.index,self.newValue,self.role)


    def undo(self):
        self.model.setData(self.index,self.oldValue,self.role)




#buggy
#model = qsqltablemodel like
class deleteRowsCommand(QUndoCommand):

    def __init__(self,model,rows, description='delete rows',select=True):
        super(deleteRowsCommand, self).__init__(description)
        self.model = model
        self.rows = sorted(rows,reverse=True)
        self.select = select

    def redo(self):
        logger.info('deleteRowsCommand.redo;rows=%s'%(str(self.rows)))
        self.data = [self.model.record(row) for row in self.rows]
        for row in self.rows:
            self.model.removeRow(row)
        
        if self.select:
            self.model.select()


    def undo(self):
        logger.info('deleteRowsCommand.undo;data=%s'%(str(self.data)))
        for i,rec in enumerate(self.data):
            #self.model.insertRecord(self.rows[i],rec)
            self.model.insertRecord(-1,rec)
            
        if self.select:
            self.model.select()
            
            
            
            
            
            
            
            
            