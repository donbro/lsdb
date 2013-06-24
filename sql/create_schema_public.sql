/*
 Navicat Premium Data Transfer

 Source Server         : localhost 5432
 Source Server Type    : PostgreSQL
 Source Server Version : 90202
 Source Host           : localhost
 Source Database       : files
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90202
 File Encoding         : utf-8

 Date: 06/23/2013 08:23:26 AM
*/

-- ----------------------------
--  Table structure for "volume_uuids"
-- ----------------------------
DROP TABLE IF EXISTS "volume_uuids";
CREATE TABLE "volume_uuids" (
	"vol_id" varchar(8) NOT NULL,
	"vol_uuid" char(36) NOT NULL,
	"vol_total_capacity" int8 NOT NULL,
	"vol_available_capacity" int8 NOT NULL
)
WITH (OIDS=FALSE);
ALTER TABLE "volume_uuids" OWNER TO "donb";

-- ----------------------------
--  Table structure for "files"
-- ----------------------------
DROP TABLE IF EXISTS "files";
CREATE TABLE "files" (
	"vol_id" varchar(8) NOT NULL,
	"folder_id" int8 NOT NULL,
	"file_name" varchar(255) NOT NULL,
	"file_id" int8 NOT NULL,
	"file_size" int8 NOT NULL,
	"file_create_date" timestamp(6) NOT NULL,
	"file_mod_date" timestamp(6) NOT NULL,
	"file_uti" varchar(128)
)
WITH (OIDS=FALSE);
ALTER TABLE "files" OWNER TO "donb";

-- ----------------------------
--  Table structure for "RKVolume"
-- ----------------------------
DROP TABLE IF EXISTS "RKVolume";
CREATE TABLE "RKVolume" (
	"modelId" int4 NOT NULL,
	"uuid" text,
	"name" text,
	"diskUuid" text,
	"label" text,
	"isOffline" int4,
	"createDate" bytea,
	"modDate" bytea
)
WITH (OIDS=FALSE);
ALTER TABLE "RKVolume" OWNER TO "donb";

-- ----------------------------
--  Table structure for "RKMaster"
-- ----------------------------
DROP TABLE IF EXISTS "RKMaster";
CREATE TABLE "RKMaster" (
	"modelId" int4 NOT NULL,
	"uuid" text,
	"name" text,
	"projectUuid" text,
	"importGroupUuid" text,
	"fileVolumeUuid" text,
	"alternateMasterUuid" text,
	"originalVersionUuid" text,
	"originalVersionName" text,
	"fileName" text,
	"type" text,
	"subtype" text,
	"fileIsReference" int4,
	"isExternallyEditable" int4,
	"isTrulyRaw" int4,
	"isMissing" int4,
	"hasAttachments" int4,
	"hasNotes" int4,
	"hasFocusPoints" int4,
	"imagePath" text,
	"fileSize" int4,
	"pixelFormat" int4,
	"duration" bytea,
	"imageDate" bytea,
	"fileCreationDate" bytea,
	"fileModificationDate" bytea,
	"imageHash" text,
	"originalFileName" text,
	"originalFileSize" int4,
	"imageFormat" int4,
	"createDate" bytea,
	"isInTrash" int4,
	"faceDetectionState" int4,
	"colorSpaceName" text,
	"colorSpaceDefinition" bytea,
	"fileAliasData" bytea,
	"importedBy" int4
)
WITH (OIDS=FALSE);
ALTER TABLE "RKMaster" OWNER TO "donb";

-- ----------------------------
--  Table structure for "strings"
-- ----------------------------
DROP TABLE IF EXISTS "strings";
CREATE TABLE "strings" (
	"str_id" varchar(10) NOT NULL,
	"string" varchar(256) NOT NULL,
	"str_ts" tsvector
)
WITH (OIDS=FALSE);
ALTER TABLE "strings" OWNER TO "donb";

-- ----------------------------
--  Table structure for "names_ids"
-- ----------------------------
DROP TABLE IF EXISTS "names_ids";
CREATE TABLE "names_ids" (
	"string_id" varchar(10) NOT NULL,
	"super_name_id" varchar(10),
	"name_seq_no" int2,
	"name_id" varchar(8) NOT NULL
)
WITH (OIDS=FALSE);
ALTER TABLE "names_ids" OWNER TO "donb";

-- ----------------------------
--  View structure for "volumes_mod_date"
-- ----------------------------
DROP VIEW IF EXISTS "volumes_mod_date";
CREATE VIEW "volumes_mod_date" AS SELECT files.vol_id, files.file_name AS volume_name, files.file_mod_date FROM files WHERE ((files.folder_id = 1) AND (files.file_mod_date = (SELECT max(b.file_mod_date) AS max FROM files b WHERE ((b.folder_id = 1) AND ((b.vol_id)::text = (files.vol_id)::text)))));

-- ----------------------------
--  View structure for "files_not_latest"
-- ----------------------------
DROP VIEW IF EXISTS "files_not_latest";
CREATE VIEW "files_not_latest" AS SELECT files.vol_id, files.folder_id, files.file_name, files.file_id, files.file_size, files.file_create_date, files.file_mod_date, files.file_uti FROM files WHERE ((((files.vol_id)::text = 'vol0003'::text) AND (files.file_id = 2)) AND (files.file_mod_date <> (SELECT max(files.file_mod_date) AS max FROM files WHERE (((files.vol_id)::text = 'vol0003'::text) AND (files.file_id = 2)))));

-- ----------------------------
--  View structure for "volumes"
-- ----------------------------
DROP VIEW IF EXISTS "volumes";
CREATE VIEW "volumes" AS SELECT DISTINCT files.vol_id, files.folder_id, files.file_name AS vol_name, volume_uuids.vol_uuid, volume_uuids.vol_total_capacity, volume_uuids.vol_available_capacity FROM (files RIGHT JOIN volume_uuids ON (((files.vol_id)::text = (volume_uuids.vol_id)::text))) WHERE (files.folder_id = 1);

-- ----------------------------
--  View structure for "files_latest"
-- ----------------------------
DROP VIEW IF EXISTS "files_latest";
CREATE VIEW "files_latest" AS SELECT a.vol_id, a.folder_id, a.file_name, a.file_id, a.file_size, a.file_create_date, a.file_mod_date, a.file_uti FROM files a WHERE ((a.file_id = 2) AND (a.file_mod_date = (SELECT max(b.file_mod_date) AS max FROM files b WHERE (((a.vol_id)::text = (b.vol_id)::text) AND (a.file_id = b.file_id)))));

-- ----------------------------
--  View structure for "volumes_all"
-- ----------------------------
DROP VIEW IF EXISTS "volumes_all";
CREATE VIEW "volumes_all" AS SELECT a.vol_id, a.vol_uuid, a.vol_total_capacity, a.vol_available_capacity, b.vol_id AS files_vol_id, b.folder_id, b.vol_name FROM (volume_uuids a LEFT JOIN volumes b ON (((a.vol_id)::text = (b.vol_id)::text)));

-- ----------------------------
--  View structure for "rk_volume_uuid"
-- ----------------------------
DROP VIEW IF EXISTS "rk_volume_uuid";
CREATE VIEW "rk_volume_uuid" AS SELECT "RKVolume".name, volume_uuids.vol_id, "RKVolume"."createDate", "RKVolume"."diskUuid", volume_uuids.vol_uuid, "RKVolume".uuid FROM (volume_uuids RIGHT JOIN "RKVolume" ON (((volume_uuids.vol_uuid)::text = "RKVolume"."diskUuid")));

-- ----------------------------
--  View structure for "rk_master_volume"
-- ----------------------------
DROP VIEW IF EXISTS "rk_master_volume";
CREATE VIEW "rk_master_volume" AS SELECT "RKMaster"."fileName", ((('/Volumes/'::text || "RKVolume".name) || '/'::text) || convert_from(("RKMaster"."imagePath")::bytea, 'utf8'::name)) AS image_path, "RKMaster"."fileSize", "RKVolume".name, "RKVolume"."diskUuid", "RKVolume"."createDate", "RKVolume".label, volume_uuids.vol_id FROM (("RKMaster" JOIN "RKVolume" ON (("RKMaster"."fileVolumeUuid" = "RKVolume".uuid))) RIGHT JOIN volume_uuids ON (("RKVolume"."diskUuid" = (volume_uuids.vol_uuid)::text)));

-- ----------------------------
--  View structure for "names"
-- ----------------------------
DROP VIEW IF EXISTS "names";
CREATE VIEW "names" AS SELECT name_strings.string AS name, super_strings.string AS super_name, names_ids.name_seq_no, names_ids.name_id FROM ((strings name_strings JOIN names_ids ON (((name_strings.str_id)::text = (names_ids.string_id)::text))) JOIN strings super_strings ON (((names_ids.super_name_id)::text = (super_strings.str_id)::text)));

-- ----------------------------
--  Function structure for path_from_vol_id_file_id(varchar, int4)
-- ----------------------------
DROP FUNCTION IF EXISTS "path_from_vol_id_file_id"(varchar, int4);
CREATE FUNCTION "path_from_vol_id_file_id"(IN vol_id varchar, IN file_id int4) RETURNS "varchar" 
	AS $BODY$

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

        $BODY$
	LANGUAGE sql
	COST 100
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "path_from_vol_id_file_id"(IN vol_id varchar, IN file_id int4) OWNER TO "donb";

-- ----------------------------
--  Function structure for path_from_vol_id_file_id(varchar, int8)
-- ----------------------------
DROP FUNCTION IF EXISTS "path_from_vol_id_file_id"(varchar, int8);
CREATE FUNCTION "path_from_vol_id_file_id"(IN vol_id varchar, IN file_id int8) RETURNS "varchar" 
	AS $BODY$

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

        $BODY$
	LANGUAGE sql
	COST 100
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "path_from_vol_id_file_id"(IN vol_id varchar, IN file_id int8) OWNER TO "donb";

-- ----------------------------
--  Function structure for string_ts_query(text, text, text, int4, varchar, numeric, float4, text)
-- ----------------------------
DROP FUNCTION IF EXISTS "string_ts_query"(text, text, text, int4, varchar, numeric, float4, text);
CREATE FUNCTION "string_ts_query"(IN fullname text, IN pipeterms text, INOUT "name" text, INOUT len int4, INOUT string_id varchar, INOUT sub_match numeric, INOUT "rank" float4, INOUT super_name text) RETURNS SETOF "record" 
	AS $BODY$

select 
    a.string as name , 
    length(a.string) as len,
    a.string_id,
    case when fullname ilike '%' || a.string || '%' then 1.0 else 0.0 end as sub_match ,
    ts_rank_cd(a.string_ts, query, 8) AS rank ,
    b.string as super_name

--"select b.string as super_name from names_ids, strings b where names_ids.string_id = '" & string_id & "' and super_name_id = b.string_id;"

from 
    strings a
    LEFT OUTER JOIN names_ids
                 ON a.string_id      = names_ids.string_id,
    to_tsquery(pipeterms) query,
    --names_ids, 
    strings b

--INNER JOIN strings a, names_ids ON (names_ids.string_id = a.string_id)
where 
    query @@ a.string_ts
    -- and names_ids.string_id = a.string_id
    and super_name_id = b.string_id
order by 
    sub_match desc, rank desc, len desc

-- limit 10;


--CREATE FUNCTION dup(int) RETURNS TABLE(f1 int, f2 text)
--    AS $$ SELECT $1, CAST($1 AS text) || ' is text' $$
--        LANGUAGE SQL;


/*
  new.string_ts :=
     setweight(to_tsvector('pg_catalog.english', coalesce(new.title,'')), 'A') ||
     setweight(to_tsvector('pg_catalog.english', coalesce(new.body,'')), 'D');
*/

$BODY$
	LANGUAGE sql
	COST 100
	ROWS 1000
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "string_ts_query"(IN fullname text, IN pipeterms text, INOUT "name" text, INOUT len int4, INOUT string_id varchar, INOUT sub_match numeric, INOUT "rank" float4, INOUT super_name text) OWNER TO "donb";

-- ----------------------------
--  Function structure for path_from_name_id(text)
-- ----------------------------
DROP FUNCTION IF EXISTS "path_from_name_id"(text);
CREATE FUNCTION "path_from_name_id"(IN string_id text) RETURNS "varchar" 
	AS $BODY$

        SELECT '::' || path FROM
--        SELECT * FROM
        (

            WITH RECURSIVE pathto(path,  id) AS (
                /* non-recursive term  */
                SELECT 'non-recursive: '||CAST (strings.string AS text),  names_ids.super_name_id 
                    FROM names_ids, strings 
                    WHERE names_ids.string_id = $1 
                    and names_ids.string_id = strings.string_id
                UNION
                /* recursive term  (here the recursive term can contain a reference to the query's own output. ) */
                SELECT pathto.path || ':' || strings.string ,  names_ids.super_name_id
                    FROM names_ids, pathto , strings
                    WHERE names_ids.string_id = pathto.id
                    and names_ids.string_id = strings.string_id
            )

            SELECT * FROM pathto

        ) AS pathto(path,  id)

        --WHERE id = 1
        ;

        $BODY$
	LANGUAGE sql
	COST 100
	CALLED ON NULL INPUT
	SECURITY INVOKER
	VOLATILE;
ALTER FUNCTION "path_from_name_id"(IN string_id text) OWNER TO "donb";

-- ----------------------------
--  Primary key structure for table "volume_uuids"
-- ----------------------------
ALTER TABLE "volume_uuids" ADD CONSTRAINT "volume_uuids_pkey" PRIMARY KEY ("vol_id", "vol_uuid") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table "files"
-- ----------------------------
ALTER TABLE "files" ADD CONSTRAINT "files_pkey" PRIMARY KEY ("file_mod_date", "file_id", "file_name", "vol_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table "RKVolume"
-- ----------------------------
ALTER TABLE "RKVolume" ADD CONSTRAINT "RKVolume_pkey" PRIMARY KEY ("modelId") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table "RKMaster"
-- ----------------------------
ALTER TABLE "RKMaster" ADD CONSTRAINT "RKMaster_pkey" PRIMARY KEY ("modelId") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table "strings"
-- ----------------------------
ALTER TABLE "strings" ADD CONSTRAINT "names_pkey" PRIMARY KEY ("str_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table "names_ids"
-- ----------------------------
ALTER TABLE "names_ids" ADD CONSTRAINT "names_pkey1" PRIMARY KEY ("name_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

