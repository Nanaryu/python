-- MariaDB dump 10.19  Distrib 10.4.27-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: ks_int
-- ------------------------------------------------------
-- Server version	10.4.27-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `ks_int`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ks_int` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `ks_int`;

--
-- Table structure for table `archiwum`
--

DROP TABLE IF EXISTS `archiwum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `archiwum` (
  `nazwisko` varchar(60) DEFAULT NULL,
  `imie` varchar(40) DEFAULT NULL,
  `data_zlozenia_zamowienia` date DEFAULT NULL,
  `liczba_zamowien` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archiwum`
--

LOCK TABLES `archiwum` WRITE;
/*!40000 ALTER TABLE `archiwum` DISABLE KEYS */;
INSERT INTO `archiwum` VALUES ('Nowak','Jna','2018-03-04',NULL),('Jan','Zdzislaw','2018-05-04',NULL),('Nosacz','Janusz','2018-12-24',NULL),('Jan','Zdzislaw',NULL,1),('Nosacz','Janusz',NULL,1),('Nowak','Jna',NULL,1);
/*!40000 ALTER TABLE `archiwum` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `autor`
--

DROP TABLE IF EXISTS `autor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `autor` (
  `id_autora` int(11) NOT NULL AUTO_INCREMENT,
  `nazwisko` varchar(50) NOT NULL,
  `imie` varchar(30) NOT NULL,
  `narodowosc` varchar(30) DEFAULT NULL,
  `okres_tworzenia` varchar(35) DEFAULT NULL,
  `jezyk` varchar(30) DEFAULT NULL,
  `rodzaj_tworczosci` varchar(35) DEFAULT NULL,
  `osiagniecia` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id_autora`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autor`
--

LOCK TABLES `autor` WRITE;
/*!40000 ALTER TABLE `autor` DISABLE KEYS */;
INSERT INTO `autor` VALUES (1,'Mickiewicz','Adam','polak','1839-1840','polski',NULL,'szczegulne'),(2,'G?owacki','Aleksander','polak','nowalistyczna','polski',NULL,'Lalka'),(3,'wyspia?ski','Stanis?aw','polak','M?oda Polska','polski',NULL,'Wesele');
/*!40000 ALTER TABLE `autor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faktura`
--

DROP TABLE IF EXISTS `faktura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `faktura` (
  `nr_faktury` int(11) NOT NULL AUTO_INCREMENT,
  `sposob_platnosci` varchar(30) DEFAULT NULL,
  `data_wystawienia_faktury` date DEFAULT NULL,
  PRIMARY KEY (`nr_faktury`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faktura`
--

LOCK TABLES `faktura` WRITE;
/*!40000 ALTER TABLE `faktura` DISABLE KEYS */;
INSERT INTO `faktura` VALUES (1,'gotówka','2020-01-10'),(2,'gotówka','2018-12-12'),(3,'karta','2022-10-20'),(4,'karta','2022-08-03'),(5,'gotówka','2023-10-20'),(6,'gotówka','2018-12-02'),(7,'czek','2018-06-04');
/*!40000 ALTER TABLE `faktura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `klient`
--

DROP TABLE IF EXISTS `klient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `klient` (
  `id_klienta` int(11) NOT NULL AUTO_INCREMENT,
  `imie` varchar(40) NOT NULL,
  `nazwisko` varchar(40) NOT NULL,
  `kod_pocztowy` varchar(6) DEFAULT NULL,
  `miejscowosc` varchar(50) DEFAULT 'Warszawa',
  `ulica` varchar(50) DEFAULT NULL,
  `nr_domu` varchar(7) DEFAULT NULL,
  `pesel` varchar(11) NOT NULL,
  `telefon` varchar(12) DEFAULT NULL,
  `adres_e_mail` varchar(70) DEFAULT NULL,
  PRIMARY KEY (`id_klienta`),
  UNIQUE KEY `telefon` (`telefon`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `klient`
--

LOCK TABLES `klient` WRITE;
/*!40000 ALTER TABLE `klient` DISABLE KEYS */;
INSERT INTO `klient` VALUES (1,'Jna','Nowak','33-201','Dlbrowa','Sloneczna','12','00889765432','435634734','mail@wp.pl'),(2,'Zdzislaw','Jan','33-100','Tarnów','Wilniowa','125','00844456432','234543345','maille@wp.pl'),(3,'Janusz','Nosacz','00-550','Wroc?aw','Ogrodowa','5','43844456432','987654321','mailik@wp.pl');
/*!40000 ALTER TABLE `klient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ksiazki`
--

DROP TABLE IF EXISTS `ksiazki`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ksiazki` (
  `id_ksiazki` int(11) NOT NULL AUTO_INCREMENT,
  `tytul` varchar(100) NOT NULL,
  `id_autora` int(11) NOT NULL,
  `cena` decimal(10,0) DEFAULT NULL,
  `wydawnictwo` varchar(20) DEFAULT NULL,
  `temat` varchar(30) DEFAULT NULL,
  `miejsce_wydania` varchar(28) DEFAULT NULL,
  `jezyk_ksiazki` varchar(15) DEFAULT NULL,
  `opis` varchar(100) DEFAULT NULL,
  `rok_wydania` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`id_ksiazki`),
  KEY `k_a_fk` (`id_autora`),
  CONSTRAINT `k_a_fk` FOREIGN KEY (`id_autora`) REFERENCES `autor` (`id_autora`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ksiazki`
--

LOCK TABLES `ksiazki` WRITE;
/*!40000 ALTER TABLE `ksiazki` DISABLE KEYS */;
INSERT INTO `ksiazki` VALUES (1,'Wesele',0,90,'Greg','wesele','warszawa','polski','ksi?zka','1930'),(2,'Katarynka',0,16,'Greg','katarynka','warszawa','polski','Krótka ksi?zka','1980'),(3,'Pan Padeusz',0,160,'Greg','opis','warszawa','polski','D?uga ksi?zka','1900');
/*!40000 ALTER TABLE `ksiazki` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rejestracja_zamowienia`
--

DROP TABLE IF EXISTS `rejestracja_zamowienia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rejestracja_zamowienia` (
  `id_zamowienia` int(11) DEFAULT NULL,
  `id_ksiazki` int(11) DEFAULT NULL,
  `liczba_egz` int(11) DEFAULT NULL,
  KEY `id_zamowienia` (`id_zamowienia`),
  KEY `id_ksiazki` (`id_ksiazki`),
  CONSTRAINT `rejestracja_zamowienia_ibfk_1` FOREIGN KEY (`id_zamowienia`) REFERENCES `zamowienia` (`id_zamowienia`),
  CONSTRAINT `rejestracja_zamowienia_ibfk_2` FOREIGN KEY (`id_ksiazki`) REFERENCES `ksiazki` (`id_ksiazki`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rejestracja_zamowienia`
--

LOCK TABLES `rejestracja_zamowienia` WRITE;
/*!40000 ALTER TABLE `rejestracja_zamowienia` DISABLE KEYS */;
INSERT INTO `rejestracja_zamowienia` VALUES (1,2,3),(2,3,1),(3,1,2);
/*!40000 ALTER TABLE `rejestracja_zamowienia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zamowienia`
--

DROP TABLE IF EXISTS `zamowienia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zamowienia` (
  `id_zamowienia` int(11) NOT NULL AUTO_INCREMENT,
  `data_zlozenia_zamowienia` date DEFAULT NULL,
  `data_wyslania` date DEFAULT NULL,
  `koszt_wysylki` decimal(10,0) DEFAULT NULL,
  `id_klienta` int(11) NOT NULL,
  `id_faktury` int(11) NOT NULL,
  PRIMARY KEY (`id_zamowienia`),
  KEY `id_klienta` (`id_klienta`),
  KEY `id_faktury` (`id_faktury`),
  CONSTRAINT `zamowienia_ibfk_1` FOREIGN KEY (`id_klienta`) REFERENCES `klient` (`id_klienta`),
  CONSTRAINT `zamowienia_ibfk_2` FOREIGN KEY (`id_faktury`) REFERENCES `faktura` (`nr_faktury`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zamowienia`
--

LOCK TABLES `zamowienia` WRITE;
/*!40000 ALTER TABLE `zamowienia` DISABLE KEYS */;
INSERT INTO `zamowienia` VALUES (1,'2018-03-04','2018-03-04',23,1,1),(2,'2018-05-04','2018-05-07',23,2,2),(3,'2018-12-24','2018-12-30',23,3,3);
/*!40000 ALTER TABLE `zamowienia` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-03 11:58:06
