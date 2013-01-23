/*
 Navicat Premium Data Transfer

 Source Server         : local mysql
 Source Server Type    : MySQL
 Source Server Version : 50515
 Source Host           : localhost
 Source Database       : files

 Target Server Type    : MySQL
 Target Server Version : 50515
 File Encoding         : utf-8

 Date: 01/23/2013 16:02:11 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `volume_uuids`
-- ----------------------------
DROP TABLE IF EXISTS `volume_uuids`;
CREATE TABLE `volume_uuids` (
  `vol_id` char(8) NOT NULL,
  `vol_uuid` char(36) NOT NULL,
  PRIMARY KEY (`vol_id`,`vol_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `volume_uuids`
-- ----------------------------
BEGIN;
INSERT INTO `volume_uuids` VALUES ('vol0002', 'FDA5D9B7-92F3-39FE-A0F1-C871BE964076'), ('vol0005', 'F6ABF7BE-4306-3AA4-AC02-E7042A15043B');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
