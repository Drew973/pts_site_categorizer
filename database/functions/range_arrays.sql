set search_path to categorizing,public;


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




--get union of rg and overlapping ranges
CREATE OR REPLACE FUNCTION range_union(rg int8range,ranges int8range[]) 
RETURNS int8range as $$									   
        BEGIN
			return int8range(least(lower(rg),(select min(lower(unnest)) from unnest(ranges) where unnest&&rg)),greatest(upper(rg),((select max(upper(unnest)) from unnest(ranges) where unnest&&rg))));				
		END;
$$ LANGUAGE plpgsql;



--merges ranges where overlapping. created discontinuous range will be as simple as possible with no overlaps. 

CREATE OR REPLACE FUNCTION range_array_union(ranges int8range[]) 
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




CREATE OR REPLACE FUNCTION range_array_union(ranges numrange[]) 
RETURNS numrange[] as $$
										   
		declare
			res numrange[];
			prev numrange;
			r numrange;
										   
        BEGIN
			if cardinality(ranges)<1 then 
				return null;
			end if;
			
			prev=ranges[1];
		
			FOREACH r in  array array(select unnest from unnest(ranges) order by lower(unnest)) loop--ordered by lower
				if prev&&r then
					prev=prev+r;
				else
					res=res||prev;
					prev=r;
				end if;

			end loop;
			res=res||prev;
			
		return res;
				
		END;
$$ LANGUAGE plpgsql;


--combine ranges into array of ranges
drop aggregate if exists range_array_agg(int8range);

CREATE AGGREGATE range_array_agg(int8range) 
(
  sfunc = array_append,
  stype = int8range[],
  finalfunc = range_array_union
);


drop aggregate if exists range_array_agg(numrange);

CREATE AGGREGATE range_array_agg(numrange) 
(
  sfunc = array_append,
  stype = numrange[],
  finalfunc = range_array_union
);


CREATE OR REPLACE FUNCTION range_array_intersection(a int8range[],b int8range) 
RETURNS int8range[] as								   
'
select array(select unnest*b from unnest(a) where unnest&&b)
'			
LANGUAGE sql IMMUTABLE;



--returns parts of a not overlapping b
CREATE OR REPLACE FUNCTION range_array_difference(a int8range,b int8range) 
RETURNS int8range[] as $$								   
        BEGIN
			if a&&b then	-- a and b overlap
				if lower(a)<lower(b) and upper(a)>upper(b) then 	--a contains b. @> buggy at boundry
					return array(select int8range(lower(a),lower(b)) union select int8range(upper(b),upper(a)));	---start of a to start of b,end of b to end of a
				else
					return array(select a-b);-- a-b does not work if a contains b. Will be 2 parts.
				end if;
					
			else			
				return array(select a);
			end if;
				
			
				
		END;
$$ LANGUAGE plpgsql;


--returns parts of a not overlapping b
CREATE OR REPLACE FUNCTION range_array_difference(a int8range,b int8range[]) 
RETURNS int8range[] as $$

DECLARE

res int8range[]=array(select unnest*a from unnest(gaps(b)) where unnest&&a);

BEGIN
	if is_null(b) then
		return a;
	end if;

	if lower(a)<lower(b) then
		res=res||int8range(lower(a),lower(b));
	end if;
	
	if upper(a)>upper(b) then
		res=res||int8range(upper(b),upper(a));
	end if;	
	
	return res;
END;
$$ LANGUAGE plpgsql;


--select range_array_difference(int8range(0,100),'{"[0,50)","[70,100)"}'::int8range[]);


CREATE OR REPLACE FUNCTION is_null(a anyarray) 
RETURNS bool as $$
BEGIN
	return (select count(unnest) from unnest(a) where not unnest is null)=0;
		END;
$$ LANGUAGE plpgsql;




--returns parts of a not overlapping b
CREATE OR REPLACE FUNCTION range_array_difference(a int8range[],b int8range) 
RETURNS int8range[] as $$								   
        BEGIN
			--return array_cat_agg(select case when b&&unnest then range_array_difference(unnest,b) else array(select unnest) end from unnest(a));--range_array_union? should give correct results without it.
			return array_cat_agg(range_array_difference) from (select range_array_difference(unnest,b) from unnest(a))s;
				
		END;
$$ LANGUAGE plpgsql;


--returns parts of a not overlapping b
CREATE OR REPLACE FUNCTION range_array_difference(a int8range[],b int8range[]) 
RETURNS int8range[] as $$

declare
	g int8range[]=gaps(a)||b;--gaps in results =gaps in a+gaps 
	res int8range[]=gaps(g); --gaps in gaps

BEGIN	

	if is_null(b) then
		return a;
	end if;

	if lower(a)<lower(g) then
		res=res||int8range(lower(a),lower(g));
	end if;
	
	if upper(a)>upper(g) then
		res=res||int8range(upper(g),upper(a));
	end if;	

	return range_array_intersection(res,int8range(lower(a),upper(a)));--{"[185,236)"}--
END;
	
$$ LANGUAGE plpgsql;



--creates ranges from minimum of r to maximum of r
CREATE OR REPLACE FUNCTION to_parts(r int8range[]) 
RETURNS int8range[] as								   
'
with a as (select unnest(r))
	,b as (select upper(unnest) from a union select lower(unnest) from a)
	,c as (select upper,lead(upper) over(order by upper) from b)
	select array(select int8range(upper,lead) from c where upper!=lead);
'			
LANGUAGE sql IMMUTABLE;




--True if a overlaps and element of b
CREATE OR REPLACE FUNCTION overlap(a int8range,b int8range[]) 
RETURNS bool as $$								   
        BEGIN
			return count(unnest)>0 from unnest(b) where unnest && a;
		END;
$$ LANGUAGE plpgsql;


--select overlap(int8range(0,100),'{"[1000,5000)","[700,1000)"}'::int8range[])



CREATE OR REPLACE FUNCTION lower(rgs int8range[]) 
RETURNS int as $$
BEGIN
	return min(lower(unnest)) from unnest(rgs);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION lower(rgs numrange[]) 
RETURNS int as $$
BEGIN
	return min(lower(unnest)) from unnest(rgs);
END;
$$ LANGUAGE plpgsql;





CREATE OR REPLACE FUNCTION upper(rgs int8range[]) 
RETURNS int as $$
BEGIN
	return max(upper(unnest)) from unnest(rgs);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION upper(rgs numrange[]) 
RETURNS numeric as $$
BEGIN
	return max(upper(unnest)) from unnest(rgs);
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION range_array_contains(a numrange[],b numeric) returns bool as 
	'select True in(select unnest@>b from unnest(a))' 
	LANGUAGE sql IMMUTABLE;



CREATE OR REPLACE FUNCTION is_null(a anyarray) 
RETURNS bool as $$
BEGIN
	return (select count(unnest) from unnest(a))=0;
		END;
$$ LANGUAGE plpgsql;



--returns gaps in rgs (from lower to upper)
CREATE OR REPLACE FUNCTION gaps(rgs int8range[]) 
RETURNS int8range[] as $$

BEGIN
	
	return array(select int8range(upper(unnest),lower(lead)) from
	(select unnest,lead(unnest) over (order by lower(unnest)) from unnest(range_array_union(rgs))
	)d
	where lead!=unnest);
	
		END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION gaps(rgs numrange []) 
RETURNS numrange [] as $$								   		  
        BEGIN
			return array(select numrange(upper(unnest),lower(lead)) from (select unnest,lead(unnest) over (order by lower(unnest)) from unnest(rgs))b where not unnest&&lead);
		END;
$$ LANGUAGE plpgsql;




--select gaps('{"[0,230)","[169,230)","[231,300)"}'::int8range[])


CREATE OR REPLACE FUNCTION has_gaps(a numrange[]) returns bool as 
$$
	select is_null(gaps(a)) 
$$	
LANGUAGE sql IMMUTABLE;


