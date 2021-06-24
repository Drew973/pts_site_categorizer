set search_path to categorizing,public;

--select * from get_events('A5230/48',False)



create or replace function process_sec(sect varchar,rev bool) 
	returns void	
	as $$
	DECLARE
		r record;

	BEGIN
			if rev then
				RETURN;

			else
				for r in select irl,ct,range_array_union(array_agg(int8range(s_ch,e_ch,'[]'))) from get_events('A5230/48',False) where s_ch!=e_ch group by irl,ct order by irl desc,ct loop
				
					insert into op(sec,reversed,category,irl,start_ch,end_ch,geom)--start_ch,end_ch,geom
					select sect,rev,r.ct,r.irl,lower(unnest),upper(unnest),get_line(sect,lower(unnest),upper(unnest)) 
					from unnest(range_array_difference(r.range_array_union
													   ,array(select int8range(start_ch::int,end_ch::int,'[]') from op where sec=sect and reversed=rev)));
					
				
				end loop;
				



			end if;
		
		
		END;
$$
	language plpgsql;
	
--select irl,ct,array_agg(int8range(s_ch,e_ch)) from get_events('A5230/48',False) where s_ch!=e_ch group by irl,ct order by irl desc,ct;


set search_path to categorizing,public;

create or replace function process_sec(sect varchar,rev bool) 
	returns void	
	as $$

	BEGIN
	
			delete from op where sec=sect and reversed=rev;
	
			if rev then
				with a as (select irl,ct,array_agg(int8range(e_ch,s_ch,'[]')) from get_events(sect,True) where s_ch!=e_ch group by irl,ct order by irl desc,ct)
				,b as (select irl,ct,array_agg from a)
				,c as (select irl,ct,unnest(range_array_difference(array_agg,(select array_cat_agg(array_agg) from a where a.irl>b.irl or (a.irl=b.irl and a.ct<b.ct)))) from b)
				insert into op(sec,reversed,category,irl,start_ch,end_ch,geom)
				select sect,rev,ct,irl,upper(unnest),lower(unnest),get_line(sect,upper(unnest),lower(unnest)) from c;

			else
			
			with a as (select irl,ct,array_agg(int8range(s_ch,e_ch,'[]')) from get_events(sect,False) where s_ch!=e_ch group by irl,ct order by irl desc,ct)
			,b as (select irl,ct,array_agg from a)
			,c as (select irl,ct,unnest(range_array_difference(array_agg,(select array_cat_agg(array_agg) from a where a.irl>b.irl or (a.irl=b.irl and a.ct<b.ct)))) from b)
			insert into op(sec,reversed,category,irl,start_ch,end_ch,geom)
			select sect,rev,ct,irl,lower(unnest),upper(unnest),get_line(sect,lower(unnest),upper(unnest)) from c;
		
			end if;
		
		
		END;
$$
	language plpgsql;

																								 
select process_sec(sec,False) from network;


select * from op



select process_sec('A5230/48',False);

select * from op where sec='A5230/48' order by start_ch