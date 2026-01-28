-- MySQL dump 10.13  Distrib 8.4.0, for Linux (x86_64)
--
-- Host: localhost    Database: BacterialGrowth
-- ------------------------------------------------------
-- Server version	8.4.4

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Bioreplicates`
--

DROP TABLE IF EXISTS Bioreplicates;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Bioreplicates (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  biosampleUrl text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  position varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  isControl tinyint(1) NOT NULL DEFAULT '0',
  isBlank tinyint(1) NOT NULL DEFAULT '0',
  calculationType varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  experimentId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY studyId (studyId,`name`),
  KEY Bioreplicates_experimentId (experimentId),
  CONSTRAINT Bioreplicates_experimentId FOREIGN KEY (experimentId) REFERENCES Experiments (publicId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT BioReplicatesPerExperiment_fk_2 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Communities`
--

DROP TABLE IF EXISTS Communities;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Communities (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  strainIds json NOT NULL DEFAULT (json_array()),
  PRIMARY KEY (id),
  KEY fk_2 (studyId),
  CONSTRAINT Community_fk_2 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CommunityStrains`
--

DROP TABLE IF EXISTS CommunityStrains;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE CommunityStrains (
  id int NOT NULL AUTO_INCREMENT,
  communityId int NOT NULL,
  strainId int NOT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY CommunityStrains_join (communityId,strainId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Compartments`
--

DROP TABLE IF EXISTS Compartments;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Compartments (
  id int NOT NULL AUTO_INCREMENT,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  volume decimal(7,2) DEFAULT NULL,
  pressure decimal(7,2) DEFAULT NULL,
  stirringSpeed float(7,2) DEFAULT NULL,
  stirringMode varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  O2 decimal(7,2) DEFAULT NULL,
  CO2 decimal(7,2) DEFAULT NULL,
  H2 decimal(7,2) DEFAULT NULL,
  N2 decimal(7,2) DEFAULT NULL,
  inoculumConcentration decimal(20,3) DEFAULT NULL,
  inoculumVolume decimal(7,2) DEFAULT NULL,
  initialPh decimal(7,2) DEFAULT NULL,
  initialTemperature decimal(7,2) DEFAULT NULL,
  carbonSource tinyint(1) DEFAULT '0',
  mediumName varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  mediumUrl varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  dilutionRate decimal(7,3) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY fk_1 (studyId),
  CONSTRAINT Compartments_fk_1 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CustomModels`
--

DROP TABLE IF EXISTS CustomModels;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE CustomModels (
  id int NOT NULL AUTO_INCREMENT,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `description` text,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  shortName varchar(5) DEFAULT NULL,
  coefficientNames json DEFAULT (json_array()),
  fitNames json DEFAULT (json_array()),
  PRIMARY KEY (id),
  KEY CustomModels_studyId (studyId),
  CONSTRAINT CustomModels_studyId FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ExcelFiles`
--

DROP TABLE IF EXISTS ExcelFiles;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ExcelFiles (
  id int NOT NULL AUTO_INCREMENT,
  filename varchar(255) DEFAULT NULL,
  size int NOT NULL,
  content longblob NOT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ExperimentCompartments`
--

DROP TABLE IF EXISTS ExperimentCompartments;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ExperimentCompartments (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  compartmentId int NOT NULL,
  id bigint unsigned NOT NULL AUTO_INCREMENT,
  experimentId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (id),
  KEY fk_2 (compartmentId),
  KEY fk_4 (studyId),
  KEY ExperimentCompartments_experimentId (experimentId),
  CONSTRAINT CompartmentsPerExperiment_fk_2 FOREIGN KEY (compartmentId) REFERENCES Compartments (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CompartmentsPerExperiment_fk_4 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT ExperimentCompartments_experimentId FOREIGN KEY (experimentId) REFERENCES Experiments (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Experiments`
--

DROP TABLE IF EXISTS Experiments;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Experiments (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  cultivationMode varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  communityId int DEFAULT NULL,
  publicId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (publicId),
  UNIQUE KEY Experiments_publicId (publicId),
  KEY fk_1 (studyId),
  KEY Experiment_fk_1 (communityId),
  CONSTRAINT Experiment_fk_1 FOREIGN KEY (communityId) REFERENCES Communities (id) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT Experiments_fk_1 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MeasurementContexts`
--

DROP TABLE IF EXISTS MeasurementContexts;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE MeasurementContexts (
  id int NOT NULL AUTO_INCREMENT,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  bioreplicateId int NOT NULL,
  compartmentId int NOT NULL,
  techniqueId int DEFAULT NULL,
  deprecatedSubjectId varchar(100) DEFAULT NULL,
  subjectType varchar(100) NOT NULL,
  calculationType varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  subjectId int NOT NULL,
  subjectName varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  subjectExternalId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (id),
  KEY MeasurementContexts_fk_1 (bioreplicateId),
  KEY MeasurementContexts_fk_2 (compartmentId),
  KEY MeasurementContexts_fk_3 (techniqueId),
  KEY MeasurementContexts_fk_4 (studyId),
  CONSTRAINT MeasurementContexts_fk_1 FOREIGN KEY (bioreplicateId) REFERENCES Bioreplicates (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MeasurementContexts_fk_2 FOREIGN KEY (compartmentId) REFERENCES Compartments (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MeasurementContexts_fk_3 FOREIGN KEY (techniqueId) REFERENCES MeasurementTechniques (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MeasurementContexts_fk_4 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MeasurementTechniques`
--

DROP TABLE IF EXISTS MeasurementTechniques;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE MeasurementTechniques (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  subjectType varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  units varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `description` text,
  includeStd tinyint(1) NOT NULL DEFAULT '0',
  metaboliteIds json DEFAULT (json_array()),
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyTechniqueId int DEFAULT NULL,
  cellType varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (id),
  KEY MeasurementTechniques_studyId (studyId),
  KEY MeasurementTechniques_studyTechniqueId (studyTechniqueId),
  CONSTRAINT MeasurementTechniques_studyId FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MeasurementTechniques_studyTechniqueId FOREIGN KEY (studyTechniqueId) REFERENCES StudyTechniques (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Measurements`
--

DROP TABLE IF EXISTS Measurements;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Measurements (
  id int NOT NULL AUTO_INCREMENT,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  timeInSeconds int NOT NULL,
  `value` decimal(20,3) DEFAULT NULL,
  std decimal(20,3) DEFAULT NULL,
  contextId int NOT NULL,
  PRIMARY KEY (id),
  KEY studyId (studyId),
  KEY Measurements_fk_1 (contextId),
  CONSTRAINT Measurements_fk_1 FOREIGN KEY (contextId) REFERENCES MeasurementContexts (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Metabolites`
--

DROP TABLE IF EXISTS Metabolites;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Metabolites (
  chebiId varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  averageMass decimal(10,5) DEFAULT NULL,
  `definition` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  massIsEstimation tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  UNIQUE KEY Metabolites_chebiId (chebiId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MigrationVersions`
--

DROP TABLE IF EXISTS MigrationVersions;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE MigrationVersions (
  id bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  migratedAt datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ModelingRequests`
--

DROP TABLE IF EXISTS ModelingRequests;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ModelingRequests (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  jobUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  state varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `error` text,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (id),
  KEY ModelingRequests_studyId (studyId),
  CONSTRAINT ModelingRequests_studyId FOREIGN KEY (studyId) REFERENCES Studies (publicId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ModelingResults`
--

DROP TABLE IF EXISTS ModelingResults;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ModelingResults (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  requestId int DEFAULT NULL,
  state varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `error` text,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  calculatedAt datetime DEFAULT NULL,
  measurementContextId int NOT NULL,
  rSummary text,
  params json DEFAULT (json_object()),
  xValues json DEFAULT (json_array()),
  yValues json DEFAULT (json_array()),
  yErrors json DEFAULT (json_array()),
  customModelId int DEFAULT NULL,
  publishedAt datetime DEFAULT NULL,
  PRIMARY KEY (id),
  KEY Calculations_calculationTechniqueId (requestId),
  KEY ModelingResults_customModelId (customModelId),
  CONSTRAINT Calculations_calculationTechniqueId FOREIGN KEY (requestId) REFERENCES ModelingRequests (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT ModelingResults_customModelId FOREIGN KEY (customModelId) REFERENCES CustomModels (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PageVisitCounters`
--

DROP TABLE IF EXISTS PageVisitCounters;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE PageVisitCounters (
  id int NOT NULL AUTO_INCREMENT,
  paths json NOT NULL DEFAULT (json_object()),
  startTimestamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  endTimestamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  countries json NOT NULL DEFAULT (json_object()),
  totalVisitCount int NOT NULL DEFAULT '0',
  totalBotVisitCount int NOT NULL DEFAULT '0',
  totalVisitorCount int NOT NULL DEFAULT '0',
  totalUserCount int NOT NULL DEFAULT '0',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PageVisits`
--

DROP TABLE IF EXISTS PageVisits;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE PageVisits (
  id int NOT NULL AUTO_INCREMENT,
  isUser tinyint(1) NOT NULL DEFAULT '0',
  isAdmin tinyint(1) NOT NULL DEFAULT '0',
  isBot tinyint(1) NOT NULL DEFAULT '0',
  uuid varchar(36) NOT NULL,
  `path` varchar(255) NOT NULL,
  `query` varchar(255) DEFAULT NULL,
  referrer varchar(255) DEFAULT NULL,
  ip varchar(100) DEFAULT NULL,
  userAgent text,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  country varchar(255) DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Perturbations`
--

DROP TABLE IF EXISTS Perturbations;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Perturbations (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  id int NOT NULL AUTO_INCREMENT,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  removedCompartmentId int DEFAULT NULL,
  addedCompartmentId int DEFAULT NULL,
  oldCommunityId int DEFAULT NULL,
  newCommunityId int DEFAULT NULL,
  startTimeInSeconds int NOT NULL,
  endTimeInSeconds int DEFAULT NULL,
  experimentId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (id),
  KEY fk_2 (studyId),
  KEY Perturbations_experimentId (experimentId),
  CONSTRAINT Perturbation_fk_2 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Perturbations_experimentId FOREIGN KEY (experimentId) REFERENCES Experiments (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ProjectUsers`
--

DROP TABLE IF EXISTS ProjectUsers;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ProjectUsers (
  id int NOT NULL AUTO_INCREMENT,
  projectUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY projectUniqueID (projectUniqueID),
  CONSTRAINT projectUniqueID FOREIGN KEY (projectUniqueID) REFERENCES Projects (uuid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Projects`
--

DROP TABLE IF EXISTS Projects;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Projects (
  publicId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  uuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  ownerUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (publicId),
  UNIQUE KEY projectUniqueID (uuid),
  UNIQUE KEY projectName (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Studies`
--

DROP TABLE IF EXISTS Studies;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Studies (
  publicId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  projectUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  uuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  timeUnits varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  publishableAt datetime DEFAULT NULL,
  publishedAt datetime DEFAULT NULL,
  embargoExpiresAt datetime DEFAULT NULL,
  ownerUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (publicId),
  UNIQUE KEY studyUniqueID (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `StudyMetabolites`
--

DROP TABLE IF EXISTS StudyMetabolites;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE StudyMetabolites (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  chebiId varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  id bigint unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id),
  KEY fk_1 (chebiId),
  KEY fk_3 (studyId),
  CONSTRAINT MetabolitePerExperiment_fk_1 FOREIGN KEY (chebiId) REFERENCES Metabolites (chebiId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MetabolitePerExperiment_fk_3 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `StudyStrains`
--

DROP TABLE IF EXISTS StudyStrains;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE StudyStrains (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  defined tinyint(1) DEFAULT '0',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  ncbiId int DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  assemblyGenBankId varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (id),
  KEY fk_1 (studyId),
  CONSTRAINT Strains_fk_1 FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `StudyTechniques`
--

DROP TABLE IF EXISTS StudyTechniques;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE StudyTechniques (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `description` text,
  units varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  includeStd tinyint(1) NOT NULL DEFAULT '0',
  label varchar(100) DEFAULT NULL,
  subjectType varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  includeUnknown tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  KEY StudyTechniques_studyId (studyId),
  CONSTRAINT StudyTechniques_studyId FOREIGN KEY (studyId) REFERENCES Studies (publicId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `StudyUsers`
--

DROP TABLE IF EXISTS StudyUsers;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE StudyUsers (
  id int NOT NULL AUTO_INCREMENT,
  studyUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY studyUniqueID (studyUniqueID),
  CONSTRAINT studyUniqueID FOREIGN KEY (studyUniqueID) REFERENCES Studies (uuid) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SubmissionBackups`
--

DROP TABLE IF EXISTS SubmissionBackups;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE SubmissionBackups (
  id int NOT NULL AUTO_INCREMENT,
  projectId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  userUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  studyDesign json DEFAULT (json_object()),
  dataFileId int DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Submissions`
--

DROP TABLE IF EXISTS Submissions;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Submissions (
  id int NOT NULL AUTO_INCREMENT,
  projectUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyDesign json DEFAULT (json_object()),
  studyFileId int DEFAULT NULL,
  dataFileId int DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Taxa`
--

DROP TABLE IF EXISTS Taxa;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Taxa (
  ncbiId int NOT NULL,
  `name` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY Taxa_ncbiId (ncbiId),
  UNIQUE KEY Taxa_name (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS Users;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Users (
  id int NOT NULL AUTO_INCREMENT,
  uuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  orcidId varchar(100) NOT NULL,
  orcidToken varchar(100) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  isAdmin tinyint(1) NOT NULL DEFAULT '0',
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  lastLoginAt datetime DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY Users_uuid (uuid),
  UNIQUE KEY Users_orcidId (orcidId)
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

INSERT INTO MigrationVersions VALUES
(1,'2024_11_11_160324_initial_schema','2025-06-05 16:50:08'),
(2,'2024_11_11_164726_remove_unique_study_description_index','2025-06-05 16:50:08'),
(3,'2024_11_21_115349_allow_null_medialink','2025-06-05 16:50:08'),
(4,'2024_11_21_120444_fix_unique_primary_keys','2025-06-05 16:50:09'),
(5,'2025_01_30_152951_fix_bioreplicates_metadata_unique_id','2025-06-05 16:50:09'),
(6,'2025_02_04_134239_rename-chebi-id','2025-06-05 16:50:09'),
(7,'2025_02_05_134203_make-project-and-study-uuids-unique','2025-06-05 16:50:09'),
(8,'2025_02_12_170210_add-assembly-id-to-strains','2025-06-05 16:50:09'),
(9,'2025_02_13_114748_increase_experiment_id_size','2025-06-05 16:50:09'),
(10,'2025_02_13_120609_rename_comunity_to_community','2025-06-05 16:50:09'),
(11,'2025_02_13_121409_rename_comunity_to_community_2','2025-06-05 16:50:09'),
(12,'2025_02_13_163206_create_measurements','2025-06-05 16:50:09'),
(13,'2025_02_17_161750_remove_duplicated_columns_from_metabolite_per_experiment','2025-06-05 16:50:09'),
(14,'2025_03_11_113040_create_submissions_and_excel_files','2025-06-05 16:50:09'),
(15,'2025_03_21_112110_create_project_and_study_user_join_tables','2025-06-05 16:50:09'),
(16,'2025_03_25_133231_add_user_id_to_new_strains','2025-06-05 16:50:09'),
(17,'2025_03_28_181930_create_measurement_techniques','2025-06-05 16:50:09'),
(18,'2025_03_30_160720_add_technique_id_to_measurements','2025-06-05 16:50:09'),
(19,'2025_04_03_121425_add_time_units_to_study','2025-06-05 16:50:09'),
(20,'2025_04_03_125243_add_timestamps_to_study_and_project','2025-06-05 16:50:09'),
(21,'2025_04_15_112546_add_publishing_related_states_to_studies','2025-06-05 16:50:10'),
(22,'2025_04_24_095808_create_calculation_techniques','2025-06-05 16:50:10'),
(23,'2025_04_25_103658_create_calculations','2025-06-05 16:50:10'),
(24,'2025_04_30_135012_fix_compartments_per_experiment_keys_and_columns','2025-06-05 16:50:10'),
(25,'2025_04_30_142205_fix_compartment_columns','2025-06-05 16:50:10'),
(26,'2025_05_01_172225_fix_community_columns','2025-06-05 16:50:10'),
(27,'2025_05_02_171609_fix_strain_columns','2025-06-05 16:50:10'),
(28,'2025_05_05_104555_fix_experiment_columns','2025-06-05 16:50:10'),
(29,'2025_05_05_130725_fix_experiment_compartments','2025-06-05 16:50:10'),
(30,'2025_05_05_201613_fix_bioreplicate_columns','2025-06-05 16:51:00'),
(31,'2025_05_05_204021_remove_bioreplicate_metadata','2025-06-05 16:51:00'),
(32,'2025_05_09_143613_fix_perturbation_columns','2025-06-05 16:51:01'),
(33,'2025_05_09_185956_remove_position_from_measurements','2025-06-05 16:51:01'),
(34,'2025_05_09_194730_fix_study_metabolite_columns','2025-06-05 16:51:01'),
(35,'2025_05_10_112933_add_compartment_id_to_measurements','2025-06-05 16:51:01'),
(36,'2025_05_11_154801_add_fields_to_bioreplicates','2025-06-05 16:51:01'),
(37,'2025_05_13_172421_drop_unused_tables','2025-06-05 16:51:01'),
(38,'2025_05_15_202520_create_measurement_contexts','2025-06-05 16:51:01'),
(39,'2025_05_15_202707_move_measurement_fields_to_contexts','2025-06-05 16:51:01'),
(40,'2025_05_16_141435_fix_taxon_columns','2025-06-05 16:51:01'),
(41,'2025_05_17_165050_fix_metabolite_columns','2025-06-05 16:51:01'),
(42,'2025_05_18_105334_rename_calculations_to_models','2025-06-05 16:51:02'),
(43,'2025_05_19_170414_add_calculation_types','2025-06-05 16:51:02'),
(44,'2025_05_20_220923_fix_modeling_requests_error_column','2025-06-05 16:51:02'),
(45,'2025_05_21_143554_add_input_params_to_modeling_results','2025-06-05 16:51:02'),
(46,'2025_05_22_235526_add_r_summary_to_modeling_results','2025-06-05 16:51:02'),
(47,'2025_05_25_132228_add_public_id_to_experiments','2025-06-05 16:51:02'),
(48,'2025_06_05_114908_create_users','2025-06-05 16:51:02'),
(49,'2025_06_05_145355_add_owner_to_studies_and_projects','2025-06-05 16:51:02'),
(50,'2025_06_05_150110_rename_study_and_project','2025-06-05 16:51:02'),
(51,'2025_06_17_202034_fix_project_columns','2025-06-22 16:27:52'),
(52,'2025_06_17_203802_fix_study_columns','2025-06-22 16:27:53'),
(53,'2025_06_22_152747_combine_modeling_params','2025-06-22 16:27:54'),
(54,'2025_06_22_161710_create_submission_backups','2025-06-22 16:27:54'),
(55,'2025_06_29_142448_add_fields_to_taxa','2025-07-02 08:53:03'),
(56,'2025_07_02_114751_readd_end_time_to_perturbations','2025-07-05 10:01:35'),
(57,'2025_07_02_174630_create_community_strains','2025-07-05 10:01:35'),
(58,'2025_07_05_121137_fix_metabolite_subject_ids','2025-08-20 12:11:24'),
(59,'2025_07_05_150703_nullify_study_ids','2025-08-20 12:11:24'),
(60,'2025_07_05_153044_fix_measurement_technique_study_ids','2025-08-20 12:11:24'),
(61,'2025_07_09_121550_use_experiment_public_id_as_key','2025-08-20 12:11:25'),
(62,'2025_07_09_124639_remove_deprecated_experiment_id','2025-08-20 12:11:25'),
(63,'2025_07_10_183310_make_subject_id_not_null','2025-08-20 12:11:25'),
(64,'2025_07_13_121621_make_orcid_token_nullable','2025-08-20 12:11:25'),
(65,'2025_10_20_124103_make_last_login_at_nullable','2025-10-20 10:52:18'),
(66,'2025_10_21_163448_add_dilution_rate','2025-10-21 16:31:56'),
(70,'2025_11_10_122037_increase_metabolite_name_length','2025-11-10 11:29:23'),
(71,'2025_11_11_155050_add_subject_name_and_external_id_to_measurement_contexts','2025-11-12 11:06:25'),
(72,'2025_11_11_160439_populate_subject_name_and_external_id','2025-11-12 11:06:28'),
(73,'2025_11_03_160947_create_study_techniques','2025-11-13 14:05:49'),
(74,'2025_11_03_162139_modify_measurement_techniques','2025-11-13 14:05:50'),
(75,'2025_11_03_164617_populate_study_techniques','2025-11-13 14:05:50'),
(76,'2025_11_18_125634_add_more_fields_to_metabolites','2025-11-18 14:20:52'),
(77,'2025_11_19_173702_add_include_unknown_flag_to_study_techniques','2025-11-20 14:00:51'),
(78,'2025_11_26_151231_rename_ncbi_id_in_study_strains','2025-11-27 11:51:23'),
(79,'2025_11_26_151436_rename_strains_to_study_strains','2025-11-27 11:51:23'),
(80,'2025_11_26_160528_rename_chebi_id_in_study_metabolites','2025-11-27 11:51:23'),
(81,'2025_12_08_172450_remove_modeling_request_id_constraint','2025-12-17 15:59:32'),
(82,'2025_12_14_121007_create_custom_models','2025-12-17 15:59:32'),
(83,'2025_12_14_121008_add_custom_upload_modeling_result_fields','2025-12-17 15:59:32'),
(84,'2025_12_14_173844_add_publish_state_to_modeling_result','2025-12-17 15:59:33'),
(85,'2025_12_17_153401_add_short_model_name_to_custom_models','2025-12-17 15:59:33'),
(86,'2026_01_05_113846_add-params-to-custom-models','2026-01-08 13:28:47'),
(90,'2026_01_22_172601_create_page_visits','2026-01-23 10:35:44'),
(93,'2026_01_23_120741_create_page_visit_counters','2026-01-23 13:45:15'),
(95,'2026_01_26_172214_add_country_to_page_visits','2026-01-26 16:22:56'),
(99,'2026_01_28_155444_track_country_in_page_visit_counters','2026-01-28 14:59:27');

