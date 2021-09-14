from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt


import logging
logger = logging.getLogger(__name__)

'''
command to delete primary keys from model.
model needs:
    delete(pks) method that returns data.
    insert(data) method that retuns primary keys
can be used for multiple rows depending on insert and delete methods
'''
class deleteCommand(QUndoCommand):

    def __init__(self,model,pks, description='delete many'):
        super().__init__(description)
        self.model = model
        self.pks = pks
     

    def redo(self):
        logger.info('deleteCommand.redo();pks:%s'%(self.pks))
        self.data = self.model.delete(self.pks)


    def undo(self):
        logger.info('deleteManyCommand.undo();data:%s'%(self.data))
        self.pks = self.model.insert(self.data)


'''
command to insert data into model.
model needs:
    delete(pks) method that returns data.
    insert(data) method that retuns primary keys
can be used for multiple rows depending on insert and delete methods
'''
class insertCommand(QUndoCommand):

    def __init__(self,model,data, description='delete many'):
        super().__init__(description)
        self.model = model
        self.data = data
     

    def redo(self):
        logger.info('insertCommand.redo();data:%s'%(self.data))
        self.pks = self.model.insert(self.data)


    def undo(self):
        logger.info('insertCommand.undo();data:%s'%(self.data))
        self.data = self.model.delete(self.pks)

