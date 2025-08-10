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
-- Table structure for table `admin_users`
--

DROP TABLE IF EXISTS `admin_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_users`
--

LOCK TABLES `admin_users` WRITE;
/*!40000 ALTER TABLE `admin_users` DISABLE KEYS */;
INSERT INTO `admin_users` VALUES (1,'midhu','scrypt:32768:8:1$tUwm7j8LIhSCDY22$103c1d41f39636cad70ede080c3a1147bc1789663e2198b3a1ab2a36fdac20d88f7455ed67d79d84d47d2b5cf7908e5be1de992a0bdb12dcbad06f6ec46736e1'),(2,'keethu','scrypt:32768:8:1$1LMMyrkVLfcfruEE$c30f4b4c835ae220760604db9d2d3283cd98ddfdc09cf09544776a02eed67c23827f4d8ad017fa615dd503f5b8af4240c04d5536d5c2ecd17876318dabf7be0a'),(3,'paru','scrypt:32768:8:1$3VIOq9j12DBj1qUk$ba4e90f19996576fd8edd92ad6cabca608ae942167e67c0a0d052f8eee4448facf65fb54690d092dad67cb5e35253079203b11c44b826a9f01388a889226e467'),(4,'kuru','scrypt:32768:8:1$p95feBYWkZTv8vx1$d3a42429e5dec62288b5ce85ef875c84357c15a1df975ca4521a726ffd3e1e0782129f1bfdcaaf622525f599a3ab3efe931b2c033a109d34b5462aa80922e86a');
/*!40000 ALTER TABLE `admin_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `food_id` int DEFAULT NULL,
  `quantity` int DEFAULT '1',
  `added_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (62,6,13,1,'2025-08-03 16:17:59'),(63,6,6,2,'2025-08-03 16:18:58'),(64,6,3,1,'2025-08-03 16:19:44'),(65,1,4,4,'2025-08-03 16:23:58'),(66,7,14,1,'2025-08-04 09:01:39'),(67,7,5,1,'2025-08-04 09:04:49'),(68,6,5,3,'2025-08-04 09:35:14');
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`id`),
  KEY `food_id` (`food_id`),
  CONSTRAINT `daily_menu_ibfk_1` FOREIGN KEY (`food_id`) REFERENCES `food_items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_menu`
--

LOCK TABLES `daily_menu` WRITE;
/*!40000 ALTER TABLE `daily_menu` DISABLE KEYS */;
INSERT INTO `daily_menu` VALUES (7,3,'2025-07-16','breakfast','11:27:00','23:56:00',40),(8,4,'2025-07-16','breakfast','11:27:00','23:56:00',40),(24,3,'2025-07-17','breakfast','21:46:00','23:56:00',55),(25,4,'2025-07-17','breakfast','21:46:00','23:56:00',55),(26,5,'2025-07-17','breakfast','21:45:00','23:55:00',54),(32,3,'2025-07-18','breakfast','14:09:00','20:09:00',21),(33,5,'2025-07-18','breakfast','15:48:00','21:48:00',39),(41,3,'2025-07-19','breakfast','09:40:00','00:46:00',10),(42,4,'2025-07-19','breakfast','09:40:00','00:46:00',25),(43,5,'2025-07-19','breakfast','09:41:00','00:41:00',40),(46,3,'2025-07-20','breakfast','08:00:00','23:05:00',43),(47,4,'2025-07-20','breakfast','08:00:00','23:05:00',58),(48,6,'2025-07-20','breakfast','08:00:00','23:05:00',27),(49,7,'2025-07-20','breakfast','08:00:00','23:05:00',49),(50,8,'2025-07-20','breakfast','08:00:00','23:05:00',49),(51,5,'2025-07-20','breakfast','12:00:00','21:10:00',57),(52,9,'2025-07-20','breakfast','08:00:00','23:05:00',10),(53,10,'2025-07-20','breakfast','08:00:00','23:05:00',10),(54,3,'2025-07-21','breakfast','08:00:00','17:00:00',90),(55,8,'2025-07-21','breakfast','08:00:00','17:00:00',10),(56,10,'2025-07-21','breakfast','08:00:00','17:00:00',10),(57,7,'2025-07-21','breakfast','08:00:00','17:00:00',11),(58,4,'2025-07-21','breakfast','08:00:00','17:00:00',900),(59,3,'2025-07-22','breakfast','08:00:00','23:00:00',48),(60,4,'2025-07-22','breakfast','08:00:00','23:00:00',50),(61,6,'2025-07-22','breakfast','08:00:00','23:00:00',50),(62,7,'2025-07-22','breakfast','08:00:00','23:00:00',50),(63,8,'2025-07-22','breakfast','08:00:00','23:00:00',50),(64,9,'2025-07-22','breakfast','08:00:00','23:00:00',50),(65,10,'2025-07-22','breakfast','08:00:00','23:00:00',50),(66,5,'2025-07-22','breakfast','10:05:00','22:00:00',50),(68,3,'2025-07-24','breakfast','08:00:00','21:00:00',3),(69,4,'2025-07-24','breakfast','08:00:00','21:00:00',7),(70,6,'2025-07-24','breakfast','08:00:00','21:00:00',8),(71,7,'2025-07-24','breakfast','08:00:00','21:00:00',7),(72,8,'2025-07-24','breakfast','08:00:00','21:00:00',10),(73,9,'2025-07-24','breakfast','08:00:00','21:00:00',9),(74,10,'2025-07-24','breakfast','08:00:00','21:00:00',8),(75,5,'2025-07-24','breakfast','08:00:00','21:00:00',7),(77,3,'2025-07-25','breakfast','08:00:00','11:00:00',10),(78,6,'2025-07-25','breakfast','08:00:00','11:00:00',10),(79,7,'2025-07-25','breakfast','08:00:00','11:00:00',10),(80,8,'2025-07-25','breakfast','08:00:00','11:00:00',10),(81,5,'2025-07-25','breakfast','12:00:00','15:00:00',10),(83,3,'2025-07-28','breakfast','08:00:00','23:00:00',9),(84,4,'2025-07-28','breakfast','08:00:00','23:00:00',8),(85,6,'2025-07-28','breakfast','08:00:00','23:00:00',10),(86,7,'2025-07-28','breakfast','08:00:00','23:00:00',10),(87,8,'2025-07-28','breakfast','08:00:00','23:00:00',10),(88,9,'2025-07-28','breakfast','08:00:00','23:00:00',10),(89,10,'2025-07-28','breakfast','08:00:00','23:00:00',10),(90,12,'2025-07-28','breakfast','08:00:00','23:00:00',9),(91,5,'2025-07-28','breakfast','09:00:00','23:30:00',10),(96,3,'2025-07-29','breakfast','08:00:00','17:00:00',9),(97,4,'2025-07-29','breakfast','08:00:00','17:00:00',10),(98,6,'2025-07-29','breakfast','08:00:00','17:00:00',10),(99,7,'2025-07-29','breakfast','08:00:00','17:00:00',10),(100,5,'2025-07-29','breakfast','12:00:00','18:00:00',10),(101,13,'2025-07-29','breakfast','12:00:00','18:00:00',10),(112,3,'2025-07-30','breakfast','08:00:00','21:00:00',9),(113,6,'2025-07-30','breakfast','08:00:00','21:00:00',10),(114,13,'2025-07-30','breakfast','12:00:00','20:00:00',9),(115,4,'2025-07-30','breakfast','08:00:00','21:00:00',9),(116,7,'2025-07-30','breakfast','08:00:00','21:00:00',10),(117,12,'2025-07-30','breakfast','08:00:00','21:00:00',10),(118,3,'2025-07-31','breakfast','08:00:00','19:00:00',5),(119,4,'2025-07-31','breakfast','08:00:00','19:00:00',9),(120,6,'2025-07-31','breakfast','08:00:00','19:00:00',9),(121,7,'2025-07-31','breakfast','08:00:00','19:00:00',9),(122,8,'2025-07-31','breakfast','08:00:00','19:00:00',10),(123,9,'2025-07-31','breakfast','08:00:00','19:00:00',9),(124,10,'2025-07-31','breakfast','08:00:00','19:00:00',10),(125,12,'2025-07-31','breakfast','08:00:00','19:00:00',10),(126,5,'2025-07-31','breakfast','12:00:00','19:00:00',10),(127,13,'2025-07-31','breakfast','12:00:00','19:00:00',9),(128,3,'2025-08-01','breakfast','08:00:00','16:33:00',10),(129,4,'2025-08-01','breakfast','08:00:00','16:33:00',10),(130,7,'2025-08-01','breakfast','08:00:00','16:33:00',10),(131,8,'2025-08-01','breakfast','08:00:00','16:33:00',10),(132,9,'2025-08-01','breakfast','08:00:00','16:33:00',10),(133,10,'2025-08-01','breakfast','08:00:00','16:33:00',10),(134,12,'2025-08-01','breakfast','08:00:00','16:33:00',10),(135,5,'2025-08-01','breakfast','12:00:00','18:30:00',10),(136,13,'2025-08-01','breakfast','12:00:00','18:30:00',10),(137,3,'2025-08-03','breakfast','08:00:00','23:00:00',0),(138,4,'2025-08-03','breakfast','08:00:00','23:00:00',10),(139,6,'2025-08-03','breakfast','08:00:00','23:00:00',8),(140,7,'2025-08-03','breakfast','08:00:00','23:00:00',9),(141,8,'2025-08-03','breakfast','08:00:00','23:00:00',10),(142,9,'2025-08-03','breakfast','08:00:00','23:00:00',10),(143,10,'2025-08-03','breakfast','08:00:00','23:00:00',10),(144,12,'2025-08-03','breakfast','08:00:00','23:00:00',10),(145,5,'2025-08-03','breakfast','12:00:00','23:00:00',10),(146,13,'2025-08-03','breakfast','12:00:00','23:00:00',8),(147,14,'2025-08-03','breakfast','12:00:00','23:00:00',10),(148,5,'2025-08-04','breakfast','12:00:00','21:00:00',9),(149,13,'2025-08-04','breakfast','12:00:00','21:00:00',10),(150,14,'2025-08-04','breakfast','12:00:00','21:00:00',8);
/*!40000 ALTER TABLE `daily_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `food_items`
--

DROP TABLE IF EXISTS `food_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `food_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `meal_type` enum('breakfast','lunch') DEFAULT NULL,
  `available` tinyint(1) DEFAULT '1',
  `stock` int DEFAULT '0',
  `about` text,
  `category` enum('breakfast','lunch') DEFAULT 'breakfast',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `food_items`
--

LOCK TABLES `food_items` WRITE;
/*!40000 ALTER TABLE `food_items` DISABLE KEYS */;
INSERT INTO `food_items` VALUES (3,'Chicken Biriyani',75.00,'chicken_biriyani_1753029774.webp','lunch',1,0,'i am a junk food','breakfast'),(4,'Veg Meals',50.00,'veg_meals_1753029797.webp','lunch',1,0,'i am a vegan broo....','breakfast'),(5,'chappathii',12.00,'chappathii_1753029826.webp',NULL,1,10,'shbuybfyubwuy','lunch'),(6,'bababa pufs',28.00,'bababa_pufs_1753029844.webp',NULL,1,10,'Hello there i am pufs ','breakfast'),(7,'Dosa',12.00,'dosa_1753029859.webp',NULL,1,10,'Dosa dosa dosa','breakfast'),(8,'Idli sambar',59.00,'idli_sambar_1753701382.webp',NULL,1,10,'Vssjsnsbsb','breakfast'),(9,'pani puriii',35.00,'pani_puriii_1753029890.webp',NULL,1,10,'blah blah blha','breakfast'),(10,'porotta',12.00,'porotta_1753029901.webp',NULL,1,10,'ghhg','breakfast'),(12,'berger',70.00,'berger.webp',NULL,1,10,'yummy','breakfast'),(13,'kozhi tikka 65',500.00,'kozhi_tikka_65.webp',NULL,1,10,'i am yummyyyyy','lunch'),(14,'Kaytha chakka',20.00,'kaytha_chakka.webp',NULL,1,10,'Very very tasty','lunch');
/*!40000 ALTER TABLE `food_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `is_admin_notification` tinyint(1) DEFAULT '0',
  `message` varchar(255) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `related_id` int DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,NULL,1,'New Order! Token #49 by None.','new_order',128,1,'2025-07-20 14:14:35'),(2,NULL,1,'New Order! Token #50 by None.','new_order',129,1,'2025-07-20 14:14:35'),(3,NULL,1,'New Order! Token #51 by None.','new_order',130,1,'2025-07-20 14:15:07'),(4,NULL,1,'New Order! Token #52 by None.','new_order',131,1,'2025-07-20 14:16:13'),(5,NULL,1,'New Order! Token #53 by None.','new_order',132,1,'2025-07-20 14:18:58'),(6,NULL,1,'New Order! Token #54 by None.','new_order',133,1,'2025-07-20 14:20:17'),(7,NULL,1,'New Order! Token #55 by None.','new_order',134,1,'2025-07-20 14:20:17'),(8,NULL,1,'New Order! Token #56 by None.','new_order',135,1,'2025-07-20 14:20:36'),(9,NULL,1,'New Order! Token #57 by None.','new_order',136,1,'2025-07-20 14:20:55'),(10,NULL,1,'New Order! Token #58 by None.','new_order',137,1,'2025-07-20 14:22:00'),(11,NULL,1,'New Order! Token #59 by None.','new_order',138,1,'2025-07-20 14:23:06'),(12,NULL,1,'New Order! Token #60 by None.','new_order',139,1,'2025-07-20 14:49:19'),(13,NULL,1,'New Order! Token #61 by None.','new_order',140,1,'2025-07-20 14:49:19'),(14,NULL,1,'New Order! Token #62 by None.','new_order',141,1,'2025-07-20 15:26:20'),(15,NULL,1,'New Order! Token #63 by None.','new_order',142,1,'2025-07-20 15:37:56'),(16,NULL,1,'New Cart Order! Token #64 by None.','new_order',143,1,'2025-07-20 15:39:54'),(17,NULL,1,'New Order! Token #65 by None.','new_order',144,1,'2025-07-20 16:40:09'),(18,NULL,1,'New Order! Token #66 by None.','new_order',145,1,'2025-07-20 16:40:47'),(19,NULL,1,'New Order! Token #67 by Joel Mathew.','new_order',146,1,'2025-07-21 09:44:18'),(20,NULL,1,'New Order! Token #68 by Joel Mathew.','new_order',147,1,'2025-07-21 09:45:16'),(21,NULL,1,'New Order! Token #69 by Joel Mathew.','new_order',148,1,'2025-07-21 09:47:53'),(22,NULL,1,'New Order! Token #70 by None.','new_order',149,1,'2025-07-22 12:21:19'),(23,NULL,1,'New Order! Token #71 by None.','new_order',150,1,'2025-07-22 15:18:57'),(24,NULL,1,'New Order! Token #72 by None.','new_order',151,1,'2025-07-22 15:43:25'),(25,NULL,1,'New Order! Token #73 by None.','new_order',152,1,'2025-07-24 04:47:43'),(26,NULL,1,'New Order! Token #74 by None.','new_order',153,1,'2025-07-24 04:48:39'),(27,NULL,1,'New Cart Order! Token #75 by None.','new_order',154,1,'2025-07-24 04:48:57'),(28,NULL,1,'New Order! Token #76 by None.','new_order',155,1,'2025-07-24 04:54:34'),(29,NULL,1,'New Order! Token #77 by None.','new_order',156,1,'2025-07-24 04:54:34'),(30,NULL,1,'New Order! Token #78 by None.','new_order',157,1,'2025-07-24 05:39:50'),(31,NULL,1,'New Order! Token #79 by None.','new_order',158,1,'2025-07-24 05:42:54'),(32,NULL,1,'New Order! Token #80 by None.','new_order',159,1,'2025-07-24 05:42:54'),(33,NULL,1,'New Cart Order! Token #90 by None.','new_order',169,1,'2025-07-24 05:50:50'),(34,NULL,1,'New Order! Token #1 by None.','new_order',170,1,'2025-07-24 06:13:22'),(35,NULL,1,'New Order! Token #1 by None.','new_order',171,1,'2025-07-24 06:39:05'),(36,NULL,1,'New Cart Order! Token #2 by None.','new_order',172,1,'2025-07-24 06:39:15'),(37,NULL,1,'New Cart Order! Token #3 by None.','new_order',173,1,'2025-07-24 06:39:46'),(38,NULL,1,'New Cart Order! Token #4 by None.','new_order',174,1,'2025-07-24 07:33:16'),(39,NULL,1,'New Order! Token #5 by None.','new_order',175,1,'2025-07-24 07:44:21'),(40,NULL,1,'New Order! Token #6 by None.','new_order',176,1,'2025-07-24 07:47:50'),(41,NULL,1,'New Order! Token #7 by None.','new_order',177,1,'2025-07-24 13:27:12'),(42,NULL,1,'New Order! Token #8 by Joel Mathew.','new_order',178,1,'2025-07-24 14:32:17'),(43,NULL,1,'New Order! Token #9 by Joel Mathew.','new_order',179,1,'2025-07-24 14:34:35'),(44,NULL,1,'New Cart Order! Token #10 by midhun s.','new_order',180,1,'2025-07-24 15:14:58'),(45,NULL,1,'New Order! Token #1 by midhun s.','new_order',195,1,'2025-07-28 10:20:50'),(46,NULL,1,'New Order! Token #2 by midhun s.','new_order',196,1,'2025-07-28 10:22:14'),(47,NULL,1,'New Order! Token #3 by midhun s.','new_order',197,1,'2025-07-28 10:22:14'),(48,NULL,1,'New Order! Token #4 by midhun s.','new_order',198,1,'2025-07-28 10:22:44'),(49,NULL,1,'New Order! Token #5 by midhun s.','new_order',199,1,'2025-07-28 10:35:00'),(50,NULL,1,'New Order! Token #1 by midhun s.','new_order',205,1,'2025-07-29 09:32:21'),(51,NULL,1,'New Order! Token #2 by keerthana v.','new_order',206,1,'2025-07-29 09:48:08'),(52,NULL,1,'New Order! Token #3 by keerthana v.','new_order',207,1,'2025-07-29 09:54:25'),(53,NULL,1,'New Order! Token #4 by midhun s.','new_order',208,1,'2025-07-29 09:57:39'),(54,NULL,1,'New Order! Token #2 by midhun s.','new_order',209,1,'2025-07-30 04:33:31'),(55,NULL,1,'New Order! Token #6 by keerthana v.','new_order',210,1,'2025-07-30 04:41:23'),(56,NULL,1,'New Order! Token #7 by keerthana v.','new_order',211,1,'2025-07-30 08:56:46'),(57,NULL,1,'New Order! Token #8 by keerthana v.','new_order',212,1,'2025-07-30 09:00:46'),(58,7,0,'Your order #15 is out for delivery!','order_delivered',226,0,'2025-07-31 10:55:55'),(59,7,0,'Your order #1 is out for delivery!','order_delivered',227,0,'2025-07-31 11:13:05'),(64,7,0,'Your order #1 is out for delivery!','order_delivered',232,0,'2025-08-03 14:01:12'),(65,7,0,'Your order #4 is out for delivery!','order_delivered',233,0,'2025-08-03 14:15:30'),(76,6,0,'Your order #4 is out for delivery!','order_delivered',238,0,'2025-08-03 16:21:11'),(77,6,0,'Your order #3 is out for delivery!','order_delivered',237,0,'2025-08-03 16:21:16'),(78,6,0,'Your order #2 is out for delivery!','order_delivered',236,0,'2025-08-03 16:21:19'),(79,8,0,'Your order #1 is out for delivery!','order_delivered',235,0,'2025-08-03 16:25:09'),(82,7,0,'Your order #1 is out for delivery!','order_delivered',239,0,'2025-08-04 09:03:46'),(85,7,0,'Your order #2 is out for delivery!','order_delivered',240,0,'2025-08-04 09:06:55');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_history`
--

LOCK TABLES `order_history` WRITE;
/*!40000 ALTER TABLE `order_history` DISABLE KEYS */;
INSERT INTO `order_history` VALUES (235,8,'1',450.00,'delivered','2025-08-03 21:44:54'),(236,6,'2',500.00,'delivered','2025-08-03 21:48:18'),(237,6,'3',556.00,'delivered','2025-08-03 21:49:07'),(238,6,'4',75.00,'delivered','2025-08-03 21:49:52'),(239,7,'1',20.00,'delivered','2025-08-04 14:32:43'),(240,7,'2',32.00,'delivered','2025-08-04 14:36:14');
/*!40000 ALTER TABLE `order_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `food_id` int DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=195 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (187,235,3,6,75.00),(188,236,13,1,500.00),(189,237,13,1,500.00),(190,237,6,2,28.00),(191,238,3,1,75.00),(192,239,14,1,20.00),(193,240,14,1,20.00),(194,240,5,1,12.00);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `token_number` int NOT NULL,
  `payment_status` varchar(50) DEFAULT 'created',
  `razorpay_order_id` varchar(255) DEFAULT NULL,
  `razorpay_payment_id` varchar(255) DEFAULT NULL,
  `razorpay_signature` varchar(255) DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT 'cash_on_delivery',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_number` (`token_number`),
  KEY `idx_token` (`token_number`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=241 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `uncollected_tokens`
--

DROP TABLE IF EXISTS `uncollected_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `uncollected_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `token_number` int NOT NULL,
  `order_id` int NOT NULL,
  `order_date` datetime NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_number` (`token_number`,`order_date`),
  UNIQUE KEY `idx_token_number_uncollected` (`token_number`),
  KEY `order_id` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=344 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uncollected_tokens`
--

LOCK TABLES `uncollected_tokens` WRITE;
/*!40000 ALTER TABLE `uncollected_tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `uncollected_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admission_number` varchar(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `dob` date NOT NULL,
  `role` enum('student','staff') DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'ST001','Joel Mathew','2003-04-12','student'),(2,'ST002','Maya Joseph','2002-11-20','student'),(3,'joel','joel k','2005-08-08','staff'),(6,'paru','keerthana v','2006-03-28',NULL),(7,'midhu','midhun s','2006-02-22',NULL),(8,'keethu','keerthana s','2006-01-04',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-05 17:28:32
