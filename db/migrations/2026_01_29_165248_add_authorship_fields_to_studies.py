import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Studies
        ADD authors JSON NOT NULL DEFAULT (json_array()),
        ADD citation TEXT DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Studies
        DROP authors,
        DROP citation
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
