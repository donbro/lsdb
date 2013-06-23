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

 Date: 05/20/2013 18:17:54 PM
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
--  View structure for "volumes_all"
-- ----------------------------
DROP VIEW IF EXISTS "volumes_all";
CREATE VIEW "volumes_all" AS SELECT a.vol_id, a.vol_uuid, a.vol_total_capacity, a.vol_available_capacity, b.vol_id AS files_vol_id, b.folder_id, b.file_name FROM (volume_uuids a LEFT JOIN volumes b ON (((a.vol_id)::text = (b.vol_id)::text)));

-- ----------------------------
--  View structure for "files_latest"
-- ----------------------------
DROP VIEW IF EXISTS "files_latest";
CREATE VIEW "files_latest" AS SELECT a.vol_id, a.folder_id, a.file_name, a.file_id, a.file_size, a.file_create_date, a.file_mod_date, a.file_uti FROM files a WHERE ((a.file_id = 2) AND (a.file_mod_date = (SELECT max(b.file_mod_date) AS max FROM files b WHERE (((a.vol_id)::text = (b.vol_id)::text) AND (a.file_id = b.file_id)))));

-- ----------------------------
--  View structure for "volumes"
-- ----------------------------
DROP VIEW IF EXISTS "volumes";
CREATE VIEW "volumes" AS SELECT DISTINCT files.vol_id, files.folder_id, files.file_name, volume_uuids.vol_uuid, volume_uuids.vol_total_capacity, volume_uuids.vol_available_capacity FROM (files RIGHT JOIN volume_uuids ON (((files.vol_id)::text = (volume_uuids.vol_id)::text))) WHERE (files.folder_id = 1);

-- ----------------------------
--  Primary key structure for table "volume_uuids"
-- ----------------------------
ALTER TABLE "volume_uuids" ADD CONSTRAINT "volume_uuids_pkey" PRIMARY KEY ("vol_id", "vol_uuid") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table "files"
-- ----------------------------
ALTER TABLE "files" ADD CONSTRAINT "files_pkey" PRIMARY KEY ("file_mod_date", "file_id", "file_name", "vol_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

