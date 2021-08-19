
set search_path to categorizing,public;

drop table if exists other_events;

create table if not exists other_events(
sec varchar references network(sec) on delete cascade on update cascade
,reversed bool
,s_ch int
,e_ch int
,category text references categories(cat) on update cascade
,pk serial primary key
,geom geometry('linestring',27700)
);

create index on other_events(sec,reversed);



--triggers to update geometry when s_ch or e_ch changed

set search_path to categorizing,public;

CREATE OR REPLACE FUNCTION other_events_geom()
  RETURNS TRIGGER 
  LANGUAGE PLPGSQL
  AS $$
BEGIN
	NEW.geom=get_line(NEW.sec,NEW.s_ch,new.e_ch);
	RETURN NEW;
END;
$$;


alter function other_events_geom set search_path to categorizing,public;

drop trigger if exists other_events_update on other_events;
create trigger other_events_update before update on other_events FOR EACH ROW execute procedure other_events_geom();
create trigger other_events_insert before insert on other_events FOR EACH ROW execute procedure other_events_geom();

