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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-20 11:25:00
