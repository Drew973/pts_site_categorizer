CREATE OR REPLACE FUNCTION max_cat(sect varchar,rev bool,rg int8range) 
RETURNS categorizing.cat as $$
        BEGIN
		return max(category) from get_events(sect,rev) where rg&&int8range(least(s_ch,e_ch),greatest(s_ch,e_ch));
		END;
$$ LANGUAGE plpgsql;