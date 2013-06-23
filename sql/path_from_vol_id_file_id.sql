
-- file: "path_from_vol_id_file_id.sql"

drop function path_from_vol_id_file_id(vol_id varchar(8), file_id bigint);

CREATE FUNCTION path_from_vol_id_file_id(vol_id varchar(8), file_id bigint) RETURNS VARCHAR AS $$

        SELECT '/Volumes/' || path FROM
        (

            WITH RECURSIVE pathto(path, vol_id, id) AS (
                SELECT CAST (file_name AS text), vol_id, folder_id 
                    FROM files 
                    WHERE vol_id = $1 and file_id = $2
                UNION
                SELECT files.file_name || '/' || pathto.path, files.vol_id, folder_id
                    FROM files, pathto 
                    WHERE files.vol_id = pathto.vol_id and files.file_id = pathto.id
            )

            SELECT * FROM pathto

        ) AS pathto(path, vol_id, id)

        WHERE id = 1
        ;

        $$ 
        LANGUAGE 'sql';
