-- file: "list_same_vol_dups.sql"

select  
  a.vol_id, a.file_id, a.file_name, a.file_size
 
 
from files a
where a.vol_id = 'vol0004' 
    --and a.file_size = b.file_size and a.file_name != b.file_name 
    --and a.file_id < b.file_id 
    and a.file_size > 10000000 
    and a.folder_id != 0 --and b.folder_id != 0
    
order by a.file_size desc ;
group by a.file_size
having count(*) > 1
