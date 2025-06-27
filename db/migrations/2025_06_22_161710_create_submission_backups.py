import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE SubmissionBackups (
            id int NOT NULL AUTO_INCREMENT,
            projectId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            userUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            studyDesign json DEFAULT (json_object()),
            dataFileId int DEFAULT NULL,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE SubmissionBackups"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
