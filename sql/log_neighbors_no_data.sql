-- MySQL dump 10.13  Distrib 5.7.28, for Linux (x86_64)
--
-- Host: 35.195.135.194    Database: monopoly
-- ------------------------------------------------------
-- Server version	5.7.14-google-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
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



--
-- Table structure for table `log_neighbors`
--

DROP TABLE IF EXISTS `log_neighbors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log_neighbors` (
  `epoch` bigint(20) NOT NULL,
  `currency_code` smallint(5) NOT NULL,
  `currency_pair` varchar(16) DEFAULT NULL,
  `mode` smallint(5) NOT NULL,
  `roc1` float NOT NULL DEFAULT '0',
  `rsi` float NOT NULL DEFAULT '0',
  `near_neighbors` smallint(5) NOT NULL,
  `neighbors` smallint(5) NOT NULL,
  `avg_benefit` float NOT NULL DEFAULT '0',
  `avg_benefit_weighted_space` float DEFAULT NULL,
  `avg_benefit_weighted_time` float DEFAULT NULL,
  `prob_win` float NOT NULL DEFAULT '0',
  `q5_benefit` float NOT NULL DEFAULT '0',
  `q95_benefit` float NOT NULL DEFAULT '0',
  `cheby2k` float NOT NULL DEFAULT '0',
  `cheby2k_weighted_space` float DEFAULT NULL,
  `cheby2k_weighted_time` float DEFAULT NULL,
  `worse_expected` float NOT NULL DEFAULT '0',
  `steps_mean` float NOT NULL DEFAULT '0',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `buy` tinyint(1) DEFAULT '0',
  `close` float DEFAULT '0',
  `avg_space_distance` float DEFAULT '0',
  PRIMARY KEY (`epoch`,`currency_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-12-13 11:36:02
