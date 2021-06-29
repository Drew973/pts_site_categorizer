create table if not exists network (
sec varchar primary key
,meas_len float
,geom geometry('LineString',27700)
,one_way bool
,road varchar
,rbt bool
,road_class categorizing.cat--default category for section. should be A,B,C or R
,note varchar
,checked bool
)