import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE ModelingResults
        DROP coefficients,
        DROP fit,
        DROP inputs,
        ADD params JSON DEFAULT (json_object())
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE ModelingResults
        ADD coefficients JSON NOT NULL DEFAULT (json_object()),
        ADD fit JSON NOT NULL DEFAULT (json_object()),
        ADD inputs JSON NOT NULL DEFAULT (json_object()),
        DROP params
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
