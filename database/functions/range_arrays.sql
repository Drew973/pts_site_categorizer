CREATE OR REPLACE FUNCTION range_array_distinct(ranges int8range[]) 
RETURNS int8range[] as $$
										   
		declare
			res int8range[];
			overlapping int8range[];
			r int8range;
			new_range int8range;
										   
        BEGIN
			FOREACH r in  array ranges loop
				overlapping=array(select unnest from unnest(res) where unnest&&r);
				if cardinality(overlapping)=0 then
					res=res||r;
				else
					new_range=range_array_single_intersection(overlapping||r);
					--raise notice 'new range:%',new_range;
					res=range_array_remove(res,r);
					res=res||new_range;
										   
				end if;
			end loop;
			return res;
				
		END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION range_array_min(a int8range[]) returns int as 
	'select cast(min(lower(unnest)) as int) from unnest(a)' 
	LANGUAGE sql IMMUTABLE;

										   
CREATE OR REPLACE FUNCTION range_array_max(a int8range[]) returns int as 
	'select cast(max(upper(unnest)) as int) from unnest(a)' 
	LANGUAGE sql IMMUTABLE;
					   
										   
CREATE OR REPLACE FUNCTION range_array_remove(a int8range[],r int8range) returns int8range[] as 
	'select array(select unnest from unnest(a) where not r&&unnest)' 
	LANGUAGE sql IMMUTABLE;	
--select distinct_ranges
									

CREATE OR REPLACE FUNCTION range_array_single_intersection(ranges int8range[]) 
RETURNS int8range as $$										   
        BEGIN
			return int8range(range_array_min(ranges),range_array_max(ranges));
		END;
$$ LANGUAGE plpgsql;