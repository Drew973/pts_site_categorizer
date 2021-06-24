CREATE OR REPLACE FUNCTION process_sec(sect varchar) 
RETURNS void as $$		
	DECLARE
        BEGIN
			perform process_sec(sect,False);
			if not (select one_way from network where sec=sect) then
				perform process_sec(sect,True);
			end if;
		END;
$$ LANGUAGE plpgsql;