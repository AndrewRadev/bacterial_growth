import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE CustomModels (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            studyId VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,

            url VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
            name VARCHAR(255) NOT NULL,
            description text DEFAULT NULL,

            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            CONSTRAINT CustomModels_studyId
                FOREIGN KEY (studyId)
                REFERENCES Studies (publicId)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE CustomModels;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
