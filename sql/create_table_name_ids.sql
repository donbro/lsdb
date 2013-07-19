-- Table: name_ids

/*
DROP VIEW names;
DROP TABLE name_ids;
CREATE TABLE name_ids
ALTER TABLE
CREATE TRIGGER
CREATE VIEW
ALTER TABLE
*/

DROP VIEW names;

DROP TABLE name_ids;

CREATE TABLE name_ids
(
  name_str_id       character varying(10) NOT NULL,
  supername_str_id  character varying(10),
  name_id           character varying(8) NOT NULL,
  CONSTRAINT names_pkey1 PRIMARY KEY (name_id)
)
WITH (
  OIDS=FALSE
);

-- name_seq_no smallint,

-- NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "names_pkey1" for table "name_ids"


ALTER TABLE name_ids
  OWNER TO donb;


CREATE OR REPLACE FUNCTION create_function_name_id()
RETURNS trigger AS
$BODY$
BEGIN
-- scheme for id is "n000000" or  'n[0-9]{6}'
IF new.name_id is null or (NEW.name_id NOT SIMILAR TO 'n[0-9]{6}') then
        new.name_id := 
                concat( 'n' , 
                    right( concat( '0000000' , (1 + (select substring( coalesce( max(name_id), 'n000000' )  from 2 for 6) from name_ids )::integer)::text ) , 6)
                    )
        ;
end if;

RETURN new; 
END;
$BODY$
LANGUAGE 'plpgsql' VOLATILE;

CREATE TRIGGER before_insert_name_ids -- names_insert_before
  BEFORE INSERT
  ON name_ids
  FOR EACH ROW
  EXECUTE PROCEDURE create_function_name_id();


-- View: names

CREATE OR REPLACE VIEW names AS 
 SELECT s1.string AS name, s2.string AS super_name, 
    name_ids.name_id
   FROM strings s1
   JOIN name_ids ON s1.str_id::text = name_ids.name_str_id::text
   JOIN strings s2 ON name_ids.supername_str_id::text = s2.str_id::text;

ALTER TABLE names
  OWNER TO donb;
