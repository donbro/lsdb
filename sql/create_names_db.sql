/*
 Navicat Premium Data Transfer

 Source Server         : localhost 5432
 Source Server Type    : PostgreSQL
 Source Server Version : 90202
 Source Host           : localhost
 Source Database       : names
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 90202
 File Encoding         : utf-8

 Date: 05/17/2013 16:21:38 PM
*/

-- ----------------------------
--  Table structure for "names"
-- ----------------------------
DROP TABLE IF EXISTS "names";
CREATE TABLE "names" (
	"name_id" varchar(8) NOT NULL,
	"name" varchar(256) NOT NULL
)
WITH (OIDS=FALSE);
ALTER TABLE "names" OWNER TO "donb";

-- ----------------------------
--  Primary key structure for table "names"
-- ----------------------------
ALTER TABLE "names" ADD CONSTRAINT "names_pkey" PRIMARY KEY ("name_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

