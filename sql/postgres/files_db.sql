/*
 Navicat Premium Data Transfer

 Source Server         : localhost 5432
 Source Server Type    : PostgreSQL
 Source Server Version : 90202
 Source Host           : localhost
 Source Database       : files
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90000
 File Encoding         : utf-8

 Date: 05/05/2013 17:16:10 PM
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

-- ----------------------------
--  View structure for "volumes_view"
-- ----------------------------
DROP VIEW IF EXISTS "volumes_view";
CREATE VIEW "volumes_view" AS 
SELECT files.vol_id, files.folder_id, files.file_name, volume_uuids.vol_uuid, volume_uuids.vol_total_capacity, volume_uuids.vol_available_capacity 
FROM (files JOIN volume_uuids ON (((files.vol_id)::text = (volume_uuids.vol_id)::text))) 
WHERE ((files.folder_id = 1) AND (files.file_mod_date = (SELECT max(b.file_mod_date) AS max 
FROM files b 
WHERE (((b.vol_id)::text = (volume_uuids.vol_id)::text) AND (b.folder_id = 1)))));

-- ----------------------------
--  Primary key structure for table "volume_uuids"
-- ----------------------------
ALTER TABLE "volume_uuids" ADD CONSTRAINT "volume_uuids_pkey" 
PRIMARY KEY ("vol_id", "vol_uuid") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Primary key structure for table "files"
-- ----------------------------
ALTER TABLE "files" ADD CONSTRAINT "files_pkey" 
PRIMARY KEY ("file_mod_date", "file_id", "file_name", "vol_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

-- ----------------------------
--  Triggers structure for table "files"
-- ----------------------------
CREATE TRIGGER "files_insert_before" BEFORE INSERT ON "files" 
FOR EACH STATEMENT EXECUTE PROCEDURE "update_modelname_function2"();

