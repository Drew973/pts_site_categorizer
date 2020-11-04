from .database_dialog.database_dialog import database_dialog

#import psycopg2
from psycopg2.extras import DictCursor,execute_batch
from os import path
from qgis.PyQt.QtSql import QSqlQuery


class site_cat_dd(database_dialog):

    def sec_exists(self,sec):
        res=self.sql('select sec from network where sec=%(sec)s',{'sec':sec},True)
        res=[r for r in res]
        if res:
            return True


   # def meas_len(self,sec):
    #    res=self.sql('select meas_len from network where sec=%(sec)s',{'sec':sec},True)
     #   if res:
      #      return res[0]['meas_len']
       # else:
        #    raise KeyError('section % does not exist'%(sec))


        #section label sec and chainage ch  to x and y in crs
    #def ch_to_xy(self,sec,ch,crs):
    #    return self.sql("with a as (select ST_Transform(ch_to_point(%(sec)s,%(ch)s),%(crs)s) as p) select st_x(p) as x,st_y(p) as y from a",{'sec':sec,'ch':ch,'crs':crs},True)


   # def xy_to_sec_ch(self,x,y,crs,sec):
  #      return self.sql("select meas_sec_ch(%(sec)s,ST_Transform(ST_SetSRID(st_Point(%(x)s,%(y)s),%(crs)s),27700)) as sec_ch",{'sec':sec,'x':x,'y':y,'crs':crs},True)['sec_ch']
        

    def setup(self):
        folder=path.join(path.dirname(__file__),'database')
        self.run_setup_file('setup.txt',folder)



    def add_to_jc(self,sec,ch,cat):
        self.sql('insert into categorizing.jc(sec,ch,category,geom) values (%(sec)s,%(ch)s,%(cat)s,categorizing.ch_to_point(%(sec)s,%(ch)s))',{'sec':sec,'ch':ch,'cat':cat})


    def process_section(self,sec):
        self.sql('select process_sec(%(sec)s)',{'sec':sec})
