import sqlalchemy as sql

TECHNIQUE_SHORT_NAMES = {
    'ph':         'pH',
    'fc':         'FC',
    'od':         'OD',
    'plates':     'PC',
    '16s':        '16S-rRNA reads',
    'qpcr':       'qPCR',
    'metabolite': 'Metabolite',
}


def up(conn):
    # Loop through all measurement techniques and create a parent study technique:
    query = """
        SELECT id, type, description, subjectType, units, includeStd, studyId
        FROM MeasurementTechniques
    """

    for row in conn.execute(sql.text(query)).all():
        (
            measurement_technique_id,
            technique_type,
            description,
            subject_type,
            units,
            include_std,
            study_id
        ) = row

        if technique_type in ('fc', '16s', 'qpcr'):
            cell_type = 'live'
        else:
            cell_type = ''

        query = """
            INSERT INTO StudyTechniques (type, description, subjectType, units, includeStd, studyId)
            VALUES (:type, :description, :subject_type, :units, :include_std, :study_id)
        """
        conn.execute(sql.text(query), {
            'type':         technique_type,
            'description':  description,
            'subject_type': subject_type,
            'units':        units,
            'include_std':  include_std,
            'study_id':     study_id,
        })

        (study_technique_id,) = conn.execute(sql.text("SELECT LAST_INSERT_ID()")).one()

        query = """
            UPDATE MeasurementTechniques
            SET
                studyTechniqueId = :study_technique_id,
                cellType = :cell_type
            WHERE id = :measurement_technique_id
        """
        conn.execute(sql.text(query), {
            'measurement_technique_id': measurement_technique_id,
            'study_technique_id':       study_technique_id,
            'cell_type':                cell_type,
        })


def down(conn):
    query = "UPDATE MeasurementTechniques SET studyTechniqueId = NULL"
    conn.execute(sql.text(query))

    query = "DELETE FROM StudyTechniques"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
