import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE CustomModels
        ADD coefficientNames json DEFAULT (json_array()),
        ADD fitNames json DEFAULT (json_array())
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE CustomModels
        DROP coefficientNames,
        DROP fitNames
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
