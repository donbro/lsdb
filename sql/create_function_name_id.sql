/* file: /users/donb/projects/names/sql/create_function_name_id.sql */

CREATE OR REPLACE FUNCTION create_function_name_id()
RETURNS trigger AS
$BODY$
BEGIN

-- scheme for id is "n000000" or  'n[0-9]{6}'

--debugging output:
-- new.file_name := 'z' || new.name_id || 'K' || new.name_id is null || ((NEW.name_id NOT SIMILAR TO 'n[0-9]{6}'));

IF new.name_id is null or (NEW.name_id NOT SIMILAR TO 'n[0-9]{6}') then

        new.name_id := 
                concat( 'n' , 
                    right( concat( '0000000' , (1 + (select substring( coalesce( max(name_id), 'n000000' )  from 2 for 6) from names )::integer)::text ) , 6)
                    )
        ;

end if;

RETURN new; 

END;
$BODY$
LANGUAGE 'plpgsql' VOLATILE;


