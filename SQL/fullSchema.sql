CREATE DATABASE  IF NOT EXISTS `thehives_beedev_portal` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `thehives_beedev_portal`;
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
-- Table structure for table `announceApp_announcement`
--

DROP TABLE IF EXISTS `announceApp_announcement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announceApp_announcement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `slug` varchar(80) NOT NULL,
  `title` varchar(140) NOT NULL,
  `message_html` longtext NOT NULL,
  `audience` varchar(12) NOT NULL,
  `severity` varchar(8) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `dismissible` tinyint(1) NOT NULL,
  `starts_at` datetime(6) DEFAULT NULL,
  `ends_at` datetime(6) DEFAULT NULL,
  `priority` int NOT NULL,
  `link_url` varchar(200) NOT NULL,
  `link_text` varchar(60) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `announceApp_version`
--

DROP TABLE IF EXISTS `announceApp_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announceApp_version` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `slug` varchar(80) NOT NULL,
  `version_num` varchar(255) NOT NULL,
  `info` longtext NOT NULL,
  `date_of_release` date DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=401 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=177 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `companyApp_company`
--

DROP TABLE IF EXISTS `companyApp_company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `companyApp_company` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `slug` varchar(220) NOT NULL,
  `primary_contact_name` varchar(120) NOT NULL,
  `primary_email` varchar(254) NOT NULL,
  `phone` varchar(30) NOT NULL,
  `address_line1` varchar(200) NOT NULL,
  `address_line2` varchar(200) NOT NULL,
  `city` varchar(120) NOT NULL,
  `state_region` varchar(120) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `country` varchar(120) NOT NULL,
  `website` varchar(200) NOT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `logo_external_url` varchar(200) NOT NULL,
  `status` varchar(20) NOT NULL,
  `pipeline_status` varchar(20) NOT NULL,
  `consultation_sheet_url` varchar(200) NOT NULL,
  `first_contact_at` date DEFAULT NULL,
  `last_contact_at` date DEFAULT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`),
  KEY `companyApp_company_created_by_id_56201c4b_fk_userApp_user_id` (`created_by_id`),
  KEY `companyApp__name_a038b8_idx` (`name`),
  KEY `companyApp__slug_52ac3a_idx` (`slug`),
  KEY `companyApp__status_cbffb7_idx` (`status`),
  KEY `companyApp__pipelin_03b7db_idx` (`pipeline_status`),
  CONSTRAINT `companyApp_company_created_by_id_56201c4b_fk_userApp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `companyApp_companycontact`
--

DROP TABLE IF EXISTS `companyApp_companycontact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `companyApp_companycontact` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(30) NOT NULL,
  `title` varchar(120) NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` bigint NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `companyApp_companycontact_company_id_email_50fb710d_uniq` (`company_id`,`email`),
  KEY `companyApp_companycontact_user_id_d3457a4a_fk_userApp_user_id` (`user_id`),
  KEY `companyApp__company_b4aac5_idx` (`company_id`,`is_primary`),
  KEY `companyApp__company_7c7ef1_idx` (`company_id`,`email`),
  CONSTRAINT `companyApp_companyco_company_id_dce76db9_fk_companyAp` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `companyApp_companycontact_user_id_d3457a4a_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `companyApp_companylink`
--

DROP TABLE IF EXISTS `companyApp_companylink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `companyApp_companylink` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `label` varchar(120) NOT NULL,
  `url` varchar(200) NOT NULL,
  `notes` longtext NOT NULL,
  `section` varchar(20) NOT NULL,
  `tags` varchar(200) NOT NULL,
  `visibility` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `key_name` varchar(120) NOT NULL,
  `key_hint` varchar(200) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `companyApp_companylink_company_id_label_section_9742d024_uniq` (`company_id`,`label`,`section`),
  KEY `companyApp_companylink_created_by_id_5347bee3_fk_userApp_user_id` (`created_by_id`),
  KEY `companyApp__company_5cb2cc_idx` (`company_id`,`visibility`,`is_active`,`sort_order`),
  KEY `companyApp__company_58993b_idx` (`company_id`,`section`),
  CONSTRAINT `companyApp_companyli_company_id_35577d81_fk_companyAp` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `companyApp_companylink_created_by_id_5347bee3_fk_userApp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `companyapp_companylink_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `companyApp_companymembership`
--

DROP TABLE IF EXISTS `companyApp_companymembership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `companyApp_companymembership` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(24) NOT NULL,
  `can_view_proposals` tinyint(1) NOT NULL,
  `can_view_invoices` tinyint(1) NOT NULL,
  `can_open_tickets` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `added_at` datetime(6) NOT NULL,
  `company_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `companyApp_companymembership_company_id_user_id_c2724e18_uniq` (`company_id`,`user_id`),
  KEY `companyApp_companymembership_user_id_c7c8cf13_fk_userApp_user_id` (`user_id`),
  KEY `companyApp__company_0bb797_idx` (`company_id`,`user_id`,`is_active`),
  KEY `companyApp__company_c30e08_idx` (`company_id`,`role`),
  CONSTRAINT `companyApp_companyme_company_id_c7486353_fk_companyAp` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `companyApp_companymembership_user_id_c7c8cf13_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_userApp_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invoiceApp_invoice`
--

DROP TABLE IF EXISTS `invoiceApp_invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoiceApp_invoice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `number` varchar(40) NOT NULL,
  `currency` varchar(8) NOT NULL,
  `issue_date` date NOT NULL,
  `due_date` date DEFAULT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `discount_total` decimal(12,2) NOT NULL,
  `tax_total` decimal(12,2) NOT NULL,
  `total` decimal(12,2) NOT NULL,
  `minimum_due` decimal(12,2) NOT NULL,
  `amount_paid` decimal(12,2) NOT NULL,
  `status` varchar(10) NOT NULL,
  `view_token` varchar(64) NOT NULL,
  `pdf` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `customer_contact_id` bigint DEFAULT NULL,
  `customer_user_id` bigint DEFAULT NULL,
  `proposal_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`),
  UNIQUE KEY `view_token` (`view_token`),
  KEY `invoiceApp_invoice_created_by_id_49c68518_fk_userApp_user_id` (`created_by_id`),
  KEY `invoiceApp_invoice_customer_contact_id_3ffd10ce_fk_companyAp` (`customer_contact_id`),
  KEY `invoiceApp_invoice_customer_user_id_3deb36d9_fk_userApp_user_id` (`customer_user_id`),
  KEY `invoiceApp_invoice_proposal_id_04e2b23b_fk_proposalA` (`proposal_id`),
  KEY `invoiceApp__company_f14901_idx` (`company_id`,`status`),
  KEY `invoiceApp__number_7b94ca_idx` (`number`),
  KEY `invoiceApp__company_32d946_idx` (`company_id`,`customer_user_id`),
  CONSTRAINT `invoiceApp_invoice_company_id_270c6ef1_fk_companyApp_company_id` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `invoiceApp_invoice_created_by_id_49c68518_fk_userApp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `invoiceApp_invoice_customer_contact_id_3ffd10ce_fk_companyAp` FOREIGN KEY (`customer_contact_id`) REFERENCES `companyApp_companycontact` (`id`),
  CONSTRAINT `invoiceApp_invoice_customer_user_id_3deb36d9_fk_userApp_user_id` FOREIGN KEY (`customer_user_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `invoiceApp_invoice_proposal_id_04e2b23b_fk_proposalA` FOREIGN KEY (`proposal_id`) REFERENCES `proposalApp_proposal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invoiceApp_invoiceapplieddiscount`
--

DROP TABLE IF EXISTS `invoiceApp_invoiceapplieddiscount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoiceApp_invoiceapplieddiscount` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `discount_code` varchar(40) NOT NULL,
  `name` varchar(120) NOT NULL,
  `kind` varchar(10) NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `amount_applied` decimal(12,2) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `invoice_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `invoiceApp_invoiceapplieddiscount_discount_code_5b26a11f` (`discount_code`),
  KEY `invoiceApp_invoiceap_invoice_id_8bf2ac13_fk_invoiceAp` (`invoice_id`),
  CONSTRAINT `invoiceApp_invoiceap_invoice_id_8bf2ac13_fk_invoiceAp` FOREIGN KEY (`invoice_id`) REFERENCES `invoiceApp_invoice` (`id`),
  CONSTRAINT `invoiceapp_invoiceapplieddiscount_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invoiceApp_invoicelineitem`
--

DROP TABLE IF EXISTS `invoiceApp_invoicelineitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoiceApp_invoicelineitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sort_order` int unsigned NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `quantity` decimal(8,2) NOT NULL,
  `unit_price` decimal(12,2) NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `invoice_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `invoiceApp_invoiceli_invoice_id_dc0f4c89_fk_invoiceAp` (`invoice_id`),
  CONSTRAINT `invoiceApp_invoiceli_invoice_id_dc0f4c89_fk_invoiceAp` FOREIGN KEY (`invoice_id`) REFERENCES `invoiceApp_invoice` (`id`),
  CONSTRAINT `invoiceapp_invoicelineitem_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invoiceApp_invoiceviewer`
--

DROP TABLE IF EXISTS `invoiceApp_invoiceviewer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoiceApp_invoiceviewer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `invoice_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoiceApp_invoiceviewer_invoice_id_user_id_2c11f427_uniq` (`invoice_id`,`user_id`),
  KEY `invoiceApp_invoiceviewer_user_id_fbcad8ca_fk_userApp_user_id` (`user_id`),
  KEY `invoiceApp__invoice_bb84b4_idx` (`invoice_id`,`user_id`),
  CONSTRAINT `invoiceApp_invoicevi_invoice_id_cbf892ef_fk_invoiceAp` FOREIGN KEY (`invoice_id`) REFERENCES `invoiceApp_invoice` (`id`),
  CONSTRAINT `invoiceApp_invoiceviewer_user_id_fbcad8ca_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invoiceApp_payment`
--

DROP TABLE IF EXISTS `invoiceApp_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoiceApp_payment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(12,2) NOT NULL,
  `method` varchar(10) NOT NULL,
  `reference` varchar(120) NOT NULL,
  `received_at` datetime(6) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `invoice_id` bigint NOT NULL,
  `payer_user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `invoiceApp_payment_created_by_id_5a8a4a69_fk_userApp_user_id` (`created_by_id`),
  KEY `invoiceApp_payment_invoice_id_8cecb4d0_fk_invoiceApp_invoice_id` (`invoice_id`),
  KEY `invoiceApp_payment_payer_user_id_cdac1ba3_fk_userApp_user_id` (`payer_user_id`),
  CONSTRAINT `invoiceApp_payment_created_by_id_5a8a4a69_fk_userApp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `invoiceApp_payment_invoice_id_8cecb4d0_fk_invoiceApp_invoice_id` FOREIGN KEY (`invoice_id`) REFERENCES `invoiceApp_invoice` (`id`),
  CONSTRAINT `invoiceApp_payment_payer_user_id_cdac1ba3_fk_userApp_user_id` FOREIGN KEY (`payer_user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projectApp_project`
--

DROP TABLE IF EXISTS `projectApp_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectApp_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `slug` varchar(240) NOT NULL,
  `status` varchar(20) NOT NULL,
  `stage` varchar(20) NOT NULL,
  `description` longtext NOT NULL,
  `scope_summary` longtext NOT NULL,
  `percent_complete` decimal(5,2) NOT NULL,
  `start_date` date DEFAULT NULL,
  `target_launch_date` date DEFAULT NULL,
  `actual_launch_date` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `tags` varchar(200) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `manager_id` bigint DEFAULT NULL,
  `proposal_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `projectApp_project_created_by_id_5cf2d884_fk_userApp_user_id` (`created_by_id`),
  KEY `projectApp_project_manager_id_8de244ea_fk_userApp_user_id` (`manager_id`),
  KEY `projectApp_project_proposal_id_45a8973a_fk_proposalA` (`proposal_id`),
  KEY `projectApp__company_2b187f_idx` (`company_id`,`status`),
  KEY `projectApp__slug_ea6dec_idx` (`slug`),
  CONSTRAINT `projectApp_project_company_id_a550c01f_fk_companyApp_company_id` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `projectApp_project_created_by_id_5cf2d884_fk_userApp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `projectApp_project_manager_id_8de244ea_fk_userApp_user_id` FOREIGN KEY (`manager_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `projectApp_project_proposal_id_45a8973a_fk_proposalA` FOREIGN KEY (`proposal_id`) REFERENCES `proposalApp_proposal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projectApp_projectenvironment`
--

DROP TABLE IF EXISTS `projectApp_projectenvironment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectApp_projectenvironment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `kind` varchar(10) NOT NULL,
  `url` varchar(200) NOT NULL,
  `health` varchar(12) NOT NULL,
  `note` varchar(200) NOT NULL,
  `last_checked_at` datetime(6) DEFAULT NULL,
  `last_updated_by_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `projectApp_projectenvironment_project_id_kind_d13b9534_uniq` (`project_id`,`kind`),
  KEY `projectApp_projecten_last_updated_by_id_098e5e87_fk_userApp_u` (`last_updated_by_id`),
  CONSTRAINT `projectApp_projecten_last_updated_by_id_098e5e87_fk_userApp_u` FOREIGN KEY (`last_updated_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `projectApp_projecten_project_id_8332594e_fk_projectAp` FOREIGN KEY (`project_id`) REFERENCES `projectApp_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projectApp_projectlink`
--

DROP TABLE IF EXISTS `projectApp_projectlink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectApp_projectlink` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `label` varchar(120) NOT NULL,
  `url` varchar(200) NOT NULL,
  `section` varchar(20) NOT NULL,
  `visibility` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `notes` longtext NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `projectApp_projectlink_project_id_label_section_b04ea292_uniq` (`project_id`,`label`,`section`),
  CONSTRAINT `projectApp_projectli_project_id_834a7447_fk_projectAp` FOREIGN KEY (`project_id`) REFERENCES `projectApp_project` (`id`),
  CONSTRAINT `projectapp_projectlink_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projectApp_projectmember`
--

DROP TABLE IF EXISTS `projectApp_projectmember`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectApp_projectmember` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(16) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `added_at` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `projectApp_projectmember_project_id_user_id_de52bf6b_uniq` (`project_id`,`user_id`),
  KEY `projectApp_projectmember_user_id_c3240517_fk_userApp_user_id` (`user_id`),
  CONSTRAINT `projectApp_projectme_project_id_b6833b9e_fk_projectAp` FOREIGN KEY (`project_id`) REFERENCES `projectApp_project` (`id`),
  CONSTRAINT `projectApp_projectmember_user_id_c3240517_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projectApp_projectmilestone`
--

DROP TABLE IF EXISTS `projectApp_projectmilestone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectApp_projectmilestone` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `due_date` date DEFAULT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `state` varchar(12) NOT NULL,
  `is_client_visible` tinyint(1) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projectApp_projectmi_project_id_26517ac4_fk_projectAp` (`project_id`),
  CONSTRAINT `projectApp_projectmi_project_id_26517ac4_fk_projectAp` FOREIGN KEY (`project_id`) REFERENCES `projectApp_project` (`id`),
  CONSTRAINT `projectapp_projectmilestone_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projectApp_projectupdate`
--

DROP TABLE IF EXISTS `projectApp_projectupdate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectApp_projectupdate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `body` longtext NOT NULL,
  `visibility` varchar(10) NOT NULL,
  `percent_complete_snapshot` decimal(5,2) NOT NULL,
  `posted_at` datetime(6) NOT NULL,
  `pinned` tinyint(1) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projectApp_projectup_created_by_id_7204fda3_fk_userApp_u` (`created_by_id`),
  KEY `projectApp__project_597c58_idx` (`project_id`,`visibility`,`posted_at` DESC),
  CONSTRAINT `projectApp_projectup_created_by_id_7204fda3_fk_userApp_u` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `projectApp_projectup_project_id_f94aaba9_fk_projectAp` FOREIGN KEY (`project_id`) REFERENCES `projectApp_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projectApp_projectupdateattachment`
--

DROP TABLE IF EXISTS `projectApp_projectupdateattachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projectApp_projectupdateattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `original_name` varchar(200) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `update_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `projectApp_projectup_update_id_85f4f5d9_fk_projectAp` (`update_id`),
  CONSTRAINT `projectApp_projectup_update_id_85f4f5d9_fk_projectAp` FOREIGN KEY (`update_id`) REFERENCES `projectApp_projectupdate` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_basesetting`
--

DROP TABLE IF EXISTS `proposalApp_basesetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_basesetting` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(60) NOT NULL,
  `name` varchar(160) NOT NULL,
  `base_rate` decimal(12,2) NOT NULL,
  `description` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  CONSTRAINT `proposalapp_basesetting_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_catalogitem`
--

DROP TABLE IF EXISTS `proposalApp_catalogitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_catalogitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(80) NOT NULL,
  `name` varchar(160) NOT NULL,
  `description` longtext NOT NULL,
  `default_hours` decimal(8,2) NOT NULL,
  `default_quantity` decimal(8,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `tags` varchar(200) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `base_setting_id` bigint NOT NULL,
  `job_rate_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `proposalApp_catalogi_base_setting_id_19dd360b_fk_proposalA` (`base_setting_id`),
  KEY `proposalApp_catalogi_job_rate_id_ede2c7c8_fk_proposalA` (`job_rate_id`),
  CONSTRAINT `proposalApp_catalogi_base_setting_id_19dd360b_fk_proposalA` FOREIGN KEY (`base_setting_id`) REFERENCES `proposalApp_basesetting` (`id`),
  CONSTRAINT `proposalApp_catalogi_job_rate_id_ede2c7c8_fk_proposalA` FOREIGN KEY (`job_rate_id`) REFERENCES `proposalApp_jobrate` (`id`),
  CONSTRAINT `proposalapp_catalogitem_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_costtier`
--

DROP TABLE IF EXISTS `proposalApp_costtier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_costtier` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(40) NOT NULL,
  `label` varchar(80) NOT NULL,
  `min_total` decimal(12,2) NOT NULL,
  `max_total` decimal(12,2) DEFAULT NULL,
  `notes` longtext NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  CONSTRAINT `proposalapp_costtier_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_discount`
--

DROP TABLE IF EXISTS `proposalApp_discount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_discount` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `code` varchar(40) NOT NULL,
  `kind` varchar(10) NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_draftitem`
--

DROP TABLE IF EXISTS `proposalApp_draftitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_draftitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(160) NOT NULL,
  `description` longtext NOT NULL,
  `hours` decimal(8,2) NOT NULL,
  `quantity` decimal(8,2) NOT NULL,
  `line_total` decimal(12,2) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `base_setting_id` bigint NOT NULL,
  `catalog_item_id` bigint NOT NULL,
  `job_rate_id` bigint NOT NULL,
  `draft_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `proposalApp_draftite_base_setting_id_bd20ec78_fk_proposalA` (`base_setting_id`),
  KEY `proposalApp_draftite_catalog_item_id_d563ad67_fk_proposalA` (`catalog_item_id`),
  KEY `proposalApp_draftite_job_rate_id_af6b813e_fk_proposalA` (`job_rate_id`),
  KEY `proposalApp_draftite_draft_id_440b5482_fk_proposalA` (`draft_id`),
  CONSTRAINT `proposalApp_draftite_base_setting_id_bd20ec78_fk_proposalA` FOREIGN KEY (`base_setting_id`) REFERENCES `proposalApp_basesetting` (`id`),
  CONSTRAINT `proposalApp_draftite_catalog_item_id_d563ad67_fk_proposalA` FOREIGN KEY (`catalog_item_id`) REFERENCES `proposalApp_catalogitem` (`id`),
  CONSTRAINT `proposalApp_draftite_draft_id_440b5482_fk_proposalA` FOREIGN KEY (`draft_id`) REFERENCES `proposalApp_proposaldraft` (`id`),
  CONSTRAINT `proposalApp_draftite_job_rate_id_af6b813e_fk_proposalA` FOREIGN KEY (`job_rate_id`) REFERENCES `proposalApp_jobrate` (`id`),
  CONSTRAINT `proposalapp_draftitem_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_jobrate`
--

DROP TABLE IF EXISTS `proposalApp_jobrate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_jobrate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(40) NOT NULL,
  `name` varchar(120) NOT NULL,
  `hourly_rate` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  CONSTRAINT `proposalapp_jobrate_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_proposal`
--

DROP TABLE IF EXISTS `proposalApp_proposal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_proposal` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `currency` varchar(8) NOT NULL,
  `amount_subtotal` decimal(12,2) NOT NULL,
  `amount_tax` decimal(12,2) NOT NULL,
  `discount_total` decimal(12,2) NOT NULL,
  `amount_total` decimal(12,2) NOT NULL,
  `deposit_type` varchar(10) NOT NULL,
  `deposit_value` decimal(12,2) NOT NULL,
  `deposit_amount` decimal(12,2) NOT NULL,
  `remaining_due` decimal(12,2) NOT NULL,
  `sign_token` varchar(64) NOT NULL,
  `token_expires_at` datetime(6) DEFAULT NULL,
  `sent_at` datetime(6) DEFAULT NULL,
  `viewed_at` datetime(6) DEFAULT NULL,
  `signed_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `converted_from_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sign_token` (`sign_token`),
  KEY `proposalApp_proposal_company_id_8514d724_fk_companyAp` (`company_id`),
  KEY `proposalApp_proposal_created_by_id_a55b53ef_fk_userApp_user_id` (`created_by_id`),
  KEY `proposalApp_proposal_converted_from_id_6d57224c_fk_proposalA` (`converted_from_id`),
  CONSTRAINT `proposalApp_proposal_company_id_8514d724_fk_companyAp` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `proposalApp_proposal_converted_from_id_6d57224c_fk_proposalA` FOREIGN KEY (`converted_from_id`) REFERENCES `proposalApp_proposaldraft` (`id`),
  CONSTRAINT `proposalApp_proposal_created_by_id_a55b53ef_fk_userApp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_proposalapplieddiscount`
--

DROP TABLE IF EXISTS `proposalApp_proposalapplieddiscount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_proposalapplieddiscount` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `discount_code` varchar(40) NOT NULL,
  `name` varchar(120) NOT NULL,
  `kind` varchar(10) NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `amount_applied` decimal(12,2) NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `proposal_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `proposalApp_proposalapplieddiscount_discount_code_31b84bb1` (`discount_code`),
  KEY `proposalApp_proposal_proposal_id_373f275a_fk_proposalA` (`proposal_id`),
  CONSTRAINT `proposalApp_proposal_proposal_id_373f275a_fk_proposalA` FOREIGN KEY (`proposal_id`) REFERENCES `proposalApp_proposal` (`id`),
  CONSTRAINT `proposalapp_proposalapplieddiscount_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_proposaldraft`
--

DROP TABLE IF EXISTS `proposalApp_proposaldraft`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_proposaldraft` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `currency` varchar(8) NOT NULL,
  `contact_name` varchar(160) NOT NULL,
  `contact_email` varchar(254) NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `discount_amount` decimal(12,2) NOT NULL,
  `total` decimal(12,2) NOT NULL,
  `deposit_type` varchar(10) NOT NULL,
  `deposit_value` decimal(12,2) NOT NULL,
  `deposit_amount` decimal(12,2) NOT NULL,
  `remaining_due` decimal(12,2) NOT NULL,
  `estimate_low` decimal(12,2) NOT NULL,
  `estimate_high` decimal(12,2) NOT NULL,
  `estimate_manual` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `discount_id` bigint DEFAULT NULL,
  `estimate_tier_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `proposalApp_proposal_company_id_4d8f0e7d_fk_companyAp` (`company_id`),
  KEY `proposalApp_proposal_created_by_id_e01843f5_fk_userApp_u` (`created_by_id`),
  KEY `proposalApp_proposal_discount_id_f96654a4_fk_proposalA` (`discount_id`),
  KEY `proposalApp_proposal_estimate_tier_id_592fd609_fk_proposalA` (`estimate_tier_id`),
  CONSTRAINT `proposalApp_proposal_company_id_4d8f0e7d_fk_companyAp` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `proposalApp_proposal_created_by_id_e01843f5_fk_userApp_u` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `proposalApp_proposal_discount_id_f96654a4_fk_proposalA` FOREIGN KEY (`discount_id`) REFERENCES `proposalApp_discount` (`id`),
  CONSTRAINT `proposalApp_proposal_estimate_tier_id_592fd609_fk_proposalA` FOREIGN KEY (`estimate_tier_id`) REFERENCES `proposalApp_costtier` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_proposalevent`
--

DROP TABLE IF EXISTS `proposalApp_proposalevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_proposalevent` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `kind` varchar(20) NOT NULL,
  `at` datetime(6) NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `data` json DEFAULT NULL,
  `actor_id` bigint DEFAULT NULL,
  `proposal_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `proposalApp_proposalevent_actor_id_4e2511a5_fk_userApp_user_id` (`actor_id`),
  KEY `proposalApp_proposal_proposal_id_0de2ca50_fk_proposalA` (`proposal_id`),
  CONSTRAINT `proposalApp_proposal_proposal_id_0de2ca50_fk_proposalA` FOREIGN KEY (`proposal_id`) REFERENCES `proposalApp_proposal` (`id`),
  CONSTRAINT `proposalApp_proposalevent_actor_id_4e2511a5_fk_userApp_user_id` FOREIGN KEY (`actor_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_proposallineitem`
--

DROP TABLE IF EXISTS `proposalApp_proposallineitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_proposallineitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sort_order` int unsigned NOT NULL,
  `name` varchar(160) NOT NULL,
  `description` longtext NOT NULL,
  `hours` decimal(8,2) NOT NULL,
  `quantity` decimal(8,2) NOT NULL,
  `line_total` decimal(12,2) NOT NULL,
  `unit_price` decimal(12,2) NOT NULL,
  `subtotal` decimal(12,2) NOT NULL,
  `base_setting_id` bigint NOT NULL,
  `job_rate_id` bigint NOT NULL,
  `proposal_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `proposalApp_proposal_base_setting_id_3edd4d91_fk_proposalA` (`base_setting_id`),
  KEY `proposalApp_proposal_job_rate_id_93446fdb_fk_proposalA` (`job_rate_id`),
  KEY `proposalApp_proposal_proposal_id_6ede0292_fk_proposalA` (`proposal_id`),
  CONSTRAINT `proposalApp_proposal_base_setting_id_3edd4d91_fk_proposalA` FOREIGN KEY (`base_setting_id`) REFERENCES `proposalApp_basesetting` (`id`),
  CONSTRAINT `proposalApp_proposal_job_rate_id_93446fdb_fk_proposalA` FOREIGN KEY (`job_rate_id`) REFERENCES `proposalApp_jobrate` (`id`),
  CONSTRAINT `proposalApp_proposal_proposal_id_6ede0292_fk_proposalA` FOREIGN KEY (`proposal_id`) REFERENCES `proposalApp_proposal` (`id`),
  CONSTRAINT `proposalapp_proposallineitem_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_proposalrecipient`
--

DROP TABLE IF EXISTS `proposalApp_proposalrecipient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_proposalrecipient` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(160) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  `delivered_at` datetime(6) DEFAULT NULL,
  `last_opened_at` datetime(6) DEFAULT NULL,
  `proposal_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `proposalApp_proposalrecipient_proposal_id_email_af70c396_uniq` (`proposal_id`,`email`),
  CONSTRAINT `proposalApp_proposal_proposal_id_7eb17062_fk_proposalA` FOREIGN KEY (`proposal_id`) REFERENCES `proposalApp_proposal` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proposalApp_proposalviewer`
--

DROP TABLE IF EXISTS `proposalApp_proposalviewer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposalApp_proposalviewer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `proposal_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `proposalApp_proposalviewer_proposal_id_user_id_84678673_uniq` (`proposal_id`,`user_id`),
  KEY `proposalApp_proposalviewer_user_id_e3251d43_fk_userApp_user_id` (`user_id`),
  KEY `proposalApp_proposa_1784a2_idx` (`proposal_id`,`user_id`),
  CONSTRAINT `proposalApp_proposal_proposal_id_01e815bf_fk_proposalA` FOREIGN KEY (`proposal_id`) REFERENCES `proposalApp_proposal` (`id`),
  CONSTRAINT `proposalApp_proposalviewer_user_id_e3251d43_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prospectApp_prospect`
--

DROP TABLE IF EXISTS `prospectApp_prospect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prospectApp_prospect` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `full_name` varchar(120) NOT NULL,
  `company_name` varchar(160) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(40) NOT NULL,
  `address1` varchar(160) NOT NULL,
  `address2` varchar(160) NOT NULL,
  `city` varchar(80) NOT NULL,
  `state` varchar(80) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `country` varchar(60) NOT NULL,
  `website_url` varchar(300) NOT NULL,
  `notes` longtext NOT NULL,
  `status` varchar(3) NOT NULL,
  `tags` varchar(200) NOT NULL,
  `last_contacted_at` datetime(6) DEFAULT NULL,
  `next_follow_up_at` datetime(6) DEFAULT NULL,
  `do_not_contact` tinyint(1) NOT NULL,
  `unsubscribe_token` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `unsubscribe_token` (`unsubscribe_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ticketApp_ticket`
--

DROP TABLE IF EXISTS `ticketApp_ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticketApp_ticket` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `public_key` varchar(24) NOT NULL,
  `subject` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `status` varchar(12) NOT NULL,
  `priority` varchar(10) NOT NULL,
  `category` varchar(10) NOT NULL,
  `last_client_reply_at` datetime(6) DEFAULT NULL,
  `closed_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `assigned_to_id` bigint DEFAULT NULL,
  `company_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `customer_user_id` bigint DEFAULT NULL,
  `project_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `public_key` (`public_key`),
  KEY `ticketApp_ticket_created_by_id_28baa308_fk_userApp_user_id` (`created_by_id`),
  KEY `ticketApp_ticket_customer_user_id_51638bbf_fk_userApp_user_id` (`customer_user_id`),
  KEY `ticketApp_ticket_project_id_0aa4ef8c_fk_projectApp_project_id` (`project_id`),
  KEY `ticketApp_t_company_d71f9b_idx` (`company_id`,`status`),
  KEY `ticketApp_t_assigne_c2d8c7_idx` (`assigned_to_id`,`status`),
  KEY `ticketApp_t_public__1bc233_idx` (`public_key`),
  CONSTRAINT `ticketApp_ticket_assigned_to_id_78f9b3d2_fk_userApp_user_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `ticketApp_ticket_company_id_cadff680_fk_companyApp_company_id` FOREIGN KEY (`company_id`) REFERENCES `companyApp_company` (`id`),
  CONSTRAINT `ticketApp_ticket_created_by_id_28baa308_fk_userApp_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `ticketApp_ticket_customer_user_id_51638bbf_fk_userApp_user_id` FOREIGN KEY (`customer_user_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `ticketApp_ticket_project_id_0aa4ef8c_fk_projectApp_project_id` FOREIGN KEY (`project_id`) REFERENCES `projectApp_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ticketApp_ticket_watchers`
--

DROP TABLE IF EXISTS `ticketApp_ticket_watchers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticketApp_ticket_watchers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ticket_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticketApp_ticket_watchers_ticket_id_user_id_3f87314a_uniq` (`ticket_id`,`user_id`),
  KEY `ticketApp_ticket_watchers_user_id_da3524d2_fk_userApp_user_id` (`user_id`),
  CONSTRAINT `ticketApp_ticket_wat_ticket_id_ffaa4ad1_fk_ticketApp` FOREIGN KEY (`ticket_id`) REFERENCES `ticketApp_ticket` (`id`),
  CONSTRAINT `ticketApp_ticket_watchers_user_id_da3524d2_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ticketApp_ticketattachment`
--

DROP TABLE IF EXISTS `ticketApp_ticketattachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticketApp_ticketattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `original_name` varchar(200) NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `message_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ticketApp_ticketatta_message_id_f9597ace_fk_ticketApp` (`message_id`),
  CONSTRAINT `ticketApp_ticketatta_message_id_f9597ace_fk_ticketApp` FOREIGN KEY (`message_id`) REFERENCES `ticketApp_ticketmessage` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ticketApp_ticketevent`
--

DROP TABLE IF EXISTS `ticketApp_ticketevent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticketApp_ticketevent` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `kind` varchar(12) NOT NULL,
  `at` datetime(6) NOT NULL,
  `data` json DEFAULT NULL,
  `actor_id` bigint DEFAULT NULL,
  `ticket_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ticketApp_ticketevent_actor_id_e6c795ea_fk_userApp_user_id` (`actor_id`),
  KEY `ticketApp_ticketevent_ticket_id_6f0ae0aa_fk_ticketApp_ticket_id` (`ticket_id`),
  CONSTRAINT `ticketApp_ticketevent_actor_id_e6c795ea_fk_userApp_user_id` FOREIGN KEY (`actor_id`) REFERENCES `userApp_user` (`id`),
  CONSTRAINT `ticketApp_ticketevent_ticket_id_6f0ae0aa_fk_ticketApp_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `ticketApp_ticket` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ticketApp_ticketmessage`
--

DROP TABLE IF EXISTS `ticketApp_ticketmessage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticketApp_ticketmessage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `author_kind` varchar(8) NOT NULL,
  `body` longtext NOT NULL,
  `is_internal` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `author_id` bigint DEFAULT NULL,
  `ticket_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ticketApp_ticketmessage_author_id_12b0c730_fk_userApp_user_id` (`author_id`),
  KEY `ticketApp_ticketmess_ticket_id_16dac3f2_fk_ticketApp` (`ticket_id`),
  CONSTRAINT `ticketApp_ticketmess_ticket_id_16dac3f2_fk_ticketApp` FOREIGN KEY (`ticket_id`) REFERENCES `ticketApp_ticket` (`id`),
  CONSTRAINT `ticketApp_ticketmessage_author_id_12b0c730_fk_userApp_user_id` FOREIGN KEY (`author_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userApp_clientprofile`
--

DROP TABLE IF EXISTS `userApp_clientprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userApp_clientprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `profile_image` varchar(100) DEFAULT NULL,
  `company_name` varchar(200) NOT NULL,
  `company_email` varchar(254) NOT NULL,
  `phone` varchar(30) NOT NULL,
  `address_line1` varchar(200) NOT NULL,
  `address_line2` varchar(200) NOT NULL,
  `city` varchar(120) NOT NULL,
  `state_region` varchar(120) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `country` varchar(120) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `userApp_clientprofile_user_id_960b1da5_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userApp_employeeprofile`
--

DROP TABLE IF EXISTS `userApp_employeeprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userApp_employeeprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `profile_image` varchar(100) DEFAULT NULL,
  `job_title` varchar(120) NOT NULL,
  `work_email` varchar(254) NOT NULL,
  `work_phone` varchar(30) NOT NULL,
  `discord_handle` varchar(60) NOT NULL,
  `address_line1` varchar(200) NOT NULL,
  `address_line2` varchar(200) NOT NULL,
  `city` varchar(120) NOT NULL,
  `state_region` varchar(120) NOT NULL,
  `postal_code` varchar(20) NOT NULL,
  `country` varchar(120) NOT NULL,
  `notes_internal` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `userApp_employeeprofile_user_id_0b843a66_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userApp_user`
--

DROP TABLE IF EXISTS `userApp_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userApp_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) NOT NULL,
  `role` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userApp_user_groups`
--

DROP TABLE IF EXISTS `userApp_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userApp_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userApp_user_groups_user_id_group_id_cc6bd041_uniq` (`user_id`,`group_id`),
  KEY `userApp_user_groups_group_id_2977c7ea_fk_auth_group_id` (`group_id`),
  CONSTRAINT `userApp_user_groups_group_id_2977c7ea_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `userApp_user_groups_user_id_fb2a0585_fk_userApp_user_id` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userApp_user_user_permissions`
--

DROP TABLE IF EXISTS `userApp_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userApp_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userApp_user_user_permis_user_id_permission_id_be62a0c2_uniq` (`user_id`,`permission_id`),
  KEY `userApp_user_user_pe_permission_id_e3916d6c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `userApp_user_user_pe_permission_id_e3916d6c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `userApp_user_user_pe_user_id_b2934d1b_fk_userApp_u` FOREIGN KEY (`user_id`) REFERENCES `userApp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-24 12:05:17
