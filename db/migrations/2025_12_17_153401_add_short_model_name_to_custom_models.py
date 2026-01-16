import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE CustomModels
        ADD shortName VARCHAR(5)
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE CustomModels
        DROP shortName
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
