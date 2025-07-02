import sqlalchemy as sql


def up(conn):
    # Clean up entries with starting whitespace
    query = "DELETE from Taxa WHERE ncbiId LIKE ' %'"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Taxa
        MODIFY ncbiId INT NOT NULL
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Taxa
        ADD updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Taxa
        ADD UNIQUE INDEX Taxa_name (name)
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Taxa
        MODIFY ncbiId VARCHAR(50) COLLATE utf8mb4_bin NOT NULL
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Taxa
        DROP updatedAt,
        DROP INDEX Taxa_name
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
