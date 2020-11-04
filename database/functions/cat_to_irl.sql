CREATE OR REPLACE FUNCTION cat_to_irl(category cat) --ch in cl1
RETURNS float AS $$
		declare
        BEGIN	
			if category>='S2' then 
				return 0.5;
			end if;

			if category>='G1' then 
				return 0.45;
			end if;

			if category='Q1' then 
				return 0.4;
			end if;
	
			if category<'Q1' then 
				return 0.35;
			end if;
			
			return Null;
			
			END;			
$$ LANGUAGE plpgsql;
