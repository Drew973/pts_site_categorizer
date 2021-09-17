set search_path to categorizing,public;

create table if not exists events(
sec varchar references network(sec) on delete cascade on update cascade
,s_ch int
,e_ch int
,category text references categories(cat) on update cascade
,irl float
,pk serial primary key
,geom geometry('linestring',27700)
);

create index on events(sec);

--triggers to fix geometry when s_ch or e_ch updated or row inserted
CREATE OR REPLACE FUNCTION events_geom()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS $$
BEGIN
	NEW.geom = categorizing.get_line(NEW.sec,NEW.s_ch::numeric,new.e_ch::numeric);
	NEW.irl = coalesce(NEW.irl,categorizing.default_irl(NEW.category));
	RETURN NEW;
END;
$$;

alter function events_geom set search_path to categorizing,public;

drop trigger if exists events_update on events;
create trigger events_update before update on events FOR EACH ROW execute procedure events_geom();
create trigger events_insert before insert on events FOR EACH ROW execute procedure events_geom();