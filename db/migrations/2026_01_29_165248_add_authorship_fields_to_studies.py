import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Studies
        ADD citation VARCHAR(255) DEFAULT NULL,
        ADD bibtexFile TEXT DEFAULT NULL,
        ADD authors JSON NOT NULL DEFAULT (json_array())
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Studies
        DROP citation,
        DROP bibtexFile,
        DROP authors;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
