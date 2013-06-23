-- file: "list_same_vol_dups.sql"

select  
 -- a.vol_id  , a.file_id, a.file_name,     b.file_id, cast( b.file_name as varchar(80) ),  b.file_size 

    path_from_vol_id_file_id(a.vol_id ,  a.file_id ), path_from_vol_id_file_id(b.vol_id ,  b.file_id ), a.file_size

 
from files a, files b 
where a.vol_id = 'vol0025' 

    and b.vol_id != a.vol_id 
    and a.file_size = b.file_size 
    and a.file_name = b.file_name 
    --and a.file_id < b.file_id 
    --and a.file_size > 20000000 
    and a.file_size > 07500000 
    and a.folder_id != 0 and b.folder_id != 0
    
order by a.file_size desc ;
