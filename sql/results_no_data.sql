-- MySQL dump 10.13  Distrib 5.7.28, for Linux (x86_64)
--
-- Host: localhost    Database: monopoly
-- ------------------------------------------------------
-- Server version	5.7.28-0ubuntu0.18.04.4

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

--
-- Table structure for table `results`
--

DROP TABLE IF EXISTS `results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `results` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `m_hash` varchar(64) NOT NULL,
  `m_currency_pair` varchar(64) NOT NULL,
  `m_always_win` int(11) DEFAULT '0',
  `m_min_rate` float DEFAULT '0',
  `m_init_amount` float DEFAULT '0',
  `m_max_amount` float DEFAULT '0',
  `m_min_amount` float DEFAULT '0',
  `m_sos_amount` float DEFAULT '0',
  `m_sos_rate` float DEFAULT '0',
  `m_mode` int(11) DEFAULT '0',
  `m_func` int(11) DEFAULT '0',
  `m_r` float DEFAULT '0',
  `m_avg` float DEFAULT '0',
  `m_min_roc1` float DEFAULT '0',
  `m_max_roc1` float DEFAULT '0',
  `r_time_sim` float DEFAULT '0',
  `r_total_benefit` float DEFAULT '0',
  `r_max_benefit` float DEFAULT '0',
  `r_mean_benefit` float DEFAULT '0',
  `r_max_benefit_rate` float DEFAULT '0',
  `r_mean_benefit_rate` float DEFAULT '0',
  `r_max_inversion` float DEFAULT '0',
  `r_mean_inversion` float DEFAULT '0',
  `r_median_inversion` float DEFAULT '0',
  `r_num_purchases` float DEFAULT '0',
  `r_num_repurchases` float DEFAULT '0',
  `r_repurchase_rate` float DEFAULT '0',
  `r_median_repurchases` float DEFAULT '0',
  `r_mean_repurchases` float DEFAULT '0',
  `r_max_repurchases` float DEFAULT '0',
  `r_num_games` float DEFAULT '0',
  `r_num_sos_games` float DEFAULT '0',
  `r_sos_rate` float DEFAULT '0',
  `r_base_balance` float DEFAULT '0',
  `r_quote_balance` float DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `r_total_benefit` (`r_total_benefit`),
  KEY `m_hash` (`m_hash`),
  KEY `r_sos_rate` (`r_sos_rate`),
  KEY `r_repurchase_rate` (`r_repurchase_rate`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-12-19  7:27:12
