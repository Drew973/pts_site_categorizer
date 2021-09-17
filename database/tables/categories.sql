set search_path to categorizing,public;



create table if not exists categories(
		cat text primary key
		,default_irl float
		,pos int--sort by irl,pos when processing
		,description text);	


DO
$do$
BEGIN
   IF (select count(cat) from categories)=0 THEN
		insert into categories(cat,default_irl,pos) values ('A',0.35,12);
		insert into categories(cat,default_irl,pos) values ('B',0.35,11);
		insert into categories(cat,default_irl,pos) values ('C',0.35,10);
		insert into categories(cat,default_irl,pos,description) values ('Q1',0.4,9,'minor junction');
		insert into categories(cat,default_irl,pos,description) values ('G1',0.45,8,'major gradient');
		insert into categories(cat,default_irl,pos,description) values ('S1',0.45,7,'major curvature');
		insert into categories(cat,default_irl,pos,description) values ('Q2',0.45,6,'major junction');
		insert into categories(cat,default_irl,pos,description) values ('Q3',0.45,5,'roundabout junction');
		insert into categories(cat,default_irl,pos,description) values ('R',0.45,4,'roundabout');
		insert into categories(cat,default_irl,pos,description) values ('G2',0.45,3,'minor gradient');
		insert into categories(cat,default_irl,pos,description) values ('S2',0.5,2,'minor curvature');
		insert into categories(cat,default_irl,pos,description) values ('K',0.5,1,'crossing');

   END IF;
END
$do$
;

CREATE OR REPLACE FUNCTION default_irl(category text) RETURNS float AS
$$ SELECT default_irl from categorizing.categories where cat=category $$
LANGUAGE sql IMMUTABLE;