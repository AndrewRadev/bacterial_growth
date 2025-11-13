import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Metabolites
        MODIFY name varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Metabolites
        MODIFY name varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
