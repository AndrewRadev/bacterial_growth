import sqlalchemy as sql


def up(conn):
    query = "RENAME TABLE Strains TO StudyStrains;"
    conn.execute(sql.text(query))


def down(conn):
    query = "RENAME TABLE StudyStrains TO Strains;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
