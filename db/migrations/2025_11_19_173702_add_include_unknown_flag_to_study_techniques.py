import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE StudyTechniques
        ADD includeUnknown tinyint(1) NOT NULL DEFAULT '0'
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE StudyTechniques
        DROP includeUnknown
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
