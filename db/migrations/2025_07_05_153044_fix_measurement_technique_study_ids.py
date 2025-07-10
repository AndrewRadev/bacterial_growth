import sqlalchemy as sql


def up(conn):
    """
    This migration changes MeasurementTechniques to point to studies by
    `publicId` and not by the private `uuid`. Originally, the intent was to
    have the private ID be the primary key, but in practice, it's fairly
    inconvenient, because we fetch studies by public ID in pages. Let's just
    commit to consistently using `publicId` as the primary key.
    """

    # Allow the `studyUniqueId` field to be null and add a new `studyId` column
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

    # Loop over studies and set the new `studyId` of MeasurementContexts to the
    # public ID of the corresponding Study.
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
