CREATE OR REPLACE FUNCTION max_cat(sect varchar,rev bool,rg int8range) 
RETURNS categorizing.cat as $$
		declare 	
			L float=meas_len from categorizing.network where sec=sect;
        BEGIN	
			return (select max(category) from categorizing.events where sec=sect and reversed=rev and rg&&r);
		END;
$$ LANGUAGE plpgsql;