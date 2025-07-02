import json

import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE CommunityStrains (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            communityId INT NOT NULL,
            strainId INT NOT NULL,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY CommunityStrains_join (communityId, strainId)
        );
    """
    conn.execute(sql.text(query))

    for community_id in conn.execute(sql.text("SELECT id from Communities")).scalars():
        strain_query = conn.execute(
            sql.text("SELECT strainIds from Communities WHERE id = :c_id"),
            {'c_id': community_id},
        )
        for strain_ids in strain_query.scalars():
            for strain_id in json.loads(strain_ids):
                query = "INSERT INTO CommunityStrains (communityId, strainId) VALUES (:c_id, :s_id)"
                conn.execute(
                    sql.text(query),
                    {'c_id': community_id, 's_id': strain_id}
                )


def down(conn):
    query = "DROP TABLE CommunityStrains"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
