CREATE DATABASE  IF NOT EXISTS `campusbites` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `campusbites`;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (62,6,13,1,'2025-08-03 16:17:59'),(63,6,6,2,'2025-08-03 16:18:58'),(64,6,3,1,'2025-08-03 16:19:44'),(65,1,4,4,'2025-08-03 16:23:58'),(66,7,14,1,'2025-08-04 09:01:39'),(67,7,5,1,'2025-08-04 09:04:49'),(68,6,5,3,'2025-08-04 09:35:14'),(69,12,3,1,'2025-08-18 13:20:41'),(70,12,6,1,'2025-08-18 13:20:57'),(71,14,6,1,'2025-08-31 06:10:52'),(72,14,7,1,'2025-08-31 06:10:59');
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
  `days` set('mon','tue','wed','thu','fri','sat','sun') NOT NULL DEFAULT 'mon,tue,wed,thu,fri',
  `default_start_time` time NOT NULL DEFAULT '09:00:00',
  `default_end_time` time NOT NULL DEFAULT '16:00:00',
  `default_stock` int NOT NULL DEFAULT '0',
  `default_breakfast_start` time DEFAULT '08:00:00',
  `default_breakfast_end` time DEFAULT '11:00:00',
  `default_lunch_start` time DEFAULT '12:00:00',
  `default_lunch_end` time DEFAULT '15:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `food_items`
--

LOCK TABLES `food_items` WRITE;
/*!40000 ALTER TABLE `food_items` DISABLE KEYS */;
INSERT INTO `food_items` VALUES (3,'Chicken Biriyani',75.00,'chicken_biriyani_1753029774.webp','lunch',1,25,'i am a junk food','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,'08:00:00','23:00:00',NULL,'23:00:00'),(4,'Veg Meals',50.00,'veg_meals_1753029797.webp','lunch',1,25,'i am a vegan broo....','lunch','mon,tue,wed,thu,fri,sun','05:07:00','23:00:00',25,'08:00:00','23:00:00','05:07:00','23:00:00'),(5,'chappathii',12.00,'chappathii_1753029826.webp',NULL,1,10,'shbuybfyubwuy','lunch','sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(6,'bababa pufs',28.00,'bababa_pufs_1753029844.webp',NULL,1,10,'Hello there i am pufs ...','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(7,'Dosa',12.00,'dosa_1753029859.webp',NULL,1,10,'Dosa dosa dosa','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(8,'Idli sambar',59.00,'idli_sambar_1753701382.webp',NULL,1,10,'Vssjsnsbsb','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(10,'porotta',12.00,'porotta_1753029901.webp',NULL,1,10,'ghhg','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(12,'berger',70.00,'berger.webp',NULL,1,10,'yummy','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',20,'08:00:00','23:00:00','08:00:00','23:00:00'),(13,'kozhi tikka 65',500.00,'kozhi_tikka_65.webp',NULL,1,25,'i am yummyyyyy','lunch','mon,tue,wed,thu,fri,sat,sun','12:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(14,'Kaytha chakka',20.00,'kaytha_chakka.webp',NULL,1,25,'Very very tasty','lunch','mon,tue,wed,thu,fri,sat,sun','12:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(15,'keethuuuuu',1.00,'keethuuuuu.webp',NULL,1,25,'poison','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(16,'paruu',1.00,'paruu.webp',NULL,1,25,'poison','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(17,'midhun',7.00,'midhun_1758195687.webp','breakfast',1,7,'helo there eat me.....','breakfast','mon,tue,wed,thu,fri,sat,sun','06:00:00','22:58:00',7,'06:00:00','22:58:00','12:00:00','15:00:00');
/*!40000 ALTER TABLE `food_items` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=218 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (187,235,3,6,75.00),(188,236,13,1,500.00),(189,237,13,1,500.00),(190,237,6,2,28.00),(191,238,3,1,75.00),(192,239,14,1,20.00),(193,240,14,1,20.00),(194,240,5,1,12.00),(195,241,3,1,75.00),(196,242,3,1,75.00),(197,243,3,1,75.00),(198,244,7,1,12.00),(199,245,4,1,50.00),(200,246,8,1,59.00),(201,247,6,1,28.00),(202,248,3,1,75.00),(203,248,6,1,28.00),(204,249,4,1,50.00),(205,250,4,10,50.00),(206,251,4,1,50.00),(207,252,7,1,12.00),(208,253,8,1,59.00),(209,254,3,1,75.00),(210,255,8,19,59.00),(211,255,9,15,35.00),(212,255,12,1,70.00),(213,256,6,1,28.00),(214,257,3,1,75.00),(215,258,13,1,500.00),(216,259,7,1,12.00),(217,259,13,1,500.00);
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
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
) ENGINE=InnoDB AUTO_INCREMENT=260 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (256,16,28.00,'confirmed','2025-09-18 17:05:43',1,'paid','order_RJ3A18ne82iAP0','pay_RJ3AJohi7CXPut',NULL,'razorpay'),(257,16,75.00,'confirmed','2025-09-18 18:23:04',2,'paid','order_RJ4TmqlyxJuTFU','pay_RJ4U1fgQwQ3YpT',NULL,'razorpay'),(258,16,500.00,'confirmed','2025-09-18 18:24:12',3,'paid','order_RJ4V40au8U7Dbq','pay_RJ4VDLRqQNjzJe',NULL,'razorpay'),(259,16,512.00,'confirmed','2025-09-18 18:30:03',4,'paid','order_RJ4bBd4OCTM3KO','pay_RJ4bOsKov9r5HI',NULL,'razorpay');
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
) ENGINE=InnoDB AUTO_INCREMENT=350 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `role` enum('student','staff') DEFAULT 'student',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (16,'MIDHUN SIBY ','midhunsiby5@gmail.com','8590488423',NULL,'student'),(17,'MIDHUN SIBY ','midhunsiby3028@gmail.com','8590488423',NULL,'student');
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

-- Dump completed on 2025-09-20 11:37:13
