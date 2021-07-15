-- MySQL dump 10.13  Distrib 8.0.22, for Win64 (x86_64)
--
-- Host: -    Database: material_database_test
-- ------------------------------------------------------
-- Server version	8.0.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '';

--
-- Table structure for table `element_defects`
--

DROP TABLE IF EXISTS `element_defects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `element_defects` (
  `uuid` binary(16) NOT NULL,
  `element_uuid` binary(16) NOT NULL,
  `fid` smallint NOT NULL,
  `u` float NOT NULL,
  `v` float NOT NULL,
  `defect_type` enum('nail','knot_live','knot_dead') DEFAULT NULL,
  PRIMARY KEY (`uuid`),
  KEY `element_uuid` (`element_uuid`),
  CONSTRAINT `e_uuid` FOREIGN KEY (`element_uuid`) REFERENCES `elements` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `element_photo_textures`
--

DROP TABLE IF EXISTS `element_photo_textures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `element_photo_textures` (
  `uuid` binary(16) NOT NULL,
  `tex_id` smallint unsigned NOT NULL,
  `data` mediumblob,
  PRIMARY KEY (`uuid`,`tex_id`),
  CONSTRAINT `uuid` FOREIGN KEY (`uuid`) REFERENCES `elements` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `elements`
--

DROP TABLE IF EXISTS `elements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elements` (
  `uuid` binary(16) NOT NULL,
  `site_uuid` binary(16) DEFAULT NULL,
  `x` float DEFAULT NULL,
  `y` float DEFAULT NULL,
  `z` float DEFAULT NULL,
  `quality` float DEFAULT NULL,
  `species` varchar(32) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `ts_create` timestamp(3) NULL DEFAULT CURRENT_TIMESTAMP(3),
  `ts_update` timestamp(3) NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `mass` float DEFAULT NULL,
  `storage_bucket` int DEFAULT NULL,
  PRIMARY KEY (`uuid`),
  KEY `uuid_idx` (`site_uuid`),
  CONSTRAINT `site_uuid_fk` FOREIGN KEY (`site_uuid`) REFERENCES `sites` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `real_elements`
--

DROP TABLE IF EXISTS `real_elements`;
/*!50001 DROP VIEW IF EXISTS `real_elements`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `real_elements` AS SELECT 
 1 AS `element_uuid`,
 1 AS `x`,
 1 AS `y`,
 1 AS `z`,
 1 AS `quality`,
 1 AS `species`,
 1 AS `lat`,
 1 AS `lng`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `site_elements`
--

DROP TABLE IF EXISTS `site_elements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `site_elements` (
  `uuid` binary(16) NOT NULL,
  `site_uuid` binary(16) DEFAULT NULL,
  `local_id` int DEFAULT NULL,
  `type` enum('beam','column','column_rect','column_round','slab','wall') DEFAULT NULL,
  `material` enum('brick','concrete','metal','wood','none') DEFAULT NULL,
  `x` float DEFAULT NULL,
  `y` float DEFAULT NULL,
  `z` float DEFAULT NULL,
  `w` float DEFAULT NULL,
  `l` float DEFAULT NULL,
  `h` float DEFAULT NULL,
  `r` float DEFAULT NULL,
  `inclination` float DEFAULT '0',
  PRIMARY KEY (`uuid`),
  KEY `site_uuid_idx` (`site_uuid`),
  CONSTRAINT `site_uuid` FOREIGN KEY (`site_uuid`) REFERENCES `sites` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sites`
--

DROP TABLE IF EXISTS `sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sites` (
  `uuid` binary(16) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `visible` tinyint DEFAULT '1',
  PRIMARY KEY (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wood_data`
--

DROP TABLE IF EXISTS `wood_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wood_data` (
  `id` int NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `density` float DEFAULT NULL,
  `fiber_stress` float DEFAULT NULL,
  `E` float DEFAULT NULL,
  `strength_compressive` float DEFAULT NULL,
  `strength_shear` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `real_elements`
--

/*!50001 DROP VIEW IF EXISTS `real_elements`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mattjosephgordon`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `real_elements` AS select bin_to_uuid(`elements`.`uuid`) AS `element_uuid`,`elements`.`x` AS `x`,`elements`.`y` AS `y`,`elements`.`z` AS `z`,`elements`.`quality` AS `quality`,`elements`.`species` AS `species`,`elements`.`lat` AS `lat`,`elements`.`lng` AS `lng` from (`elements` join `sites`) where ((`elements`.`site_uuid` = `sites`.`uuid`) and (`sites`.`name` <> 'synthetic')) order by `elements`.`storage_bucket` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-07-15 18:22:25
