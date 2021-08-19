set search_path to categorizing,public;



create table if not exists categories(
		cat text primary key
		,irl float
		,pos int unique not null--order
		,bidirectional bool
		,description text);	


DO
$do$
BEGIN
   IF (select count(cat) from categories)=0 THEN
		insert into categories(cat,irl,pos) values ('A',0.35,12);
		insert into categories(cat,irl,pos) values ('B',0.35,11);
		insert into categories(cat,irl,pos) values ('C',0.35,10);
		insert into categories(cat,irl,pos,description) values ('Q1',0.4,9,'minor junction');
		insert into categories(cat,irl,pos,description) values ('G1',0.45,8,'major gradient');
		insert into categories(cat,irl,pos,description) values ('S1',0.45,7,'major curvature');
		insert into categories(cat,irl,pos,description) values ('Q2',0.45,6,'major junction');
		insert into categories(cat,irl,pos,description) values ('Q3',0.45,5,'roundabout junction');
		insert into categories(cat,irl,pos,description) values ('R',0.45,4,'roundabout');
		insert into categories(cat,irl,pos,description) values ('G2',0.45,3,'minor gradient');
		insert into categories(cat,irl,pos,description) values ('S2',0.5,2,'minor curvature');
		insert into categories(cat,irl,pos,description) values ('K',0.5,1,'crossing');

   END IF;
END
$do$


update categories set bidirectional = case when cat in('Q1','Q2','Q3','K') then true else false end;
