set search_path to categorizing,public;

create or replace function process(sect varchar) 
	returns void	
	as $$

	BEGIN
	
		delete from op where sec=sect;
	
	
		with a as (select ct,(select pos from categories where cat=ct),array_agg(int8range(s_ch,e_ch,'[]')) as rgs from get_events_f(sect) where s_ch!=e_ch group by ct)
		,b as(select ct,range_array_difference(rgs,array((select unnest(rgs) from a as a2 where a2.pos<a.pos))) as rgs from a)
		,c as (select ct,unnest(rgs),(select irl from categories where cat=ct) from b)
			 insert into op (sec,reversed,start_ch,end_ch,category,irl,geom)
			 select sect,False,lower(unnest),upper(unnest),ct,irl,get_line(sect,lower(unnest),upper(unnest)) from c;


		if not (select one_way from network where sec=sect)	then

			with a as (select ct,(select pos from categories where cat=ct),array_agg(int8range(e_ch,s_ch,'[]')) as rgs from get_events_r(sect) where s_ch!=e_ch group by ct)
			,b as(select ct,range_array_difference(rgs,array((select unnest(rgs) from a as a2 where a2.pos<a.pos))) as rgs from a)
			,c as (select ct,unnest(rgs),(select irl from categories where cat=ct) from b)
				 insert into op (sec,reversed,start_ch,end_ch,category,irl,geom)
				 select sect,True,upper(unnest),lower(unnest),ct,irl,get_line(sect,upper(unnest),lower(unnest)) from c;																								 

		end if;																						 
	
	END;
$$
	language plpgsql;

