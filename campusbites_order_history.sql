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
-- Table structure for table `order_history`
--

DROP TABLE IF EXISTS `order_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_history` (
  `id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `token_number` varchar(50) DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_history`
--

LOCK TABLES `order_history` WRITE;
/*!40000 ALTER TABLE `order_history` DISABLE KEYS */;
INSERT INTO `order_history` VALUES (235,8,'1',450.00,'delivered','2025-08-03 21:44:54'),(236,6,'2',500.00,'delivered','2025-08-03 21:48:18'),(237,6,'3',556.00,'delivered','2025-08-03 21:49:07'),(238,6,'4',75.00,'delivered','2025-08-03 21:49:52'),(239,7,'1',20.00,'delivered','2025-08-04 14:32:43'),(240,7,'2',32.00,'delivered','2025-08-04 14:36:14'),(241,10,'1',75.00,'delivered','2025-08-14 13:59:31'),(242,9,'1',75.00,'confirmed','2025-08-14 15:16:28'),(243,9,'2',75.00,'delivered','2025-08-14 17:48:43'),(244,9,'2',12.00,'confirmed','2025-08-15 18:01:00'),(245,9,'3',50.00,'confirmed','2025-08-15 18:36:47'),(246,9,'4',59.00,'confirmed','2025-08-15 19:34:05'),(247,12,'5',28.00,'confirmed','2025-08-18 18:55:40'),(248,12,'6',103.00,'confirmed','2025-08-18 18:56:17'),(249,14,'7',50.00,'delivered','2025-08-31 11:42:17'),(250,14,'8',500.00,'delivered','2025-08-31 12:00:53'),(251,14,'9',50.00,'delivered','2025-08-31 12:59:38'),(252,14,'10',12.00,'delivered','2025-08-31 13:10:40'),(253,14,'11',59.00,'delivered','2025-08-31 13:16:35'),(254,16,'12',75.00,'delivered','2025-08-31 18:27:59'),(255,16,'13',1716.00,'delivered','2025-08-31 18:29:13');
/*!40000 ALTER TABLE `order_history` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-20 11:25:00
