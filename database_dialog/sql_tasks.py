
from qgis.core import QgsTask

from qgis.utils import iface

from psycopg2.extras import execute_batch







class cancelable_sql(QgsTask):



    def __init__(self,con,sql,args=None,sucess_message=None):

        QgsTask.__init__(self)

        self.con=con

        self.cur=con.cursor()

        self.sql=sql

        self.args=args

        self.sucess_message=sucess_message



        

    def run(self):

        cur=self.con.cursor()

        try:

            with self.con:

                if self.args:

                    self.cur.execute(self.sql,self.args)

                else:

                    self.cur.execute(self.sql)#with makes con commit here

            return True

        except Exception as e:

            self.err=e

            return False



#result bool

    def finished(self,result):

        iface.messageBar().clearWidgets()

        if result:
            if self.sucess_message:
                iface.messageBar().pushMessage(self.sucess_message)

        else:

            iface.messageBar().pushMessage(str(self.err))



    

    def cancel(self):

        self.con.cancel()#psycopg2 conection can be cancelled from any thread.

        QgsTask.cancel(self)





class cancellable_batch(cancelable_sql):



    def run(self):

        cur=self.con.cursor()

        try:

            with self.con:

                    execute_batch(self.cur,q,vals)

            return True

        except Exception as e:

            self.err=e

            return False

    





class cancelable_queries(QgsTask):



#args is list of arguments.

    

    def __init__(self,con,queries,args=None,sucess_message=None):

        QgsTask.__init__(self)

        self.con=con

        self.cur=con.cursor()

        self.queries=queries

        

        if args:

            if len(args)==len(queries):

                   self.args=args

            else:

                   raise ValueError('cancelable_queries:length of queries!= length of arguments')

        else:

            self.args=[None for q in queries]

                        

        self.sucess_message=sucess_message

        

        

    def run(self):

        cur=self.con.cursor()



        try:

            with self.con: #with makes con commit here

                for i,v in enumerate(self.queries):

                    if self.isCanceled():

                        return False

                    self.cur.execute(v,self.args[i])

                    self.setProgress(100*float(i)/len(self.queries))#setProgress takes float from 0 to 100 and emits progressChanged signal

            return True

        

        except Exception as e:

            self.err=e

            return False



#result bool

    def finished(self,result):

        iface.messageBar().clearWidgets()

        if result:
            if self.sucess_message:
                iface.messageBar().pushMessage(self.sucess_message)

        else:

            iface.messageBar().pushMessage(str(self.err))



    

    def cancel(self):

        self.con.cancel()#psycopg2 conection can be cancelled from any thread.

        QgsTask.cancel(self)





class cancelable_batches(cancelable_queries):



    def run(self):

        cur=self.con.cursor()



        try:

            with self.con: #with makes con commit here

                for i,v in enumerate(self.queries):

                    if self.isCanceled():

                        return False

                    execute_batch(self.cur,v,self.args[i])

                    self.setProgress(100*float(i)/len(self.queries))#setProgress takes float from 0 to 100 and emits progressChanged signal

            return True

        

        except Exception as e:

            self.err=e

            return False
