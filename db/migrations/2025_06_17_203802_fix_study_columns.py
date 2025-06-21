import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Studies
        CHANGE studyId publicId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        CHANGE studyName name varchar(255) DEFAULT NULL,
        CHANGE studyDescription description TEXT DEFAULT NULL,
        CHANGE studyURL url varchar(255) DEFAULT NULL,
        CHANGE studyUniqueId uuid VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
        CHANGE projectUniqueID projectUuid VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
        CHANGE ownerUniqueID ownerUuid VARCHAR(100) COLLATE utf8mb4_bin
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Studies
        CHANGE publicId studyId varchar(100) COLLATE utf8mb4_bin NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Studies
        CHANGE uuid studyUniqueID VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Studies
        CHANGE projectUuid projectUniqueID VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Studies
        CHANGE ownerUuid ownerUniqueID VARCHAR(100) COLLATE utf8mb4_bin
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Studies
        CHANGE name studyName varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        CHANGE description studyDescription TEXT DEFAULT NULL,
        CHANGE url studyURL varchar(100) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
