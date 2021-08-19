create table if not exists op(
sec text references network(sec) on update cascade
,reversed bool
,start_ch float
,end_ch float
,category text references categories(cat) on update cascade
,irl float
,geom geometry('linestring',27700)
)
--assuming category same for all lanes in same direction