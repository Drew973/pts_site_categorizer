create table if not exists op(
sec text references network(sec) on update cascade
,reversed bool
,start_ch int
,end_ch int
,category text references categories(cat) on update cascade
,irl float
,geom geometry
)
--assuming category same for all lanes in same direction