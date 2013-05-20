
-- file: list_duplicates.sql

select 
        a.vol_id, c.volume_name, b.vol_id, d.volume_name,
       -- a.folder_id, 
        a.file_name, 
       -- a.file_id, 
        a.file_size, 
        a.file_create_date, 
        a.file_mod_date, 
        a.file_uti 
from files a, files b, volumes c,volumes d
where 
    a.file_size = b.file_size 
    and a.file_name = b.file_name 
    and ( a.vol_id > b.vol_id  )  -- only one side of each difference
    and a.file_size > 5*1024*1024
    and a.folder_id != 0
    and b.folder_id != 0
    and a.vol_id = 'vol0027'
    and a.vol_id = c.vol_id
    and b.vol_id = d.vol_id
    order by file_size desc
