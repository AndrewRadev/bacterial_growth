import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE PageVisitCounters (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            counts JSON NOT NULL DEFAULT (json_object()),

            startTimestamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            endTimestamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE PageVisitCounters;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
