CREATE OR REPLACE FUNCTION update_vol_id()
RETURNS trigger AS
$BODY$
BEGIN

--debugging output:
-- new.file_name := 'z' || new.vol_id || 'K' || new.vol_id is null || ((NEW.vol_id NOT SIMILAR TO 'vol[0-9]{4}'));

IF new.vol_id is null or (NEW.vol_id NOT SIMILAR TO 'vol[0-9]{4}') then

    NEW.vol_id := (select distinct vol_id from files where files.file_create_date = new.file_create_date and files.file_name = new.file_name and files.folder_id = 1 ); 

    IF NEW.vol_id is null then
                new.vol_id := 
                        concat( 'vol' , 
                            right( concat( '0000' , (1 + (select substring( coalesce( max(vol_id), 'vol0000' )  from 4 for 4) from files )::integer)::text ) , 4)
                            )
                ;
    end if;

end if;

RETURN new; 

END;
$BODY$
LANGUAGE 'plpgsql' VOLATILE;


