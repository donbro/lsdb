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

 Date: 02/18/2013 22:44:05 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `files`
-- ----------------------------
DROP TABLE IF EXISTS `files`;
CREATE TABLE `files` (
  `vol_id` char(8) COLLATE utf8_bin NOT NULL,
  `folder_id` int(11) NOT NULL DEFAULT '0',
  `file_name` varchar(255) COLLATE utf8_bin NOT NULL,
  `file_id` int(11) NOT NULL,
  `file_size` bigint(20) NOT NULL,
  `file_create_date` datetime NOT NULL,
  `file_mod_date` datetime NOT NULL,
  `file_uti` varchar(128) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`vol_id`,`folder_id`,`file_name`,`file_mod_date`),
  UNIQUE KEY `vol_folder_file_mod_date` (`vol_id`,`folder_id`,`file_name`,`file_mod_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
delimiter ;;
CREATE TRIGGER `trigger_before_insert_files` BEFORE INSERT ON `files` FOR EACH ROW BEGIN 

	/* If we don't have a good vol_id upon insertion we do either:
		(1) find the volume by name and file_create_date or
	    (2) create custom auto identity column with the form 'vol0001' */
	
	IF NEW.vol_id NOT RLIKE "vol[0-9][0-9][0-9][0-9]" then

		set @vol_id = (select vol_id from files where files.file_create_date = new.file_create_date and files.file_name = new.file_name and files.folder_id = 1) ; 

		if not isnull(@vol_id) then 
			SET NEW.vol_id = @vol_id;  /* could be creating a duplicate entry here.  is okay: this trigger will still set and return vol_id */
		else
			SET NEW.vol_id = concat( 'vol' ,  substr( concat( '0000' , 1 + ifnull( (select max(substr(vol_id,-4)) from files) , 0) ) , -4 ) ) ;
		end if;

	END if;
	
	set @vol_id = (select NEW.vol_id) ;  

    /* before insert, this can be zero or one or mistakenly more than one */

	set @existing_count = (select count(*) from files where files.vol_id = new.vol_id and files.file_id = new.file_id) ; 


	/*set @vol_id = (select files.vol_id from files where files.vol_id = new.vol_id and files.folder_id = 1) ;  */

END;
 ;;
delimiter ;

-- ----------------------------
--  Records of `files`
-- ----------------------------
BEGIN;
INSERT INTO `files` VALUES ('vol0001', '1', 'Genie', '2', '0', '2011-07-02 21:02:54', '2013-01-16 06:51:12', 'public.volume'), ('vol0001', '2', 'Users', '48946', '0', '2011-06-24 21:49:24', '2011-09-02 18:36:34', 'public.folder'), ('vol0001', '48946', 'donb', '328394', '0', '2011-09-02 18:36:34', '2013-02-17 19:02:31', 'public.folder'), ('vol0001', '328394', 'projects', '541309', '0', '2011-09-06 02:30:45', '2013-02-08 07:36:45', 'public.folder'), ('vol0001', '541309', 'lsdb', '40014149', '0', '2013-01-19 09:26:32', '2013-02-18 22:37:41', 'public.folder'), ('vol0001', '40014149', 'An insert, even against a duplicate key….txt', '41197622', '166', '2013-01-31 00:05:41', '2013-01-31 00:05:41', 'public.plain-text'), ('vol0001', '40014149', 'Module \'LaunchServices\'.txt', '42693837', '133635', '2013-02-18 22:37:41', '2013-02-18 22:37:41', 'public.plain-text'), ('vol0001', '40014149', 'Module \'mysql.connector\'.txt', '40415836', '2693', '2013-01-22 06:31:41', '2013-01-24 07:30:49', 'public.plain-text'), ('vol0001', '40014149', 'NSFileAttributes.txt', '40666462', '1397', '2013-01-24 10:21:07', '2013-01-24 10:21:07', 'public.plain-text'), ('vol0001', '40014149', 'README.md', '41194397', '6723', '2013-01-30 23:45:22', '2013-02-01 03:31:17', 'net.daringfireball.markdown'), ('vol0001', '40014149', 'cnx_mysql.py', '40432066', '1125', '2013-01-22 08:04:14', '2013-01-24 18:35:05', 'public.python-script'), ('vol0001', '40014149', 'dates', '41299565', '0', '2013-01-31 23:55:57', '2013-02-01 02:25:40', 'public.folder'), ('vol0001', '40014149', 'dbfiles', '42140840', '0', '2013-02-11 07:10:20', '2013-02-11 07:10:25', 'public.folder'), ('vol0001', '40014149', 'dir(NSError).txt', '42225317', '6153', '2013-02-12 12:08:49', '2013-02-12 12:08:49', 'public.plain-text'), ('vol0001', '40014149', 'dist', '41285016', '0', '2013-01-31 20:36:06', '2013-01-31 20:36:06', 'public.folder'), ('vol0001', '40014149', 'do_mysql.py', '40415987', '1287', '2013-01-22 06:33:05', '2013-01-22 14:22:17', 'public.python-script'), ('vol0001', '40014149', 'executing (1, \'Genie\', 2, 0,….txt', '40581232', '1430', '2013-01-23 14:30:12', '2013-01-23 14:30:12', 'public.plain-text'), ('vol0001', '40014149', 'lsdb', '41285570', '0', '2013-01-31 20:43:23', '2013-02-18 17:10:51', 'public.folder'), ('vol0001', '40014149', 'lsdb', '41285570', '0', '2013-01-31 20:43:23', '2013-02-19 03:30:51', 'public.folder'), ('vol0001', '40014149', 'lsdb.egg-info', '41283741', '0', '2013-01-31 20:20:12', '2013-01-31 20:37:03', 'public.folder'), ('vol0001', '40014149', 'repeated.py', '40699888', '586', '2013-01-24 18:10:05', '2013-01-24 18:10:05', 'public.python-script'), ('vol0001', '40014149', 'setup.py', '41285792', '785', '2013-01-31 20:45:39', '2013-01-31 20:45:39', 'public.python-script'), ('vol0001', '40014149', 'sql', '40595140', '0', '2013-01-23 17:50:46', '2013-02-08 07:38:13', 'public.folder'), ('vol0001', '40014149', 'untitled 3.txt', '40416759', '621', '2013-01-22 06:40:16', '2013-01-22 06:40:16', 'public.plain-text'), ('vol0001', '40595140', 'files.sql', '40595151', '2701', '2013-01-23 17:50:52', '2013-01-23 17:50:52', 'com.panic.coda.structured-query-language-file'), ('vol0001', '40595140', 'files2.sql', '42002394', '18037', '2013-02-08 07:38:13', '2013-02-08 07:38:13', 'com.panic.coda.structured-query-language-file'), ('vol0001', '40595140', 'volume_uuids.sql', '40609411', '958', '2013-01-23 21:02:11', '2013-01-23 21:02:12', 'com.panic.coda.structured-query-language-file'), ('vol0001', '41283741', 'PKG-INFO', '41283743', '1151', '2013-01-31 20:20:12', '2013-01-31 20:49:25', 'public.data'), ('vol0001', '41283741', 'SOURCES.txt', '41283747', '165', '2013-01-31 20:20:12', '2013-01-31 20:49:25', 'public.plain-text'), ('vol0001', '41283741', 'dependency_links.txt', '41283745', '1', '2013-01-31 20:20:12', '2013-01-31 20:49:25', 'public.plain-text'), ('vol0001', '41283741', 'entry_points.txt', '41283746', '42', '2013-01-31 20:20:12', '2013-01-31 20:49:25', 'public.plain-text'), ('vol0001', '41283741', 'top_level.txt', '41283744', '5', '2013-01-31 20:20:12', '2013-01-31 20:49:25', 'public.plain-text'), ('vol0001', '41285016', 'lsdb-0.5-py2.7.egg', '41285017', '13610', '2013-01-31 20:36:06', '2013-01-31 20:47:03', 'org.python.python-egg'), ('vol0001', '41285570', '__init__.py', '41286211', '0', '2013-01-31 20:51:14', '2013-01-31 20:51:14', 'public.python-script'), ('vol0001', '41285570', '__init__.pyc', '41286216', '129', '2013-01-31 20:51:18', '2013-01-31 20:51:18', 'dyn.ah62d4rv4ge81a8pd'), ('vol0001', '41285570', 'files.py', '41291492', '40645', '2013-01-31 22:05:28', '2013-02-19 03:26:59', 'public.python-script'), ('vol0001', '41285570', 'files.py', '41291492', '40663', '2013-01-31 22:05:28', '2013-02-19 03:30:47', 'public.python-script'), ('vol0001', '41285570', 'files.py', '41291492', '40666', '2013-01-31 22:05:28', '2013-02-19 03:38:25', 'public.python-script'), ('vol0001', '41285570', 'files.py', '41291492', '40669', '2013-01-31 22:05:28', '2013-02-19 03:39:05', 'public.python-script'), ('vol0001', '41285570', 'files.py', '41291492', '40645', '2013-01-31 22:05:28', '2013-02-19 03:42:11', 'public.python-script'), ('vol0001', '41285570', 'files.pyc', '42675372', '21197', '2013-02-18 17:10:51', '2013-02-18 17:10:51', 'dyn.ah62d4rv4ge81a8pd'), ('vol0001', '41285570', 'files.pyc', '42708928', '21754', '2013-02-19 03:30:51', '2013-02-19 03:30:51', 'dyn.ah62d4rv4ge81a8pd'), ('vol0001', '41299565', '__init__.py', '41300363', '0', '2013-01-31 20:51:14', '2013-01-31 20:51:14', 'public.python-script'), ('vol0001', '41299565', '__init__.pyc', '41300396', '130', '2013-02-01 00:07:40', '2013-02-01 00:07:40', 'dyn.ah62d4rv4ge81a8pd'), ('vol0001', '41299565', 'dateutils.py', '41300541', '9964', '2013-02-01 00:09:23', '2013-02-01 02:25:27', 'public.python-script'), ('vol0001', '41299565', 'dateutils.pyc', '41310112', '7940', '2013-02-01 02:25:40', '2013-02-01 02:25:40', 'dyn.ah62d4rv4ge81a8pd'), ('vol0001', '42140840', 'GetVolID.py', '42140845', '3558', '2013-02-11 07:10:25', '2013-02-11 13:08:58', 'public.python-script'), ('vol0002', '1', 'Roma', '2', '0', '2011-09-07 02:57:33', '2013-01-16 03:41:36', 'public.volume'), ('vol0002', '2', 'bittorrent', '104600', '0', '2011-10-14 04:40:34', '2013-02-18 21:52:36', 'public.folder'), ('vol0002', '104600', 'VA - 2013 Grammy Nominees (2013)[Mp3][www.lokotorrents.cm]', '2765542', '0', '2013-02-18 21:52:36', '2013-02-18 22:05:21', 'public.folder'), ('vol0002', '2765542', '01-The Black Keys-Lonely Boy.mp3', '2765547', '6142705', '2013-02-18 21:52:44', '2013-02-18 22:05:11', 'public.mp3'), ('vol0002', '2765542', '02-Kelly Clarkson-Stronger (What Doesnt Kill You).mp3', '2765560', '6951081', '2013-02-18 21:53:00', '2013-02-18 22:03:44', 'public.mp3'), ('vol0002', '2765542', '03-Taylor Swift-We Are Never Ever Getting Back Together.mp3', '2765548', '6487294', '2013-02-18 21:52:44', '2013-02-18 22:05:12', 'public.mp3'), ('vol0002', '2765542', '04-Gotye-Somebody That I Used To Know (Feat. Kimbra).mp3', '2765549', '6356966', '2013-02-18 21:52:44', '2013-02-18 22:05:08', 'public.mp3'), ('vol0002', '2765542', '05-Katy Perry-Wide Awake.mp3', '2765564', '7433695', '2013-02-18 21:53:10', '2013-02-18 22:04:27', 'public.mp3'), ('vol0002', '2765542', '06-Fun.-We Are Young (Feat. Janelle Monae).mp3', '2765563', '7662280', '2013-02-18 21:53:05', '2013-02-18 22:05:09', 'public.mp3'), ('vol0002', '2765542', '07-Florence And The Machine-Shake It Out.mp3', '2765556', '8142758', '2013-02-18 21:52:53', '2013-02-18 22:03:52', 'public.mp3'), ('vol0002', '2765542', '08-Pink-Try.mp3', '2765551', '7782468', '2013-02-18 21:52:48', '2013-02-18 22:04:53', 'public.mp3'), ('vol0002', '2765542', '09-Maroon 5-Payphone (Feat. Wiz Khalifa).mp3', '2765558', '7114916', '2013-02-18 21:52:53', '2013-02-18 22:04:10', 'public.mp3'), ('vol0002', '2765542', '10-Carly Rae Jepsen-Call Me Maybe.mp3', '2765550', '6265443', '2013-02-18 21:52:44', '2013-02-18 22:03:40', 'public.mp3'), ('vol0002', '2765542', '11-Miguel-Adorn.mp3', '2765544', '5803046', '2013-02-18 21:52:36', '2013-02-18 22:03:31', 'public.mp3'), ('vol0002', '2765542', '12-Ed Sheeran-The A Team.mp3', '2765554', '6178698', '2013-02-18 21:52:49', '2013-02-18 22:03:40', 'public.mp3'), ('vol0002', '2765542', '13-Hunter Hayes-Wanted.mp3', '2765552', '7720372', '2013-02-18 21:52:48', '2013-02-18 22:03:20', 'public.mp3'), ('vol0002', '2765542', '14-The Lumineers-Ho Hey.mp3', '2765553', '5134686', '2013-02-18 21:52:49', '2013-02-18 22:05:18', 'public.mp3'), ('vol0002', '2765542', '15-Alabama Shakes-Hold On.mp3', '2765561', '7169632', '2013-02-18 21:53:00', '2013-02-18 22:05:16', 'public.mp3'), ('vol0002', '2765542', '16-Mumford And Sons-I Will Wait.mp3', '2765543', '9147714', '2013-02-18 21:52:36', '2013-02-18 21:59:09', 'public.mp3'), ('vol0002', '2765542', '17-Frank Ocean-Pyramids.mp3', '2765559', '7072265', '2013-02-18 21:52:53', '2013-02-18 22:03:46', 'public.mp3'), ('vol0002', '2765542', '18-Bruce Springsteen-We Take Care Of Our Own.mp3', '2765562', '8342545', '2013-02-18 21:53:00', '2013-02-18 22:04:30', 'public.mp3'), ('vol0002', '2765542', '19-Jack White-Freedom At 21.mp3', '2765545', '5738645', '2013-02-18 21:52:36', '2013-02-18 22:05:17', 'public.mp3'), ('vol0002', '2765542', '20-Muse-Madness.mp3', '2765555', '6534399', '2013-02-18 21:52:53', '2013-02-18 21:55:27', 'public.mp3'), ('vol0002', '2765542', '21-Coldplay-Charlie Brown.mp3', '2765557', '8133501', '2013-02-18 21:52:53', '2013-02-18 22:05:11', 'public.mp3'), ('vol0002', '2765542', '22-Adele-Set Fire To The Rain (Live At The Royal Albert Hall).mp3', '2765546', '8503770', '2013-02-18 21:52:44', '2013-02-18 22:05:21', 'public.mp3'), ('vol0002', '2765542', '4UnmgK0.jpg', '2765567', '108589', '2013-02-18 21:55:14', '2013-02-18 21:55:14', 'public.jpeg');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
