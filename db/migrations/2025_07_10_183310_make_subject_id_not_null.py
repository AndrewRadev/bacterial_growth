import sqlalchemy as sql


def up(conn):
    query = f"""
        ALTER TABLE MeasurementContexts
        MODIFY subjectId INT NOT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE MeasurementContexts
        MODIFY subjectId INT DEFAULT NULL
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
