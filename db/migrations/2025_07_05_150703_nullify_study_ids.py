import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Bioreplicates
        MODIFY studyId VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Bioreplicates
        MODIFY studyId VARCHAR(100) COLLATE utf8mb4_bin NOT NULL
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
