CREATE OR REPLACE FUNCTION process_sec(sect varchar) 
RETURNS void as $$		
	DECLARE
        BEGIN
			delete from categorizing.op where sec=sect;

			with a as (select reversed,unnest(array_distinct(0||array_agg(s_ch)||array_agg(e_ch)||meas_len(sect)::int)) as ch from get_events(sect) group by reversed)
			,b as (select *,lead(ch) over (partition by reversed order by ch) from a)
			,c as (select *,max_cat(sect,reversed,int8range(ch,lead)),int8range(ch,lead,'[]') as rg from b where ch!=lead and not lead is null)--have sec,reversed,ch,lead,max_cat. want to merge where same as ajacent cats
			,op_view_like as (select reversed,max_cat,unnest(range_array_distinct(array_agg(rg))) as r from c group by reversed,max_cat)

			insert into categorizing.op(sec,reversed,start_ch,end_ch,category,irl,geom)
			select sect
			,reversed
			,case when reversed then (upper(r)-1)::int else lower(r)::int end as s_ch
			,case when reversed then lower(r)::int else (upper(r)-1)::int end as e_ch
			,max_cat as category
			,cat_to_irl(max_cat) as irl																		  
			,case when reversed then categorizing.get_line(sect,(upper(r)-1)::float,lower(r)::float) else categorizing.get_line(sect,lower(r)::float,(upper(r)-1)::float) end as geom
			from op_view_like;	
							
		END;
$$ LANGUAGE plpgsql;