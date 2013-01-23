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

 Date: 01/23/2013 12:50:52 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `files`
-- ----------------------------
DROP TABLE IF EXISTS `files`;
CREATE TABLE `files` (
  `vol_id` char(8) COLLATE utf8_bin NOT NULL,
  `folder_id` int(11) DEFAULT NULL,
  `file_name` varchar(255) COLLATE utf8_bin NOT NULL,
  `file_id` int(11) NOT NULL,
  `file_size` bigint(20) NOT NULL,
  `file_create_date` datetime NOT NULL,
  `file_mod_date` datetime NOT NULL,
  UNIQUE KEY `vol_folder_file_mod_date` (`vol_id`,`folder_id`,`file_name`,`file_mod_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
delimiter ;;
CREATE TRIGGER `trigger_before_insert_files` BEFORE INSERT ON `files` FOR EACH ROW BEGIN 

	/* custom "auto" identity column: vol0001 */
	/* eg,	vol0167  Acapulco H.E.A.T. One                                        
			vol0165  Action Man • WitchBlade       */

	IF NEW.vol_id NOT RLIKE "vol[0-9][0-9][0-9][0-9]" then
		SET NEW.vol_id = concat( 'vol' ,  substr( concat( '0000' , 1 + ifnull( (select max(substr(vol_id,-4)) from files) , 0) ) , -4 ) ) ;  
	END if;

END;
 ;;
delimiter ;

-- ----------------------------
--  Records of `files`
-- ----------------------------
BEGIN;
INSERT INTO `files` VALUES ('vol0001', '1', 'Genie', '2', '0', '2011-07-02 21:02:54', '2013-01-16 06:51:12'), ('vol0001', '2', 'Users', '48946', '0', '2011-06-24 21:49:24', '2011-09-02 18:36:34'), ('vol0001', '48946', 'donb', '328394', '0', '2011-09-02 18:36:34', '2013-01-22 07:00:39'), ('vol0001', '328394', 'projects', '541309', '0', '2011-09-06 02:30:45', '2013-01-19 09:26:32'), ('vol0001', '541309', 'lsdb', '22755950', '0', '2007-10-30 05:49:13', '2012-09-12 22:05:32'), ('vol0001', '22755950', 'tests', '22756449', '0', '2009-01-24 08:49:20', '2012-07-19 04:44:04'), ('vol0001', '22756449', 'unicode filename test', '22756468', '0', '2007-01-02 16:55:04', '2009-02-04 03:30:32'), ('vol0001', '22756468', 'Adobe® Pro Fonts', '22756470', '13', '2007-01-02 13:18:08', '2007-01-02 13:18:08'), ('vol0002', '1', 'Dunharrow', '2', '0', '2012-10-03 00:52:17', '2013-01-17 14:06:08'), ('vol0002', '2', 'pdf', '75686', '0', '2012-11-29 23:29:38', '2012-12-21 22:37:25'), ('vol0002', '75686', 'Xcode 4 Unleashed 2nd ed. - F. Anderson (Sams, 2012) WW.pdf', '75756', '19591553', '2012-11-01 14:43:39', '2012-11-01 14:43:39');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
