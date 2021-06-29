--table of junctiona and crossings/

set search_path to categorizing,public;


drop table if exists jc;

create table if not exists jc

(
sec text references network(sec) on delete cascade on update cascade
,ch int
,category text references categories(cat) on update cascade
,geom geometry('Point',27700)
,pk serial primary key
);
