CREATE OR REPLACE FUNCTION process_sec(sect varchar) 
RETURNS void as $$									   
        BEGIN
			delete from op where sec=sect;
			insert into categorizing.op(sec,reversed,start_ch,end_ch,category,irl,geom)
			select sec,reversed,s_ch,e_ch,category,irl,geom from op_view where sec=sect;
				
		END;
$$ LANGUAGE plpgsql;