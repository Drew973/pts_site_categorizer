drop table if exists other_events;

create table if not exists other_events(
sec varchar references network(sec) on delete cascade on update cascade
,reversed bool
,s_ch int
,e_ch int
,category cat)
;



create index on other_events(sec,reversed);