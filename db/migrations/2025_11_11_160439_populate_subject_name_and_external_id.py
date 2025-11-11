import sqlalchemy as sql


def up(conn):
    query = "SELECT id, subjectId, subjectType from MeasurementContexts"
    for (mc_id, subject_id, subject_type) in conn.execute(sql.text(query)).all():
        external_id = None

        if subject_type == 'bioreplicate':
            query = "SELECT name from Bioreplicates where id = :id"
            (subject_name,) = conn.execute(sql.text(query), {'id': subject_id}).one()
        elif subject_type == 'strain':
            query = "SELECT name, NCBId from Strains where id = :id"
            (subject_name, external_id) = conn.execute(sql.text(query), {'id': subject_id}).one()
            external_id = f"NCBI:{external_id}"
        elif subject_type == 'metabolite':
            query = "SELECT name, chebiId from Metabolites where id = :id"
            (subject_name, external_id) = conn.execute(sql.text(query), {'id': subject_id}).one()

        query = """
            UPDATE MeasurementContexts
            SET
                subjectName = :subject_name,
                subjectExternalId = :external_id
            WHERE MeasurementContexts.id = :id
        """
        conn.execute(sql.text(query), {
            'id': mc_id,
            'subject_name': subject_name,
            'external_id': external_id,
        })


def down(conn):
    query = "UPDATE MeasurementContexts SET subjectName = NULL, subjectExternalId = NULL"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
