create or replace function get_events(sect varchar,rev bool) 
	returns table (s_ch int,e_ch int,category categorizing.cat) 
	
	as $$
	BEGIN
		if rev then
			RETURN QUERY select start_chain,end_chain,event_category from
				(select ch_to_sec_len(sect,ch+50) as start_chain,ch_to_sec_len(sect,ch) as end_chain,categorizing.jc.category as event_category from categorizing.jc where sec=sect
				union
				select meas_len(sect)::int,0,(select road_class from network where sec=sect)
				)f;
			
		else 
			
			RETURN QUERY SELECT start_chain,end_chain,event_category from
			(select ch_to_sec_len(sect,ch-50) as start_chain,ch_to_sec_len(sect,ch) as end_chain,categorizing.jc.category as event_category from categorizing.jc where sec=sect
			union
			select 0,meas_len(sect)::int,(select road_class from network where sec=sect)
			union select ch_to_sec_len(sect,other_events.s_ch),ch_to_sec_len(sect,other_events.e_ch),other_events.category from other_events where sec=sect and other_events.reversed=rev
			)r;
			
		end if;

		END;
	$$
	language plpgsql;


create or replace function get_events(sect varchar) 
	returns table (reversed bool,s_ch int,e_ch int,category categorizing.cat) 
	
	as $$
	BEGIN
	
		if (select one_way from network where sec=sect) then
			RETURN QUERY select False,* from get_events(sect,False);
						
		else
			RETURN QUERY
				select * from
				(
				select False,* from get_events(sect,False)
				union
				select True,* from get_events(sect,True)
				)b;
				
		end if;

		END;
	$$
	language plpgsql;



create or replace function get_events_r(sect varchar) 
	returns table (s_ch int,e_ch int,ct text) 
	as $$
	select start_chain,end_chain,event_category from
			(select ch_to_sec_len(sect,ch+50) as start_chain,ch_to_sec_len(sect,ch) as end_chain,categorizing.jc.category as event_category from categorizing.jc where sec=sect
			union
			select meas_len(sect)::int,0,(select road_class::text from network where sec=sect)
			 union select ch_to_sec_len(sect,other_events.s_ch),ch_to_sec_len(sect,other_events.e_ch),other_events.category::text from other_events where sec=sect and other_events.reversed

			)f;
	$$
	language sql IMMUTABLE;


create or replace function get_events_f(sect varchar) 
	returns table (s_ch int,e_ch int,ct text) 
	as $$
	SELECT start_chain,end_chain,event_category from
			(select ch_to_sec_len(sect,ch-50) as start_chain,ch_to_sec_len(sect,ch) as end_chain,categorizing.jc.category as event_category from categorizing.jc where sec=sect
			union
			select 0,meas_len(sect)::int,(select road_class::text from network where sec=sect)
			union select ch_to_sec_len(sect,other_events.s_ch),ch_to_sec_len(sect,other_events.e_ch),other_events.category::text from other_events where sec=sect and not other_events.reversed
			)r;
	$$
	language sql IMMUTABLE;