import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE ModelingResults
        ADD xValues JSON DEFAULT (json_array()),
        ADD yValues JSON DEFAULT (json_array()),
        ADD yErrors JSON DEFAULT (json_array()),
        ADD customModelId INT DEFAULT NULL,

        ADD CONSTRAINT ModelingResults_customModelId
            FOREIGN KEY (customModelId)
            REFERENCES CustomModels (id)
            ON DELETE CASCADE ON UPDATE CASCADE
        ;
    """
    params = {}

    conn.execute(sql.text(query), params)


def down(conn):
    query = """
        ALTER TABLE ModelingResults
        DROP xValues,
        DROP yValues,
        DROP yErrors,
        DROP CONSTRAINT ModelingResults_customModelId,
        DROP customModelId;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
