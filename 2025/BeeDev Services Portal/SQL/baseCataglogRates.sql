-- MySQL dump 10.13  Distrib 8.0.27, for macos11 (x86_64)
--
-- Host: localhost    Database: thehives_beedev_portal
-- ------------------------------------------------------
-- Server version	8.0.22

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
-- Dumping data for table `proposalApp_basesetting`
--

LOCK TABLES `proposalApp_basesetting` WRITE;
/*!40000 ALTER TABLE `proposalApp_basesetting` DISABLE KEYS */;
INSERT INTO `proposalApp_basesetting` VALUES (1,'vite-base','Vite App',300.00,'',1,0),(2,'python-default','Python Default Base',400.00,'',1,0),(3,'python-custom','Python Custom Base',500.00,'',1,0),(5,'hosting-monthly','Hosting-Monthly',20.00,'',1,0),(6,'hosting-yearly','Hosting Yearly',200.00,'',1,0),(7,'gen','General',0.00,'',1,0);
/*!40000 ALTER TABLE `proposalApp_basesetting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `proposalApp_catalogitem`
--

LOCK TABLES `proposalApp_catalogitem` WRITE;
/*!40000 ALTER TABLE `proposalApp_catalogitem` DISABLE KEYS */;
INSERT INTO `proposalApp_catalogitem` VALUES (1,'viteHome','Vite App + Home page','Vite App with Home Page',2.00,1.00,1,'',0,1,1),(2,'python-default','Python App + 3 Pages + Default Admin','',6.00,1.00,1,'',0,2,1),(3,'python-custom','Python App + 3 Pages + Custom Admin','',12.00,1.00,1,'',0,3,1),(4,'design','Site Design','',1.00,1.00,1,'',0,7,2),(5,'seo','SEO','',0.50,1.00,1,'',0,7,3),(6,'mobile','Mobile Responsivness','',0.50,1.00,1,'',0,7,1),(7,'deploy','Deployment','',1.00,1.00,1,'',0,7,3),(8,'contact-node','Contact Page w/Node Mailer','',4.00,1.00,1,'',0,7,1),(9,'privacy-terms','Privacy Policy / Terms and Conditions','',2.00,1.00,1,'',0,7,1),(10,'pages','Additional Pages','',0.50,2.00,1,'',0,7,1),(11,'blog-open','Blog - Open Source','',4.00,1.00,1,'',0,7,1),(12,'blog-custom','Blog - Custom','',8.00,1.00,1,'',0,7,1),(13,'ecomm-open','Ecommerce - Open Source','',4.00,1.00,1,'',0,7,1),(14,'ecomm-custom','Ecommerce - Custom','',16.00,1.00,1,'',0,7,1),(15,'transfer-domain','Domain Transfer','',1.00,1.00,1,'',0,7,3),(16,'hosting-monthly','Hosting-Monthly','',12.00,1.00,1,'',0,5,3),(17,'hosting-yearly','Hosting Yearly','',1.00,1.00,1,'',0,6,3),(18,'single-app-non','Single Platform App - Non Ecommerce','',16.00,1.00,1,'',0,7,1),(19,'cross-app-non','Cross Platform App - Non Ecommerce','',24.00,2.00,1,'',0,7,1),(20,'single-app-ecom','Single Platform App - Complex','',24.00,2.00,1,'',0,7,4),(21,'cross-app-ecomm','Cross Platform App - Complex','',36.00,3.00,1,'',0,7,4),(22,'back-heavy-custom','Heavy Custom Backend','',16.00,1.00,1,'',0,7,4);
/*!40000 ALTER TABLE `proposalApp_catalogitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `proposalApp_costtier`
--

LOCK TABLES `proposalApp_costtier` WRITE;
/*!40000 ALTER TABLE `proposalApp_costtier` DISABLE KEYS */;
INSERT INTO `proposalApp_costtier` VALUES (1,'tier01','Tier 1',0.00,1100.00,'',0,1),(2,'tier02','Tier 2',1100.01,1700.00,'',0,1),(3,'tier03','Tier 3',1700.01,NULL,'',0,1);
/*!40000 ALTER TABLE `proposalApp_costtier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `proposalApp_jobrate`
--

LOCK TABLES `proposalApp_jobrate` WRITE;
/*!40000 ALTER TABLE `proposalApp_jobrate` DISABLE KEYS */;
INSERT INTO `proposalApp_jobrate` VALUES (1,'dev','Developer',35.00,1,0),(2,'design','Designer',30.00,1,0),(3,'devops','DevOps',25.00,1,0),(4,'back','Backend Developer',40.00,1,0);
/*!40000 ALTER TABLE `proposalApp_jobrate` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-25 20:16:30
