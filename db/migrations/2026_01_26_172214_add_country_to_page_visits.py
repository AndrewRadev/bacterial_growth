import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE PageVisits
        ADD country VARCHAR(255) DEFAULT NULL;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE PageVisits
        DROP country;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
