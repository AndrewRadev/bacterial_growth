import sqlalchemy as sql


def up(conn):
    # Drop relationships:
    query = """
        ALTER TABLE Bioreplicates
        DROP CONSTRAINT BioReplicatesPerExperiment_fk_1,
        DROP deprecatedExperimentId
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Perturbations
        DROP CONSTRAINT Perturbation_fk_1,
        DROP deprecatedExperimentId
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ExperimentCompartments
        DROP CONSTRAINT CompartmentsPerExperiment_fk_1,
        DROP deprecatedExperimentId
    """
    conn.execute(sql.text(query))

    # Drop the actual column
    query = """
        ALTER TABLE Experiments
        DROP PRIMARY KEY,
        ADD PRIMARY KEY (publicId),
        DROP id
    """
    conn.execute(sql.text(query))


def down(conn):
    """
    This migration removes `deprecatedExperimentId` columns that we no longer need
    """

    # Restore id column
    query = """
        ALTER TABLE Experiments
        ADD id INT NOT NULL AUTO_INCREMENT,
        DROP PRIMARY KEY,
        ADD PRIMARY KEY (id)
    """
    conn.execute(sql.text(query))

    # Restore relationships:
    query = """
        ALTER TABLE Bioreplicates
        ADD deprecatedExperimentId INT DEFAULT NULL,
        ADD CONSTRAINT BioReplicatesPerExperiment_fk_1
            FOREIGN KEY (deprecatedExperimentId)
            REFERENCES Experiments (id)
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Perturbations
        ADD deprecatedExperimentId INT DEFAULT NULL,
        ADD CONSTRAINT Perturbation_fk_1
            FOREIGN KEY (deprecatedExperimentId)
            REFERENCES Experiments (id)
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ExperimentCompartments
        ADD deprecatedExperimentId INT DEFAULT NULL,
        ADD CONSTRAINT CompartmentsPerExperiment_fk_1
            FOREIGN KEY (deprecatedExperimentId)
            REFERENCES Experiments (id)
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
