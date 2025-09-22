import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Experiments
        DROP CONSTRAINT Experiment_fk_1,
        ADD CONSTRAINT Experiments_communityId
            FOREIGN KEY (communityId)
            REFERENCES Communities (id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE,
        MODIFY communityId INT NOT NULL;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Experiments
        MODIFY communityId INT DEFAULT NULL,
        DROP CONSTRAINT Experiments_communityId,
        ADD CONSTRAINT Experiment_fk_1
            FOREIGN KEY (communityId)
            REFERENCES Communities (id)
            ON DELETE SET NULL
            ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
