set search_path to categorizing,public;

alter table curvatures add column if not exists ch numeric;
update curvatures set ch = distance::numeric;
create index on curvatures(sec);
create index on curvatures(ch);

select * from curvatures;




set search_path to categorizing,public;


create or replace function auto_curvatures(sect text,width numeric=10) 
	returns void as $$
	
	Declare
		rgs numrange[] = to_ranges(meas_len(sect)::numeric,width,'[]');
		threshold int=case when speed_limit>50 then 500 else 100 end from network where sec=sect ;
		
	BEGIN
		drop table if exists test;
		
		with a as (select sect,array_agg(ch) as chainages,array_agg(roc),avg(roc),unnest from unnest(rgs) 
			inner join curvatures on sec=sect and unnest@>ch
		group by unnest)
		
		create table test as select * from a;
		
--remove where <100m long and lowest roc>250
	END;
	$$
	language plpgsql;
	
select auto_curvatures('5010A679 1/00050')