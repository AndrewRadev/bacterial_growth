import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Users
        MODIFY orcidToken VARCHAR(100) DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    # Making the orcid token non-null after data has been added may break, so
    # we do nothing
    pass


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
