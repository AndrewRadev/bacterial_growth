import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE ModelingResults
        MODIFY requestId INT DEFAULT NULL;
    """
    conn.execute(sql.text(query))


def down(conn):
    # We can't restore non-nullability
    pass


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
