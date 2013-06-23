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

 Date: 05/17/2013 18:01:16 PM
*/

-- ----------------------------
--  Table structure for "strings"
-- ----------------------------
DROP TABLE IF EXISTS "strings";
CREATE TABLE "strings" (
	"string_id" varchar(8) NOT NULL,
	"string" varchar(256) NOT NULL
)
WITH (OIDS=FALSE);
ALTER TABLE "strings" OWNER TO "donb";

-- ----------------------------
--  Records of "strings"
-- ----------------------------
BEGIN;
INSERT INTO "strings" VALUES ('n000001', 'hello world!');
COMMIT;

-- ----------------------------
--  Primary key structure for table "strings"
-- ----------------------------
ALTER TABLE "strings" ADD CONSTRAINT "names_pkey" PRIMARY KEY ("string_id") NOT DEFERRABLE INITIALLY IMMEDIATE;

