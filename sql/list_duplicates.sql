
-- file: list_duplicates.sql

select 
        --a.vol_id, a.file_id, c.vol_name, 
        --b.vol_id, b.file_id, d.vol_name,
        path_from_vol_id_file_id(a.vol_id ,  a.file_id ),
        path_from_vol_id_file_id(b.vol_id ,  b.file_id ),
        --a.file_name, 
        a.file_size 
        --a.file_create_date, 
        --a.file_mod_date, 
        --a.file_uti 
from files a, files b, volumes c, volumes d -- volumes just for volume name
where 
    a.file_size = b.file_size 
    and a.file_size >= 20000000
    and a.file_name = b.file_name 
    --and a.vol_id != b.vol_id  -- only one side of each difference
    --and a.vol_id < b.vol_id  -- only one side of each difference
    and a.file_size > 5*1024*1024
    and a.folder_id != 0
    and b.folder_id != 0
    and a.vol_id = 'vol0004'
    and b.vol_id >= 'vol0032'
    and a.vol_id = c.vol_id
    and b.vol_id = d.vol_id
    order by file_size desc
