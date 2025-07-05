import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Perturbations
        ADD endTimeInSeconds INT DEFAULT NULL,
        CHANGE startTimepoint startTimeInSeconds INT NOT NULL
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Perturbations
        DROP endTimeInSeconds,
        CHANGE startTimeInSeconds startTimepoint int NOT NULL
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
