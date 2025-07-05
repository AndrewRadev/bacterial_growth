import json

import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE MeasurementContexts
        CHANGE subjectId deprecatedSubjectId VARCHAR(100) DEFAULT NULL;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE MeasurementContexts
        ADD subjectId INT DEFAULT NULL;
    """
    conn.execute(sql.text(query))

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
