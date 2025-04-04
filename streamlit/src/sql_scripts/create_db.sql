DROP DATABASE BacterialGrowth;
CREATE DATABASE BacterialGrowth;
USE BacterialGrowth;

CREATE TABLE IF NOT EXISTS Project (
    projectId VARCHAR(100),
    projectName VARCHAR(100) DEFAULT NULL,
    projectDescription TEXT DEFAULT NULL,
    projectUniqueID VARCHAR(100),
    PRIMARY KEY (projectId),
    UNIQUE (projectName)
);

CREATE TABLE IF NOT EXISTS Study (
    studyId VARCHAR(100),
    projectUniqueID VARCHAR(100),
    studyName VARCHAR(100) DEFAULT NULL,
    studyDescription TEXT DEFAULT NULL,
    studyURL VARCHAR(100) DEFAULT NULL,
    studyUniqueID VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (studyId),
    -- TODO: this should not be unique and it should definitely not be unique
    -- only on the first 255 characters
    UNIQUE (studyDescription(255))
);

CREATE TABLE IF NOT EXISTS Experiments (
    studyId VARCHAR(100),
    experimentUniqueId BIGINT AUTO_INCREMENT,
    experimentId VARCHAR(20),
    experimentDescription TEXT,
    cultivationMode  VARCHAR(50),
    controlDescription TEXT,
    PRIMARY KEY (experimentUniqueId),
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Compartments (
    compartmentUniqueId BIGINT AUTO_INCREMENT PRIMARY KEY,
    studyId VARCHAR(100),
    compartmentId VARCHAR(50) NOT NULL,
    volume FLOAT(7,2) DEFAULT 0,
    pressure FLOAT(7,2) DEFAULT 0,
    stirring_speed FLOAT(7,2) DEFAULT 0,
    stirring_mode VARCHAR(50) DEFAULT '',
    O2 FLOAT(7,2) DEFAULT 0,
    CO2 FLOAT(7,2) DEFAULT 0,
    H2  FLOAT(7,2) DEFAULT 0,
    N2 FLOAT(7,2) DEFAULT 0,
    inoculumConcentration FLOAT(10,2) DEFAULT 0,
    inoculumVolume FLOAT(7,2) DEFAULT 0,
    initialPh FLOAT(7,2) DEFAULT 0,
    initialTemperature FLOAT(7,2) DEFAULT 0,
    carbonSource BOOLEAN DEFAULT FALSE,
    mediaNames VARCHAR(100) NOT NULL,
    -- TODO: this should be nullable
    mediaLink VARCHAR(100),

    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Strains (
    studyId VARCHAR(100),
    memberId VARCHAR(50),
    defined BOOLEAN DEFAULT FALSE,
    memberName TEXT,
    strainId BIGINT AUTO_INCREMENT PRIMARY KEY,
    NCBId INT,
    descriptionMember TEXT,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Community (
    studyId VARCHAR(100),
    comunityUniqueId BIGINT AUTO_INCREMENT PRIMARY KEY,
    comunityId VARCHAR(50) NOT NULL,
    strainId BIGINT,
    UNIQUE(comunityId,strainId),
    FOREIGN KEY (strainId) REFERENCES Strains (strainId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Metabolites (
    chebi_id VARCHAR(255) NOT NULL,
    metabo_name VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (chebi_id)
);
-- This is needed to enable drop/add constraints/foreign keys
CREATE UNIQUE INDEX idx_chebi_id ON Metabolites(chebi_id);


CREATE TABLE IF NOT EXISTS Taxa (
    tax_id VARCHAR(255),
    tax_names VARCHAR(255),
    PRIMARY KEY (tax_id)
);

CREATE TABLE IF NOT EXISTS MetaboliteSynonym (
    syn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    synonym_value VARCHAR(255) DEFAULT NULL,
    chebi_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (chebi_id) REFERENCES Metabolites(chebi_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE CompartmentsPerExperiment (
    studyId VARCHAR(100),
    experimentUniqueId BIGINT,
    experimentId VARCHAR(100) NOT NULL,
    compartmentUniqueId BIGINT,
    compartmentId VARCHAR(100) NOT NULL,
    comunityUniqueId BIGINT,
    comunityId VARCHAR(100) NOT NULL,
    PRIMARY KEY (experimentUniqueId, compartmentUniqueId,comunityUniqueId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (compartmentUniqueId) REFERENCES Compartments(compartmentUniqueId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (comunityUniqueId) REFERENCES Community(comunityUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE TechniquesPerExperiment (
    studyId VARCHAR(100),
    experimentUniqueId BIGINT,
    experimentId VARCHAR(100) NOT NULL,
    technique VARCHAR(100),
    techniqueUnit VARCHAR(100),
    PRIMARY KEY (experimentUniqueId, technique, techniqueUnit),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE BioReplicatesPerExperiment (
    studyId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId BIGINT AUTO_INCREMENT PRIMARY KEY,
    bioreplicateId VARCHAR(100),
    experimentUniqueId BIGINT,
    experimentId VARCHAR(100) NOT NULL,
    controls BOOLEAN DEFAULT FALSE,
    OD BOOLEAN DEFAULT FALSE,
    OD_std BOOLEAN DEFAULT FALSE,
    Plate_counts BOOLEAN DEFAULT FALSE,
    Plate_counts_std BOOLEAN DEFAULT FALSE,
    pH BOOLEAN DEFAULT FALSE,
    UNIQUE (studyId, bioreplicateId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId)  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE BioReplicatesMetadata (
    studyId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId BIGINT,
    bioreplicateId VARCHAR(100),
    biosampleLink TEXT,
    bioreplicateDescrition TEXT,

    -- TODO: bioreplicateId can't be unique
    PRIMARY KEY (bioreplicateUniqueId),

    UNIQUE (studyId, bioreplicateUniqueId),
    FOREIGN KEY (bioreplicateUniqueId) REFERENCES BioReplicatesPerExperiment (bioreplicateUniqueId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId)  ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Perturbation (
    studyId VARCHAR(100),
    perturbationUniqueid BIGINT AUTO_INCREMENT,
    perturbationId VARCHAR(100) NOT NULL,
    experimentUniqueId BIGINT,
    experimentId VARCHAR(100) NOT NULL,
    OLDCompartmentId VARCHAR(100),
    OLDComunityId VARCHAR(100),
    NEWCompartmentId VARCHAR(100),
    NEWComunityId VARCHAR(100),
    perturbationDescription TEXT,
    perturbationMinimumValue DECIMAL(10, 2),
    perturbationMaximumValue DECIMAL(10, 2),
    perturbationStartTime TIME,
    perturbationEndTime TIME,
    PRIMARY KEY (perturbationUniqueid),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS MetabolitePerExperiment (
    studyId VARCHAR(100),
    experimentUniqueId BIGINT,
    experimentId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId BIGINT,
    bioreplicateId VARCHAR(100),
    metabo_name VARCHAR(255) DEFAULT NULL,
    chebi_id VARCHAR(255) NOT NULL,
    -- NOTE: experimentId can't be primary key, the experiment id is not unique
    PRIMARY KEY (experimentUniqueId, bioreplicateId, chebi_id),
    FOREIGN KEY (chebi_id) REFERENCES Metabolites(chebi_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);
-- CREATE UNIQUE INDEX idx_met_exp_id ON MetabolitePerExperiment(experimentUniqueId, bioreplicateId, chebi_id);

CREATE TABLE IF NOT EXISTS Abundances (
    studyId VARCHAR(100),
    experimentUniqueId BIGINT,
    experimentId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId BIGINT,
    bioreplicateId VARCHAR(100),
    strainId BIGINT,
    memberId VARCHAR(255),
    PRIMARY KEY  (experimentId, bioreplicateId, memberId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS FC_Counts (
    studyId VARCHAR(100),
    experimentUniqueId BIGINT,
    experimentId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId BIGINT,
    bioreplicateId VARCHAR(100),
    strainId BIGINT,
    memberId VARCHAR(255),
    PRIMARY KEY  (experimentId, bioreplicateId, memberId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);
