import sqlalchemy as sql


def up(conn):
    """
    This migration changes MeasurementContext subject ids for metabolites to
    point to their database ids and not their CHEBI ids. This makes metabolite
    measurements consistent with the others and allows us to simplify the code.
    """

    # Rename the `subjectId` column to `deprecatedSubjectId`, keeping the existing values
    query = """
        ALTER TABLE MeasurementContexts
        CHANGE subjectId deprecatedSubjectId VARCHAR(100) DEFAULT NULL;
    """
    conn.execute(sql.text(query))

    # Add a new `subjectId` that we'll copy from the deprecated one
    query = """
        ALTER TABLE MeasurementContexts
        ADD subjectId INT DEFAULT NULL;
    """
    conn.execute(sql.text(query))

    # Loop through all measurement contexts and either copy the previous value
    # of `subjectId`, or find the metabolite by its CHEBI id and take its
    # database id instead.
    query = "SELECT id, deprecatedSubjectId, subjectType from MeasurementContexts"

    for (id, deprecated_subject_id, subject_type) in conn.execute(sql.text(query)).all():
        if subject_type == 'metabolite':
            metabolite_id = conn.execute(
                sql.text("SELECT id from Metabolites WHERE chebiId = :chebi_id"),
                {'chebi_id': deprecated_subject_id},
            ).scalars().one()

            subject_id = int(metabolite_id)
        else:
            subject_id = int(deprecated_subject_id)

        query = """
            UPDATE MeasurementContexts
            SET subjectId = :subject_id
            WHERE id = :id
        """
        conn.execute(sql.text(query), {
            'id': id,
            'subject_id': subject_id,
        })


def down(conn):
    query = "ALTER TABLE MeasurementContexts DROP subjectId;"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE MeasurementContexts
        CHANGE deprecatedSubjectId subjectId VARCHAR(100) DEFAULT NULL;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
