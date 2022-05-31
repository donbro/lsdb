--DROP TABLE
--CREATE TABLE

drop table u12;

create table u12 ( mid uuid , tid timestamp with time zone, pid bigint, vid uuid, inode bigint, u6 bigint, u7 bigint, u8 bigint, u9 bigint, u10 bigint, u11 text, u12 text);

-- 36009918-F912-59E6-BD6D-9013DAFA2B77,2022-05-31T03:48:50.398032+00,852,3F9900B2-4FA3-4302-9CDB-72487A304246,1062930,160,1653968930,1653965929,1653965929,1653856762,directory,"/Users/donb/lsdb"

                --print MID,TID,PID,VID,$1,$2,$3,$4,$5,$6,$7,"\""SS"\"";

              --printf "VOLUME UUID,Inode Number,
                --         total size (bytes),last access (seconds),
                --         data mod (seconds),status change (seconds),
                --         creation (seconds),file type,file path
