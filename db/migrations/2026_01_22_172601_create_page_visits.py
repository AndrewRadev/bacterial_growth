import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE PageVisits (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            isUser tinyint(1) NOT NULL DEFAULT '0',
            isAdmin tinyint(1) NOT NULL DEFAULT '0',
            isBot tinyint(1) NOT NULL DEFAULT '0',
            uuid VARCHAR(36) NOT NULL,
            path VARCHAR(255) NOT NULL,
            query VARCHAR(255) DEFAULT NULL,
            referrer VARCHAR(255) DEFAULT NULL,
            ip VARCHAR(100) DEFAULT NULL,
            userAgent TEXT DEFAULT NULL,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE PageVisits;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
