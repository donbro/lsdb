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
                new.vol_id := 
                        
                        -- (select substring( coalesce( max(vol_id), 'vol0000' )  from 4 for 4) from files ) -- '0030', '0000' if null
                        --to_number( (select substring( coalesce( max(vol_id), 'vol0000' )  from 4 for 4) from files ), '9999' )

                        concat( 'vol' , 
                            right( concat( '0000' , (1 + (select substring( coalesce( max(vol_id), 'vol0000' )  from 4 for 4) from files )::integer)::text ) , 4)
                            )

                --NEW.vol_id := (select concat( 'vol' ,  substr( concat( '0000' , 1 + 
                    -- ifnull( (select max(substr(vol_id,-4)) from files) , 0) 

                    -- ERROR:  operator does not exist: integer + text

                    --(select substring(max(vol_id) from 4 for 4) from files )
                    -- substring(string [from int] [for int])

                    -- coalesce( to_number( (select max(substr(vol_id,-4)) from files ), "vol9999") , 0) 

                    --ERROR:  invalid input syntax for integer: "vol0030"
                    --SELECT coalesce(field, 'Empty') AS field_alias

                --) , -4 ) ) ) ;
                ;
    end if;

end if;

RETURN new; 

END;
$BODY$
LANGUAGE 'plpgsql' VOLATILE;


