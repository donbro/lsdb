CREATE OR REPLACE FUNCTION update_vol_id()
RETURNS trigger AS
$BODY$
BEGIN

IF new.vol_id is null or (NEW.vol_id NOT LIKE 'vol[0-9][0-9][0-9][0-9]') then

    -- update new 
    NEW.vol_id := (select distinct vol_id from files where files.file_create_date = new.file_create_date and files.file_name = new.file_name and files.folder_id = 1 ); 
    --RAISE NOTICE 'vol_id is % ', new.vol_id;

    IF NEW.vol_id is null then
                --update new
                NEW.vol_id := (select concat( 'vol' ,  substr( concat( '0000' , 1 + 
                    -- ifnull( (select max(substr(vol_id,-4)) from files) , 0) 

                    -- ERROR:  operator does not exist: integer + text

                    (select max(substr(vol_id,-4)) from files )

                    -- coalesce( to_number( (select max(substr(vol_id,-4)) from files ), "vol9999") , 0) 

                    --ERROR:  invalid input syntax for integer: "vol0030"
                    --SELECT coalesce(field, 'Empty') AS field_alias

                ) , -4 ) ) ) ;
    end if;

end if;

RETURN new; 

END;
$BODY$
LANGUAGE 'plpgsql' VOLATILE;


