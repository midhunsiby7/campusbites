-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: campusbites
-- ------------------------------------------------------
-- Server version	8.0.42

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

--
-- Table structure for table `daily_menu`
--

DROP TABLE IF EXISTS `daily_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_menu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `food_id` int NOT NULL,
  `available_date` date NOT NULL,
  `category` enum('breakfast','lunch') NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `stock` int DEFAULT '0',
  `availability` enum('available','reserved','not_available') DEFAULT 'available',
  `reserved_by` int DEFAULT NULL,
  `reserved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_food_date` (`food_id`,`available_date`),
  CONSTRAINT `daily_menu_ibfk_1` FOREIGN KEY (`food_id`) REFERENCES `food_items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=389 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_menu`
--

LOCK TABLES `daily_menu` WRITE;
/*!40000 ALTER TABLE `daily_menu` DISABLE KEYS */;
INSERT INTO `daily_menu` VALUES (377,3,'2025-09-18','breakfast','08:00:00','23:00:00',24,'available',NULL,NULL),(378,4,'2025-09-18','lunch','05:07:00','23:00:00',25,'available',NULL,NULL),(379,6,'2025-09-18','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(380,7,'2025-09-18','breakfast','08:00:00','23:00:00',24,'available',NULL,NULL),(381,8,'2025-09-18','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(382,10,'2025-09-18','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(383,12,'2025-09-18','breakfast','08:00:00','23:00:00',20,'available',NULL,NULL),(384,13,'2025-09-18','lunch','12:00:00','23:00:00',23,'available',NULL,NULL),(385,14,'2025-09-18','lunch','12:00:00','23:00:00',25,'available',NULL,NULL),(386,15,'2025-09-18','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(387,16,'2025-09-18','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(388,17,'2025-09-18','breakfast','06:00:00','22:58:00',7,'available',NULL,NULL);
/*!40000 ALTER TABLE `daily_menu` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-20 11:24:59
