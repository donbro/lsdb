/* "create_trigger_before_insert_strings.sql" */


CREATE FUNCTION trigger_before_insert_strings() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

/* scheme for string ids is: "str000000" or  'str[0-9]{6}' */

--debugging output:
-- new.file_name := 'z' || new.string_id || 'K' || new.string_id is null || ((NEW.string_id NOT SIMILAR TO 'str[0-9]{6}'));

IF new.string_id is null or (NEW.string_id NOT SIMILAR TO 'str[0-9]{6}') then

        new.string_id := 
                concat( 'str' , 
                    right( concat( '0000000' , (1 + (select substring( coalesce( max(string_id), 'str000000' )  from 4 for 6) from strings )::integer)::text ) , 6)
                    )
        ;

end if;

new.string_ts := to_tsvector('english', new.string);

RETURN new; 

/*
  new.string_ts :=
     setweight(to_tsvector('pg_catalog.english', coalesce(new.title,'')), 'A') ||
     setweight(to_tsvector('pg_catalog.english', coalesce(new.body,'')), 'D');
*/

END;

--BEGIN
--    IF EXISTS (SELECT 1 FROM "myschema".mytable WHERE "MyKey" = NEW."MyKey") THEN
--        RETURN NULL;
--    ELSE
--        RETURN NEW;
--    END IF;
--END;

--CREATE RULE "my_table_on_duplicate_ignore" AS ON INSERT TO "my_table"
--  WHERE EXISTS(SELECT 1 FROM my_table 
--                WHERE (pk_col_1, pk_col_2)=(NEW.pk_col_1, NEW.pk_col_2))
--  DO INSTEAD NOTHING;

$$;


ALTER FUNCTION public.trigger_before_insert_strings() OWNER TO donb;


CREATE TRIGGER before_insert_strings BEFORE INSERT ON strings FOR EACH ROW EXECUTE PROCEDURE trigger_before_insert_strings();


