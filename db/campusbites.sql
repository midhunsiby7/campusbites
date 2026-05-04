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
use campusbites;
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
INSERT INTO `admin_users` VALUES (1,'midhun','scrypt:32768:8:1$bQjH353igYELfZVd$5ccb90ea090c2695185e75ab617194fc434b238614e79884388e304d31e709fdbab0cddad6c241bd35c94d42cd17c8c9d4f15e65ee58ccc347a8b2aeab49f973'),(2,'keerthi','scrypt:32768:8:1$ptBvHE40BrHgvJGg$2f3252f7cc5a22be5694ca4977338a25348931b28130d7b917bd974e0840f005b0a87744a25a59a04f71c61fad0fabaefe6c14ca8f704367ffd9fddd46368cc6'),(3,'paru','scrypt:32768:8:1$i21KtTqZCewYGNmm$c3ffeaa852b51d696596f9dc70f83c124b7470e9a2d945a6471b9f9de08a83d95e8787b9415cebf9d6708a0acbb84d0fe2a988c9bad6c62bdab18909032ab287');
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
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (99,22,7,1,'2026-04-11 16:47:47'),(100,17,18,1,'2026-04-24 07:13:57');
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `checkout_token_holds`
--

DROP TABLE IF EXISTS `checkout_token_holds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `checkout_token_holds` (
  `token_number` int NOT NULL,
  `razorpay_order_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`token_number`),
  UNIQUE KEY `uniq_rz_order` (`razorpay_order_id`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `checkout_token_holds`
--

LOCK TABLES `checkout_token_holds` WRITE;
/*!40000 ALTER TABLE `checkout_token_holds` DISABLE KEYS */;
INSERT INTO `checkout_token_holds` VALUES (1899,'order_ShFEOclF66Qu6c',17,'2026-04-24 07:18:09'),(1925,'order_ShFFYCegBeYp3O',17,'2026-04-24 07:19:15'),(3411,'order_ShFHFjAuH8dAwP',17,'2026-04-24 07:20:51');
/*!40000 ALTER TABLE `checkout_token_holds` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=592 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_menu`
--

LOCK TABLES `daily_menu` WRITE;
/*!40000 ALTER TABLE `daily_menu` DISABLE KEYS */;
INSERT INTO `daily_menu` VALUES (579,3,'2026-04-27','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(580,4,'2026-04-27','lunch','05:07:00','23:00:00',25,'available',NULL,NULL),(581,6,'2026-04-27','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(582,7,'2026-04-27','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(583,8,'2026-04-27','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(584,10,'2026-04-27','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(585,12,'2026-04-27','breakfast','08:00:00','23:00:00',20,'available',NULL,NULL),(586,13,'2026-04-27','lunch','12:00:00','23:00:00',25,'available',NULL,NULL),(587,14,'2026-04-27','lunch','12:00:00','23:00:00',25,'available',NULL,NULL),(588,15,'2026-04-27','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(589,16,'2026-04-27','breakfast','08:00:00','23:00:00',25,'available',NULL,NULL),(590,17,'2026-04-27','breakfast','06:00:00','22:58:00',7,'available',NULL,NULL),(591,18,'2026-04-27','lunch','12:00:00','18:00:00',25,'available',NULL,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `food_items`
--

LOCK TABLES `food_items` WRITE;
/*!40000 ALTER TABLE `food_items` DISABLE KEYS */;
INSERT INTO `food_items` VALUES (3,'Chicken Biriyani',75.00,'chicken_biriyani_1753029774.webp','lunch',1,25,'i am a junk food','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,'08:00:00','23:00:00',NULL,'23:00:00'),(4,'Veg Meals',50.00,'veg_meals_1753029797.webp','lunch',1,25,'i am a vegan broo....','lunch','mon,tue,wed,thu,fri,sun','05:07:00','23:00:00',25,'08:00:00','23:00:00','05:07:00','23:00:00'),(5,'chappathii',12.00,'chappathii_1753029826.webp',NULL,1,10,'shbuybfyubwuy','lunch','sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(6,'bababa pufs',28.00,'bababa_pufs_1775905680.webp',NULL,1,25,'Hello there i am pufs ...','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(7,'Dosa',12.00,'dosa_1775905543.webp',NULL,1,25,'Dosa dosa dosa','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(8,'Idli sambar',59.00,'idli_sambar_1753701382.webp',NULL,1,10,'Vssjsnsbsb','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(10,'porotta',12.00,'porotta_1753029901.webp',NULL,1,10,'ghhg','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',25,'08:00:00','23:00:00','08:00:00','23:00:00'),(12,'berger',70.00,'berger.webp',NULL,1,10,'yummy','breakfast','mon,tue,wed,thu,fri,sat,sun','09:00:00','23:00:00',20,'08:00:00','23:00:00','08:00:00','23:00:00'),(13,'kozhi tikka 65',500.00,'kozhi_tikka_65.webp',NULL,1,25,'i am yummyyyyy','lunch','mon,tue,wed,thu,fri,sat,sun','12:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(14,'Kaytha chakka',20.00,'kaytha_chakka.webp',NULL,1,25,'Very very tasty','lunch','mon,tue,wed,thu,fri,sat,sun','12:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(15,'keethuuuuu',1.00,'keethuuuuu.webp',NULL,1,25,'poison','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(16,'paruu',1.00,'paruu.webp',NULL,1,25,'poison','breakfast','mon,tue,wed,thu,fri,sat,sun','08:00:00','23:00:00',25,NULL,'23:00:00',NULL,'23:00:00'),(17,'midhun',7.00,'midhun_1758195687.webp','breakfast',1,7,'helo there eat me.....','breakfast','mon,tue,wed,thu,fri,sat,sun','06:00:00','22:58:00',7,'06:00:00','22:58:00','12:00:00','15:00:00'),(18,'Cristiano',7.00,'cristiano_1775905755.webp','lunch',1,25,'Goat ?','lunch','mon,tue,wed,thu,fri,sat,sun','12:00:00','18:00:00',25,NULL,'11:00:00','12:00:00','18:00:00');
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
) ENGINE=InnoDB AUTO_INCREMENT=248 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (236,299,7,1,12.00),(237,300,17,1,7.00),(238,302,3,1,75.00),(239,302,12,1,70.00),(240,303,8,1,59.00),(241,303,16,1,1.00),(242,304,10,1,12.00),(243,304,16,1,1.00),(244,305,3,1,75.00),(245,306,3,1,75.00),(246,306,7,1,12.00),(247,306,10,2,12.00);
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
  `order_type` varchar(10) NOT NULL DEFAULT 'online',
  PRIMARY KEY (`id`),
  KEY `idx_token` (`token_number`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=307 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (299,21,12.00,'confirmed','2026-04-11 19:20:33',1,'paid','order_ScCyCCBNYCtQV3','pay_ScCyKPPaLTHuSt',NULL,'razorpay','online'),(300,22,7.00,'confirmed','2026-04-11 22:18:34',2,'paid','order_ScG02D0REtW0mH','pay_ScG0HVPb1HQN28',NULL,'razorpay','online'),(302,23,145.00,'delivered','2026-04-24 12:06:50',1,'paid',NULL,NULL,NULL,'cash','offline'),(303,23,60.00,'delivered','2026-04-24 12:42:17',2,'paid',NULL,NULL,NULL,'cash','offline'),(304,23,13.00,'delivered','2026-04-24 12:52:54',3,'paid',NULL,NULL,NULL,'cash','offline'),(305,16,75.00,'delivered','2026-04-24 12:56:40',5381,'paid','order_ShFMyxYKrJN852','pay_ShFNKZUgUaNQVH',NULL,'razorpay','online'),(306,23,111.00,'delivered','2026-04-24 12:58:27',4,'paid',NULL,NULL,NULL,'cash','offline');
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
  KEY `order_id` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=355 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (16,'MIDHUN SIBY ','midhunsiby5@gmail.com','8590488423',NULL,'student'),(17,'MIDHUN SIBY ','midhunsiby3028@gmail.com','8590488423',NULL,'student'),(18,'Keerthana S','keertisnair04@gmail.com','7736637902',NULL,'student'),(19,'MIDHUN SIBY ','midhunsiby9999@gmail.com','8590488423',NULL,'student'),(20,'Test User','test@example.com','1234567890',NULL,'student'),(21,'MIDHUN SIBY ','midhunsibi123@gmail.com','8590488423',NULL,'student'),(22,'Karthik Baki Secret','karthiksambhur123@gmail.com','1234567890',NULL,'student'),(23,'Walk-in Customer','walkin@campusbites.local','0000000000',NULL,'student');
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

-- Dump completed on 2026-04-27 13:50:29
