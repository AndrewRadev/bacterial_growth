import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Metabolites
        ADD definition TEXT DEFAULT NULL,
        ADD massIsEstimation tinyint(1) NOT NULL DEFAULT '0'
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Metabolites
        DROP definition,
        DROP massIsEstimation
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
