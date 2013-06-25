/* "create_trigger_before_insert_strings.sql" */


CREATE or replace FUNCTION trigger_before_insert_strings() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

/* scheme for string ids is: "str000000" or  'str[0-9]{6}' */

--debugging output:
-- new.file_name := 'z' || new.str_id || 'K' || new.str_id is null || ((NEW.str_id NOT SIMILAR TO 'str[0-9]{6}'));

IF new.str_id is null or (NEW.str_id NOT SIMILAR TO 'str[0-9]{6}') then

        new.str_id := 
                concat( 'str' , 
                    right( concat( '0000000' , (1 + (select substring( coalesce( max(str_id), 'str000000' )  from 4 for 6) from strings )::integer)::text ) , 6)
                    )
        ;

end if;

new.str_ts := to_tsvector('english', new.string);

RETURN new; 

/*
  new.str_ts :=
     setweight(to_tsvector('pg_catalog.english', coalesce(new.title,'')), 'A') ||
     setweight(to_tsvector('pg_catalog.english', coalesce(new.body,'')), 'D');
*/

END;

$$;


ALTER FUNCTION public.trigger_before_insert_strings() OWNER TO donb;


drop trigger before_insert_strings on strings;

CREATE TRIGGER before_insert_strings BEFORE INSERT ON strings FOR EACH ROW EXECUTE PROCEDURE trigger_before_insert_strings();


