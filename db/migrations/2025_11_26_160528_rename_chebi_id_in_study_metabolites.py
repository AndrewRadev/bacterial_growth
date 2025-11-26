import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE StudyMetabolites
        RENAME COLUMN chebi_id TO chebiId;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE StudyMetabolites
        RENAME COLUMN chebiId TO chebi_id;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
