import sqlalchemy as sql

# TODO label, subtype (live, etc)

def up(conn):
    query = """
        ALTER TABLE MeasurementTechniques
        ADD studyTechniqueId INT DEFAULT NULL,
        ADD subtype varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
        ADD label VARCHAR(100) DEFAULT NULL,
        DROP CONSTRAINT MeasurementTechniques_studyUniqueId,
        DROP studyUniqueId,
        DROP strainIds,
        ADD INDEX MeasurementTechniques_studyTechniqueId (studyTechniqueId),
        ADD CONSTRAINT MeasurementTechniques_studyTechniqueId
            FOREIGN KEY (studyTechniqueId) REFERENCES StudyTechniques (id)
            ON DELETE CASCADE ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE MeasurementTechniques
        DROP CONSTRAINT MeasurementTechniques_studyTechniqueId,
        DROP studyTechniqueId,
        DROP subtype,
        DROP label,
        ADD strainIds json NOT NULL DEFAULT (json_array()),
        ADD studyUniqueId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
        ADD CONSTRAINT MeasurementTechniques_studyUniqueId
            FOREIGN KEY (studyUniqueId) REFERENCES Studies (uuid)
            ON DELETE CASCADE ON UPDATE CASCADE
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
