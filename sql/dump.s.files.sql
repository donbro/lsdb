--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: check_consistency(); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION check_consistency() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$--CREATE OR REPLACE FUNCTION check_consistency() RETURNS TRIGGER AS $$
  BEGIN
    IF EXISTS (SELECT * FROM product WHERE name=NEW.name AND expired='false') THEN
      RAISE EXCEPTION 'duplicated!!!';              
    END IF;
    RETURN NEW;
  END;
--$$ LANGUAGE plpgsql;
$_$;


ALTER FUNCTION public.check_consistency() OWNER TO donb;

--
-- Name: create_function_name_id(); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION create_function_name_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

-- scheme for id is "n000000" or  'n[0-9]{6}'

--debugging output:
-- new.file_name := 'z' || new.name_id || 'K' || new.name_id is null || ((NEW.name_id NOT SIMILAR TO 'n[0-9]{6}'));

IF new.name_id is null or (NEW.name_id NOT SIMILAR TO 'n[0-9]{6}') then

        new.name_id := 
                concat( 'n' , 
                    right( concat( '0000000' , (1 + (select substring( coalesce( max(name_id), 'n000000' )  from 2 for 6) from names )::integer)::text ) , 6)
                    )
        ;

end if;

RETURN new; 

END;
$$;


ALTER FUNCTION public.create_function_name_id() OWNER TO donb;

--
-- Name: create_function_string_id(); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION create_function_string_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

-- scheme for string ids is: "str000000" or  'str[0-9]{6}'

--debugging output:
-- new.file_name := 'z' || new.string_id || 'K' || new.string_id is null || ((NEW.string_id NOT SIMILAR TO 'str[0-9]{6}'));

IF new.string_id is null or (NEW.string_id NOT SIMILAR TO 'str[0-9]{6}') then

        new.string_id := 
                concat( 'str' , 
                    right( concat( '0000000' , (1 + (select substring( coalesce( max(string_id), 'str000000' )  from 4 for 6) from strings )::integer)::text ) , 6)
                    )
        ;

end if;

new.string_ts := to_tsvector('english', new.string);

RETURN new; 

/*
  new.string_ts :=
     setweight(to_tsvector('pg_catalog.english', coalesce(new.title,'')), 'A') ||
     setweight(to_tsvector('pg_catalog.english', coalesce(new.body,'')), 'D');
*/

END;

--BEGIN
--    IF EXISTS (SELECT 1 FROM "myschema".mytable WHERE "MyKey" = NEW."MyKey") THEN
--        RETURN NULL;
--    ELSE
--        RETURN NEW;
--    END IF;
--END;

--CREATE RULE "my_table_on_duplicate_ignore" AS ON INSERT TO "my_table"
--  WHERE EXISTS(SELECT 1 FROM my_table 
--                WHERE (pk_col_1, pk_col_2)=(NEW.pk_col_1, NEW.pk_col_2))
--  DO INSTEAD NOTHING;

$$;


ALTER FUNCTION public.create_function_string_id() OWNER TO donb;

--
-- Name: path_from_name_id(text); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION path_from_name_id(string_id text) RETURNS character varying
    LANGUAGE sql
    AS $_$

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

        $_$;


ALTER FUNCTION public.path_from_name_id(string_id text) OWNER TO donb;

--
-- Name: path_from_vol_id_file_id(character varying, integer); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION path_from_vol_id_file_id(vol_id character varying, file_id integer) RETURNS character varying
    LANGUAGE sql
    AS $_$

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

        $_$;


ALTER FUNCTION public.path_from_vol_id_file_id(vol_id character varying, file_id integer) OWNER TO donb;

--
-- Name: path_from_vol_id_file_id(character varying, bigint); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION path_from_vol_id_file_id(vol_id character varying, file_id bigint) RETURNS character varying
    LANGUAGE sql
    AS $_$

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

        $_$;


ALTER FUNCTION public.path_from_vol_id_file_id(vol_id character varying, file_id bigint) OWNER TO donb;

--
-- Name: string_ts_query(text, text); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION string_ts_query(fullname text, pipeterms text) RETURNS TABLE(name text, len integer, string_id character varying, sub_match numeric, rank real, super_name text)
    LANGUAGE sql
    AS $_$

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

$_$;


ALTER FUNCTION public.string_ts_query(fullname text, pipeterms text) OWNER TO donb;

--
-- Name: strings_ts_procedure(); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION strings_ts_procedure() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ BEGIN update strings set string_ts = to_tsvector('english', string); END; $$;


ALTER FUNCTION public.strings_ts_procedure() OWNER TO donb;

--
-- Name: update_modelname_function(); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION update_modelname_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
IF NEW.vol_id NOT LIKE 'vol[0-9][0-9][0-9][0-9]' then
   select * from NEW;
end if;
END;
$$;


ALTER FUNCTION public.update_modelname_function() OWNER TO donb;

--
-- Name: update_modelname_function2(); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION update_modelname_function2() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
  IF tg_op = 'INSERT' THEN
     new.model_name := upper(new.model_name);
     RETURN new;
  END IF;
  IF tg_op = 'UPDATE' THEN
     old.model_name := upper(old.model_name);
     RETURN new;
  END IF;
END
$$;


ALTER FUNCTION public.update_modelname_function2() OWNER TO donb;

--
-- Name: update_vol_id(); Type: FUNCTION; Schema: public; Owner: donb
--

CREATE FUNCTION update_vol_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.update_vol_id() OWNER TO donb;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: RKMaster; Type: TABLE; Schema: public; Owner: donb; Tablespace: 
--

CREATE TABLE "RKMaster" (
    "modelId" integer NOT NULL,
    uuid text,
    name text,
    "projectUuid" text,
    "importGroupUuid" text,
    "fileVolumeUuid" text,
    "alternateMasterUuid" text,
    "originalVersionUuid" text,
    "originalVersionName" text,
    "fileName" text,
    type text,
    subtype text,
    "fileIsReference" integer,
    "isExternallyEditable" integer,
    "isTrulyRaw" integer,
    "isMissing" integer,
    "hasAttachments" integer,
    "hasNotes" integer,
    "hasFocusPoints" integer,
    "imagePath" text,
    "fileSize" integer,
    "pixelFormat" integer,
    duration bytea,
    "imageDate" bytea,
    "fileCreationDate" bytea,
    "fileModificationDate" bytea,
    "imageHash" text,
    "originalFileName" text,
    "originalFileSize" integer,
    "imageFormat" integer,
    "createDate" bytea,
    "isInTrash" integer,
    "faceDetectionState" integer,
    "colorSpaceName" text,
    "colorSpaceDefinition" bytea,
    "fileAliasData" bytea,
    "importedBy" integer
);


ALTER TABLE public."RKMaster" OWNER TO donb;

--
-- Name: RKVolume; Type: TABLE; Schema: public; Owner: donb; Tablespace: 
--

CREATE TABLE "RKVolume" (
    "modelId" integer NOT NULL,
    uuid text,
    name text,
    "diskUuid" text,
    label text,
    "isOffline" integer,
    "createDate" bytea,
    "modDate" bytea
);


ALTER TABLE public."RKVolume" OWNER TO donb;

--
-- Name: files; Type: TABLE; Schema: public; Owner: donb; Tablespace: 
--

CREATE TABLE files (
    vol_id character varying(8) NOT NULL,
    folder_id bigint NOT NULL,
    file_name character varying(255) NOT NULL,
    file_id bigint NOT NULL,
    file_size bigint NOT NULL,
    file_create_date timestamp without time zone NOT NULL,
    file_mod_date timestamp without time zone NOT NULL,
    file_uti character varying(128)
);


ALTER TABLE public.files OWNER TO donb;

--
-- Name: files_latest; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW files_latest AS
    SELECT a.vol_id, a.folder_id, a.file_name, a.file_id, a.file_size, a.file_create_date, a.file_mod_date, a.file_uti FROM files a WHERE ((a.file_id = 2) AND (a.file_mod_date = (SELECT max(b.file_mod_date) AS max FROM files b WHERE (((a.vol_id)::text = (b.vol_id)::text) AND (a.file_id = b.file_id)))));


ALTER TABLE public.files_latest OWNER TO donb;

--
-- Name: files_not_latest; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW files_not_latest AS
    SELECT files.vol_id, files.folder_id, files.file_name, files.file_id, files.file_size, files.file_create_date, files.file_mod_date, files.file_uti FROM files WHERE ((((files.vol_id)::text = 'vol0003'::text) AND (files.file_id = 2)) AND (files.file_mod_date <> (SELECT max(files.file_mod_date) AS max FROM files WHERE (((files.vol_id)::text = 'vol0003'::text) AND (files.file_id = 2)))));


ALTER TABLE public.files_not_latest OWNER TO donb;

--
-- Name: names_ids; Type: TABLE; Schema: public; Owner: donb; Tablespace: 
--

CREATE TABLE names_ids (
    string_id character varying(10) NOT NULL,
    super_name_id character varying(10),
    name_seq_no smallint,
    name_id character varying(8) NOT NULL
);


ALTER TABLE public.names_ids OWNER TO donb;

--
-- Name: strings; Type: TABLE; Schema: public; Owner: donb; Tablespace: 
--

CREATE TABLE strings (
    str_id character varying(10) NOT NULL,
    string character varying(256) NOT NULL,
    str_ts tsvector
);


ALTER TABLE public.strings OWNER TO donb;

--
-- Name: names; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW names AS
    SELECT name_strings.string AS name, super_strings.string AS super_name, names_ids.name_seq_no, names_ids.name_id FROM ((strings name_strings JOIN names_ids ON (((name_strings.str_id)::text = (names_ids.string_id)::text))) JOIN strings super_strings ON (((names_ids.super_name_id)::text = (super_strings.str_id)::text)));


ALTER TABLE public.names OWNER TO donb;

--
-- Name: volume_uuids; Type: TABLE; Schema: public; Owner: donb; Tablespace: 
--

CREATE TABLE volume_uuids (
    vol_id character varying(8) NOT NULL,
    vol_uuid character(36) NOT NULL,
    vol_total_capacity bigint NOT NULL,
    vol_available_capacity bigint NOT NULL
);


ALTER TABLE public.volume_uuids OWNER TO donb;

--
-- Name: rk_master_volume; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW rk_master_volume AS
    SELECT "RKMaster"."fileName", ((('/Volumes/'::text || "RKVolume".name) || '/'::text) || convert_from(("RKMaster"."imagePath")::bytea, 'utf8'::name)) AS image_path, "RKMaster"."fileSize", "RKVolume".name, "RKVolume"."diskUuid", "RKVolume"."createDate", "RKVolume".label, volume_uuids.vol_id FROM (("RKMaster" JOIN "RKVolume" ON (("RKMaster"."fileVolumeUuid" = "RKVolume".uuid))) RIGHT JOIN volume_uuids ON (("RKVolume"."diskUuid" = (volume_uuids.vol_uuid)::text)));


ALTER TABLE public.rk_master_volume OWNER TO donb;

--
-- Name: rk_volume_uuid; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW rk_volume_uuid AS
    SELECT "RKVolume".name, volume_uuids.vol_id, "RKVolume"."createDate", "RKVolume"."diskUuid", volume_uuids.vol_uuid, "RKVolume".uuid FROM (volume_uuids RIGHT JOIN "RKVolume" ON (((volume_uuids.vol_uuid)::text = "RKVolume"."diskUuid")));


ALTER TABLE public.rk_volume_uuid OWNER TO donb;

--
-- Name: volumes; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW volumes AS
    SELECT DISTINCT files.vol_id, files.folder_id, files.file_name AS vol_name, volume_uuids.vol_uuid, volume_uuids.vol_total_capacity, volume_uuids.vol_available_capacity FROM (files RIGHT JOIN volume_uuids ON (((files.vol_id)::text = (volume_uuids.vol_id)::text))) WHERE (files.folder_id = 1);


ALTER TABLE public.volumes OWNER TO donb;

--
-- Name: volumes_all; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW volumes_all AS
    SELECT a.vol_id, a.vol_uuid, a.vol_total_capacity, a.vol_available_capacity, b.vol_id AS files_vol_id, b.folder_id, b.vol_name FROM (volume_uuids a LEFT JOIN volumes b ON (((a.vol_id)::text = (b.vol_id)::text)));


ALTER TABLE public.volumes_all OWNER TO donb;

--
-- Name: volumes_mod_date; Type: VIEW; Schema: public; Owner: donb
--

CREATE VIEW volumes_mod_date AS
    SELECT files.vol_id, files.file_name AS volume_name, files.file_mod_date FROM files WHERE ((files.folder_id = 1) AND (files.file_mod_date = (SELECT max(b.file_mod_date) AS max FROM files b WHERE ((b.folder_id = 1) AND ((b.vol_id)::text = (files.vol_id)::text)))));


ALTER TABLE public.volumes_mod_date OWNER TO donb;

--
-- Name: RKMaster_pkey; Type: CONSTRAINT; Schema: public; Owner: donb; Tablespace: 
--

ALTER TABLE ONLY "RKMaster"
    ADD CONSTRAINT "RKMaster_pkey" PRIMARY KEY ("modelId");


--
-- Name: RKVolume_pkey; Type: CONSTRAINT; Schema: public; Owner: donb; Tablespace: 
--

ALTER TABLE ONLY "RKVolume"
    ADD CONSTRAINT "RKVolume_pkey" PRIMARY KEY ("modelId");


--
-- Name: files_pkey; Type: CONSTRAINT; Schema: public; Owner: donb; Tablespace: 
--

ALTER TABLE ONLY files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_mod_date, file_id, file_name, vol_id);


--
-- Name: names_pkey; Type: CONSTRAINT; Schema: public; Owner: donb; Tablespace: 
--

ALTER TABLE ONLY strings
    ADD CONSTRAINT names_pkey PRIMARY KEY (str_id);


--
-- Name: names_pkey1; Type: CONSTRAINT; Schema: public; Owner: donb; Tablespace: 
--

ALTER TABLE ONLY names_ids
    ADD CONSTRAINT names_pkey1 PRIMARY KEY (name_id);


--
-- Name: volume_uuids_pkey; Type: CONSTRAINT; Schema: public; Owner: donb; Tablespace: 
--

ALTER TABLE ONLY volume_uuids
    ADD CONSTRAINT volume_uuids_pkey PRIMARY KEY (vol_id, vol_uuid);


--
-- Name: RKMaster_alternateMasterUuid_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_alternateMasterUuid_index" ON "RKMaster" USING btree ("alternateMasterUuid");


--
-- Name: RKMaster_createDate_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_createDate_index" ON "RKMaster" USING btree ("createDate");


--
-- Name: RKMaster_faceDetectionState_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_faceDetectionState_index" ON "RKMaster" USING btree ("faceDetectionState");


--
-- Name: RKMaster_fileCreationDate_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_fileCreationDate_index" ON "RKMaster" USING btree ("fileCreationDate");


--
-- Name: RKMaster_fileIsReference_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_fileIsReference_index" ON "RKMaster" USING btree ("fileIsReference");


--
-- Name: RKMaster_fileModificationDate_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_fileModificationDate_index" ON "RKMaster" USING btree ("fileModificationDate");


--
-- Name: RKMaster_fileName_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_fileName_index" ON "RKMaster" USING btree ("fileName");


--
-- Name: RKMaster_fileSize_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_fileSize_index" ON "RKMaster" USING btree ("fileSize");


--
-- Name: RKMaster_fileVolumeUuid_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_fileVolumeUuid_index" ON "RKMaster" USING btree ("fileVolumeUuid");


--
-- Name: RKMaster_imageFormat_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_imageFormat_index" ON "RKMaster" USING btree ("imageFormat");


--
-- Name: RKMaster_importGroupUuid_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_importGroupUuid_index" ON "RKMaster" USING btree ("importGroupUuid");


--
-- Name: RKMaster_isExternallyEditable_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_isExternallyEditable_index" ON "RKMaster" USING btree ("isExternallyEditable");


--
-- Name: RKMaster_isInTrash_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_isInTrash_index" ON "RKMaster" USING btree ("isInTrash");


--
-- Name: RKMaster_originalFileName_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_originalFileName_index" ON "RKMaster" USING btree ("originalFileName");


--
-- Name: RKMaster_originalFileSize_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_originalFileSize_index" ON "RKMaster" USING btree ("originalFileSize");


--
-- Name: RKMaster_projectUuid_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_projectUuid_index" ON "RKMaster" USING btree ("projectUuid");


--
-- Name: RKMaster_type_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_type_index" ON "RKMaster" USING btree (type);


--
-- Name: RKMaster_uuid_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKMaster_uuid_index" ON "RKMaster" USING btree (uuid);


--
-- Name: RKVolume_createDate_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKVolume_createDate_index" ON "RKVolume" USING btree ("createDate");


--
-- Name: RKVolume_diskUuid_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKVolume_diskUuid_index" ON "RKVolume" USING btree ("diskUuid");


--
-- Name: RKVolume_modDate_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKVolume_modDate_index" ON "RKVolume" USING btree ("modDate");


--
-- Name: RKVolume_name_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKVolume_name_index" ON "RKVolume" USING btree (name);


--
-- Name: RKVolume_uuid_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX "RKVolume_uuid_index" ON "RKVolume" USING btree (uuid);


--
-- Name: files_file_size; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX files_file_size ON files USING btree (file_size);


--
-- Name: string_index; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE UNIQUE INDEX string_index ON strings USING btree (string);


--
-- Name: string_ts_gin; Type: INDEX; Schema: public; Owner: donb; Tablespace: 
--

CREATE INDEX string_ts_gin ON strings USING gin (str_ts);


--
-- Name: my_table_on_duplicate_ignore; Type: RULE; Schema: public; Owner: donb
--

CREATE RULE my_table_on_duplicate_ignore AS ON INSERT TO strings WHERE (EXISTS (SELECT 1 FROM strings WHERE ((strings.string)::text = (new.string)::text))) DO INSTEAD SELECT strings.str_id AS string_id, strings.string FROM strings WHERE ((strings.string)::text = (new.string)::text);


--
-- Name: my_table_on_duplicate_ignore2; Type: RULE; Schema: public; Owner: donb
--

CREATE RULE my_table_on_duplicate_ignore2 AS ON INSERT TO strings DO SELECT strings.str_id AS string_id, strings.string FROM strings WHERE ((strings.string)::text = (new.string)::text);


--
-- Name: files_insert_before; Type: TRIGGER; Schema: public; Owner: donb
--

CREATE TRIGGER files_insert_before BEFORE INSERT ON files FOR EACH ROW EXECUTE PROCEDURE update_vol_id();


--
-- Name: names_insert_before; Type: TRIGGER; Schema: public; Owner: donb
--

CREATE TRIGGER names_insert_before BEFORE INSERT ON names_ids FOR EACH ROW EXECUTE PROCEDURE create_function_name_id();


--
-- Name: strings_insert_before; Type: TRIGGER; Schema: public; Owner: donb
--

CREATE TRIGGER strings_insert_before BEFORE INSERT ON strings FOR EACH ROW EXECUTE PROCEDURE create_function_string_id();


--
-- Name: public; Type: ACL; Schema: -; Owner: donb
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM donb;
GRANT ALL ON SCHEMA public TO donb;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

