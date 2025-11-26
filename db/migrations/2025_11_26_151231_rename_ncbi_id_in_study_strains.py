import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Strains
        RENAME COLUMN NCBId TO ncbiId;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Strains
        RENAME COLUMN ncbiId TO NCBId;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
