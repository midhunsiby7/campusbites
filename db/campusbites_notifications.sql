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
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,NULL,1,'New Order! Token #49 by None.','new_order',128,1,'2025-07-20 14:14:35'),(2,NULL,1,'New Order! Token #50 by None.','new_order',129,1,'2025-07-20 14:14:35'),(3,NULL,1,'New Order! Token #51 by None.','new_order',130,1,'2025-07-20 14:15:07'),(4,NULL,1,'New Order! Token #52 by None.','new_order',131,1,'2025-07-20 14:16:13'),(5,NULL,1,'New Order! Token #53 by None.','new_order',132,1,'2025-07-20 14:18:58'),(6,NULL,1,'New Order! Token #54 by None.','new_order',133,1,'2025-07-20 14:20:17'),(7,NULL,1,'New Order! Token #55 by None.','new_order',134,1,'2025-07-20 14:20:17'),(8,NULL,1,'New Order! Token #56 by None.','new_order',135,1,'2025-07-20 14:20:36'),(9,NULL,1,'New Order! Token #57 by None.','new_order',136,1,'2025-07-20 14:20:55'),(10,NULL,1,'New Order! Token #58 by None.','new_order',137,1,'2025-07-20 14:22:00'),(11,NULL,1,'New Order! Token #59 by None.','new_order',138,1,'2025-07-20 14:23:06'),(12,NULL,1,'New Order! Token #60 by None.','new_order',139,1,'2025-07-20 14:49:19'),(13,NULL,1,'New Order! Token #61 by None.','new_order',140,1,'2025-07-20 14:49:19'),(14,NULL,1,'New Order! Token #62 by None.','new_order',141,1,'2025-07-20 15:26:20'),(15,NULL,1,'New Order! Token #63 by None.','new_order',142,1,'2025-07-20 15:37:56'),(16,NULL,1,'New Cart Order! Token #64 by None.','new_order',143,1,'2025-07-20 15:39:54'),(17,NULL,1,'New Order! Token #65 by None.','new_order',144,1,'2025-07-20 16:40:09'),(18,NULL,1,'New Order! Token #66 by None.','new_order',145,1,'2025-07-20 16:40:47'),(19,NULL,1,'New Order! Token #67 by Joel Mathew.','new_order',146,1,'2025-07-21 09:44:18'),(20,NULL,1,'New Order! Token #68 by Joel Mathew.','new_order',147,1,'2025-07-21 09:45:16'),(21,NULL,1,'New Order! Token #69 by Joel Mathew.','new_order',148,1,'2025-07-21 09:47:53'),(22,NULL,1,'New Order! Token #70 by None.','new_order',149,1,'2025-07-22 12:21:19'),(23,NULL,1,'New Order! Token #71 by None.','new_order',150,1,'2025-07-22 15:18:57'),(24,NULL,1,'New Order! Token #72 by None.','new_order',151,1,'2025-07-22 15:43:25'),(25,NULL,1,'New Order! Token #73 by None.','new_order',152,1,'2025-07-24 04:47:43'),(26,NULL,1,'New Order! Token #74 by None.','new_order',153,1,'2025-07-24 04:48:39'),(27,NULL,1,'New Cart Order! Token #75 by None.','new_order',154,1,'2025-07-24 04:48:57'),(28,NULL,1,'New Order! Token #76 by None.','new_order',155,1,'2025-07-24 04:54:34'),(29,NULL,1,'New Order! Token #77 by None.','new_order',156,1,'2025-07-24 04:54:34'),(30,NULL,1,'New Order! Token #78 by None.','new_order',157,1,'2025-07-24 05:39:50'),(31,NULL,1,'New Order! Token #79 by None.','new_order',158,1,'2025-07-24 05:42:54'),(32,NULL,1,'New Order! Token #80 by None.','new_order',159,1,'2025-07-24 05:42:54'),(33,NULL,1,'New Cart Order! Token #90 by None.','new_order',169,1,'2025-07-24 05:50:50'),(34,NULL,1,'New Order! Token #1 by None.','new_order',170,1,'2025-07-24 06:13:22'),(35,NULL,1,'New Order! Token #1 by None.','new_order',171,1,'2025-07-24 06:39:05'),(36,NULL,1,'New Cart Order! Token #2 by None.','new_order',172,1,'2025-07-24 06:39:15'),(37,NULL,1,'New Cart Order! Token #3 by None.','new_order',173,1,'2025-07-24 06:39:46'),(38,NULL,1,'New Cart Order! Token #4 by None.','new_order',174,1,'2025-07-24 07:33:16'),(39,NULL,1,'New Order! Token #5 by None.','new_order',175,1,'2025-07-24 07:44:21'),(40,NULL,1,'New Order! Token #6 by None.','new_order',176,1,'2025-07-24 07:47:50'),(41,NULL,1,'New Order! Token #7 by None.','new_order',177,1,'2025-07-24 13:27:12'),(42,NULL,1,'New Order! Token #8 by Joel Mathew.','new_order',178,1,'2025-07-24 14:32:17'),(43,NULL,1,'New Order! Token #9 by Joel Mathew.','new_order',179,1,'2025-07-24 14:34:35'),(44,NULL,1,'New Cart Order! Token #10 by midhun s.','new_order',180,1,'2025-07-24 15:14:58'),(45,NULL,1,'New Order! Token #1 by midhun s.','new_order',195,1,'2025-07-28 10:20:50'),(46,NULL,1,'New Order! Token #2 by midhun s.','new_order',196,1,'2025-07-28 10:22:14'),(47,NULL,1,'New Order! Token #3 by midhun s.','new_order',197,1,'2025-07-28 10:22:14'),(48,NULL,1,'New Order! Token #4 by midhun s.','new_order',198,1,'2025-07-28 10:22:44'),(49,NULL,1,'New Order! Token #5 by midhun s.','new_order',199,1,'2025-07-28 10:35:00'),(50,NULL,1,'New Order! Token #1 by midhun s.','new_order',205,1,'2025-07-29 09:32:21'),(51,NULL,1,'New Order! Token #2 by keerthana v.','new_order',206,1,'2025-07-29 09:48:08'),(52,NULL,1,'New Order! Token #3 by keerthana v.','new_order',207,1,'2025-07-29 09:54:25'),(53,NULL,1,'New Order! Token #4 by midhun s.','new_order',208,1,'2025-07-29 09:57:39'),(54,NULL,1,'New Order! Token #2 by midhun s.','new_order',209,1,'2025-07-30 04:33:31'),(55,NULL,1,'New Order! Token #6 by keerthana v.','new_order',210,1,'2025-07-30 04:41:23'),(56,NULL,1,'New Order! Token #7 by keerthana v.','new_order',211,1,'2025-07-30 08:56:46'),(57,NULL,1,'New Order! Token #8 by keerthana v.','new_order',212,1,'2025-07-30 09:00:46'),(58,7,0,'Your order #15 is out for delivery!','order_delivered',226,0,'2025-07-31 10:55:55'),(59,7,0,'Your order #1 is out for delivery!','order_delivered',227,0,'2025-07-31 11:13:05'),(64,7,0,'Your order #1 is out for delivery!','order_delivered',232,0,'2025-08-03 14:01:12'),(65,7,0,'Your order #4 is out for delivery!','order_delivered',233,0,'2025-08-03 14:15:30'),(76,6,0,'Your order #4 is out for delivery!','order_delivered',238,0,'2025-08-03 16:21:11'),(77,6,0,'Your order #3 is out for delivery!','order_delivered',237,0,'2025-08-03 16:21:16'),(78,6,0,'Your order #2 is out for delivery!','order_delivered',236,0,'2025-08-03 16:21:19'),(79,8,0,'Your order #1 is out for delivery!','order_delivered',235,0,'2025-08-03 16:25:09'),(82,7,0,'Your order #1 is out for delivery!','order_delivered',239,0,'2025-08-04 09:03:46'),(85,7,0,'Your order #2 is out for delivery!','order_delivered',240,0,'2025-08-04 09:06:55');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-05 17:22:19
