import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Projects
        CHANGE projectId publicId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        CHANGE projectName name varchar(255) DEFAULT NULL,
        CHANGE projectDescription description TEXT DEFAULT NULL,
        CHANGE projectUniqueID uuid VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
        CHANGE ownerUniqueID ownerUuid VARCHAR(100) COLLATE utf8mb4_bin
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Projects
        CHANGE publicId projectId varchar(100) COLLATE utf8mb4_bin NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Projects
        CHANGE uuid projectUniqueID VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Projects
        CHANGE ownerUuid ownerUniqueID VARCHAR(100) COLLATE utf8mb4_bin
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Projects
        CHANGE name projectName varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        CHANGE description projectDescription TEXT DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
