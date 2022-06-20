select max(u6/(1000*1000)) "size", count(*), min(pathname), max(pathname), min(inode), max(inode) from u12 where u6 > 1000 group by u6 having max(pathname) <> min(pathname) order by u6 desc  limit 20;