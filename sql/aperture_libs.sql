DROP TABLE IF EXISTS `aperture_libs`;
CREATE TABLE `aperture_libs` (
  databaseUuid char(22) COLLATE utf8_bin NOT NULL,
  external_masters_count int(8) NOT NULL ,
  file_id int(11) NOT NULL,
  `vol_id` char(8) COLLATE utf8_bin NOT NULL,
  masterCount int(8) NOT NULL ,
  versionCount int(8) NOT NULL ,
  lib_version varchar(8) NOT NULL ,
  PRIMARY KEY (`vol_id`, `file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
 

 