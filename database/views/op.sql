
drop view if exists op_view;

create view op_view as
with a as (select sec,reversed,unnest(array_distinct(0||array_agg(s_ch)||array_agg(e_ch)||meas_len(sec)::int)) as ch from categorizing.events group by sec,reversed)
,b as (select *,lead(ch) over (partition by sec,reversed order by ch) from a)
,c as (select *,max_cat(sec,reversed,int8range(ch,lead)),int8range(ch,lead,'[]') as rg from b where ch!=lead and not lead is null)--have sec,reversed,ch,lead,max_cat. want to merge where same as ajacent cats
,d as (select sec,reversed,max_cat,unnest(range_array_distinct(array_agg(rg))) as r from c group by sec,reversed,max_cat)
select sec
,reversed
,max_cat as category
,cat_to_irl(max_cat) as irl
,case when reversed then (upper(r)-1)::int else lower(r)::int end as s_ch
,case when reversed then lower(r)::int else (upper(r)-1)::int end as e_ch
,case when reversed then categorizing.get_line(sec,(upper(r)-1)::float,lower(r)::float) else categorizing.get_line(sec,lower(r)::float,(upper(r)-1)::float) end as geom
from d
;