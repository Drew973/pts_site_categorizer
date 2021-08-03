set search_path to categorizing,public;

CREATE OR REPLACE FUNCTION jc_update_point()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS $$
BEGIN
	NEW.geom=ch_to_point(NEW.sec,NEW.ch);
	RETURN NEW;
END;
$$;


alter function jc_update_point set search_path to categorizing,public;

drop trigger if exists jc_update on jc;
create trigger jc_update before update of ch on jc FOR EACH ROW execute procedure jc_update_point();

