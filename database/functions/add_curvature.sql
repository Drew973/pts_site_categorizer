create or replace function add_curvature(sect text,s float,e float) 
	returns void as $$
	
	Declare
		one_way bool = one_way from network where sec=sect;
		
	BEGIN
		if one_way then
			insert into other_events(sec,reversed,s_ch,e_ch,category) values(sect,false,s,e,'S1');
		else
			insert into other_events(sec,reversed,s_ch,e_ch,category) values(sect,false,s,e,'S2');
			insert into other_events(sec,reversed,s_ch,e_ch,category) values(sect,True,e,s,'S2');
		end if;
	END;
	$$
	language plpgsql;

alter function add_curvature set search_path to categorizing