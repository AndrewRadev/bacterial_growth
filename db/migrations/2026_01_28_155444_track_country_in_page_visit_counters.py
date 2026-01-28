import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE PageVisitCounters
        CHANGE counts paths JSON NOT NULL DEFAULT (json_object()),
        ADD countries JSON NOT NULL DEFAULT (json_object()),
        ADD totalVisitCount INT NOT NULL DEFAULT 0,
        ADD totalBotVisitCount INT NOT NULL DEFAULT 0,
        ADD totalVisitorCount INT NOT NULL DEFAULT 0,
        ADD totalUserCount INT NOT NULL DEFAULT 0
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE PageVisitCounters
        CHANGE paths counts JSON NOT NULL DEFAULT (json_object()),
        DROP countries,
        DROP totalVisitCount,
        DROP totalBotVisitCount,
        DROP totalVisitorCount,
        DROP totalUserCount
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
