import json

import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE MeasurementTechniques
        CHANGE studyUniqueId studyUniqueId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD studyId VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD CONSTRAINT MeasurementTechniques_studyId
            FOREIGN KEY (studyId)
            REFERENCES Studies (publicId)
            ON DELETE CASCADE ON UPDATE CASCADE
    """
    conn.execute(sql.text(query))

    query = "SELECT uuid, publicId FROM Studies"
    for (study_uuid, study_id) in conn.execute(sql.text(query)).all():
        query = """
            UPDATE MeasurementTechniques
            SET studyId = :study_id
            WHERE studyUniqueID = :study_uuid
        """
        conn.execute(sql.text(query), {
            'study_id': study_id,
            'study_uuid': study_uuid,
        })


def down(conn):
    query = """
        ALTER TABLE MeasurementTechniques
        DROP CONSTRAINT MeasurementTechniques_studyId,
        DROP studyId
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
