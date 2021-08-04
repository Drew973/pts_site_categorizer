CREATE OR REPLACE FUNCTION meas_len(sect varchar) RETURNS float AS
'SELECT cast(meas_len as float) from categorizing.network where sec=sect' LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION road(sect varchar) RETURNS varchar AS
'SELECT road from categorizing.network where sec=sect' LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION is_rbt(sect varchar) RETURNS bool AS
'SELECT rbt from categorizing.network where sec=sect' LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION near_rbt(pt geometry('point'),dist float=5) RETURNS bool AS
'SELECT 0<count(sec) from categorizing.network  where rbt and st_dwithin(pt,geom,dist)' LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION invert_ch(ch float,sect varchar) RETURNS float AS
'SELECT meas_len-ch from categorizing.network  where sec=sect' LANGUAGE sql IMMUTABLE;
					   

CREATE OR REPLACE FUNCTION ch_to_point(sect varchar,chainage float) 
RETURNS geometry('point',27700) AS $$
		declare 	
			f float = chainage/meas_len from network where sec=sect;
			geom geometry('linestring',27700) = geom from network where sec=sect;
        BEGIN	
			return ST_LineInterpolatePoint(geom,clamp(f,0,1));
		END;			
$$ LANGUAGE plpgsql;


alter function ch_to_point set search_path to categorizing,public;

CREATE OR REPLACE FUNCTION ch_to_sec_len(sect varchar,chainage float) 
RETURNS float as $$
		declare 	
			L float=meas_len from categorizing.network where sec=sect;
        BEGIN	
			if chainage>L  then 
				return L;
			end if;
			
			if chainage<0 then
				return 0;
			end if;
			
			return chainage;
		END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION ch_to_sec_len(sect varchar,chainage int) 
RETURNS int as $$
		declare 	
			L float=meas_len from categorizing.network where sec=sect;
        BEGIN	
			if chainage>L  then 
				return L;
			end if;
			
			if chainage<0 then
				return 0;
			end if;
			
			return chainage;
		END;			
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION meas_sec_ch(sect varchar,pt geometry('point'),rev bool=False) 
RETURNS float AS $$
	declare 
		geom geometry=geom from categorizing.network  where sec=sect;
		ml float=meas_len from categorizing.network  where sec=sect;
	BEGIN
		if rev then
			return ml*(1-st_linelocatepoint(geom,pt));
		 else
		 	return ml*st_linelocatepoint(geom,pt);
		end if;
	END;			
$$ LANGUAGE plpgsql;										
																
CREATE OR REPLACE FUNCTION  floor_meas_len(sect varchar) 
RETURNS int AS $$
	declare f int=10*floor(meas_len/10) from categorizing.network  where sec=sect;
        BEGIN	
			if f<meas_len from categorizing.network  where sec=sect then
				return f;
			else 
				return f-10;
			end if;
		END;			
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION invert_ch(ch float,sect varchar) 
RETURNS float AS $$
        BEGIN	
			return meas_len-ch from categorizing.network  where sec=sect;
		END;			
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION int_meas_len(sect varchar) 
RETURNS int AS $$
        BEGIN	
			return meas_len from categorizing.network  where sec=sect;
		END;			
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calc_to_meas(calc float,sect varchar) 
RETURNS float AS $$
        BEGIN	
			return calc*(select meas_len from categorizing.network  where sec=sect)/(select calc_len from categorizing.network  where sec=sect);
		END;			
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calc_to_meas(calc int,sect varchar) 
RETURNS float AS $$
        BEGIN	
			return calc*(select meas_len from categorizing.network  where sec=sect)/(select calc_len from categorizing.network  where sec=sect);
		END;			
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION road_class(sect varchar) 
RETURNS varchar AS $$
	declare
		c varchar=upper(left(sect,1));
    BEGIN	
		if c='A' or c='B'or c='C' then
			return c;
		else
			return 'U';
		end if;
		END;			
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xsp_reversed(x varchar) 
RETURNS bool AS $$
        BEGIN	
			return x like('CR');
		END;			
$$ LANGUAGE plpgsql;


--part of linestring  from start_ch to end_ch. len=noninal length. chainages in terms of nominal length

CREATE OR REPLACE FUNCTION make_line(L geometry('linestring'),len float,start_ch float,end_ch float) 
RETURNS geometry('linestring') AS $$
		declare
			f1 float;
			f2 float;
			r geometry;
        BEGIN	
				f1=start_ch/len;
				f2=end_ch/len;
				
				if f1<0 then
					f1=0;
				end if;
				
				if f1>1 then
					f1=1;
				end if; 

				if f2>1 then
					f2=1;
				end if; 

				if f2<0 then
					f2=0;
				end if; 
				
				if f2=f1 then
					raise notice 'f2=f1';
					return null;
				end if;

				if f2>f1 then
					r= ST_LineSubstring(L,f1,f2);
				else
					r= st_reverse(ST_LineSubstring(L,f2,f1));
				end if;
						
				if st_geometryType(r)!='ST_LineString' then
					raise warning 'make_line(%,%,%,%) returned %',st_asText(L),len,start_ch,end_ch,st_geometryType(r);
				end if;
										   
				return r;							   
												   
		END;			
$$ LANGUAGE plpgsql;
													   

--returns linestring from start_ch to end_ch of section, start_ch and end_ch in terms of meas_len.
													   					
CREATE OR REPLACE FUNCTION get_line(sect varchar,start_ch float,end_ch float) 
RETURNS geometry('linestring',27700) AS $$
		declare g geometry=geom from categorizing.network  where sec=sect;
		len float=meas_len(sect);
        BEGIN	
			if start_ch=end_ch then
				--raise warning 'get line(%,%,%) start_ch=end_ch',sect,start_ch,end_ch;
				return null;
			end if;
		
			if start_ch>len then
				raise warning 'get line(%,%,%) start_ch>section length %',sect,start_ch,end_ch,len;
			end if;


			if end_ch>len then
				--raise warning 'get line(%,%,%) end chainage>section length %',sect,start_ch,end_ch,len;
			end if;

			if st_geometrytype(make_line(g,len,start_ch,end_ch))!='ST_LineString' then
				--raise warning 'get line(%,%,%) returned wrong type',sect,start_ch,end_ch;
				--raise warning 'make_line(%,%,%,%) returned wrong type',st_asText(g),len,start_ch,end_ch;
				return null;
			end if;
		
		
		return make_line(g,len,start_ch,end_ch);
		END;			
$$ LANGUAGE plpgsql;	