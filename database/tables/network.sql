
set search_path to categorizing,public;

create table if not exists network (
sec varchar primary key
,meas_len float
,geom geometry('LineString',27700)
,one_way bool
,road varchar
,rbt bool
,note varchar
,checked bool
,speed_limit int
,wkt text
);
