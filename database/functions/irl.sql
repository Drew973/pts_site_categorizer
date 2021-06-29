set search_path to categorizing,public;

--function to get irl given category ct and section label sect
CREATE OR REPLACE FUNCTION irl(ct text,sect text) RETURNS float AS
$$
SELECT irl from categories where cat=ct
$$
LANGUAGE sql IMMUTABLE;

alter function irl(ct text,sect text) set search_path to categorizing,public;