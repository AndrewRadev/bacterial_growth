import sqlalchemy as sql


def up(conn):
    """
    This migration ensures that the three relationships of Experiments are all
    connected to their parent Experiment by its `publicId` and not by its
    auto-incrementing `id`. This is done for consistency with studies and
    projects.
    """

    for table in ['Bioreplicates', 'Perturbations', 'ExperimentCompartments']:
        # Deprecate the existing column
        query = f"""
            ALTER TABLE {table}
            CHANGE experimentId deprecatedExperimentId INT DEFAULT NULL
        """
        conn.execute(sql.text(query))

        # Create the new column and a foreign key to Experiments
        query = f"""
            ALTER TABLE {table}
            ADD COLUMN experimentId VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL,
            ADD CONSTRAINT {table}_experimentId
                FOREIGN KEY (experimentId)
                REFERENCES Experiments (publicId)
                ON DELETE CASCADE ON UPDATE CASCADE
        """
        conn.execute(sql.text(query))

        # Find the experiments by the value in the deprecated column, get their
        # corresponding publicId, and set it in the new column.
        query = f"SELECT DISTINCT deprecatedExperimentId from {table}"
        for (deprecated_experiment_id,) in conn.execute(sql.text(query)).all():
            experiment_public_id = conn.execute(
                sql.text("SELECT publicId FROM Experiments WHERE id = :id"),
                {'id': deprecated_experiment_id},
            ).scalars().one()
            query = f"""
                UPDATE {table}
                SET experimentId = :public_id
                WHERE deprecatedExperimentId = :id
            """
            conn.execute(sql.text(query), {
                'id': deprecated_experiment_id,
                'public_id': experiment_public_id,
            })

        # After filling all the values, ensure that `experimentId` is not nullable
        query = f"""
            ALTER TABLE {table}
            MODIFY experimentId VARCHAR(100) COLLATE utf8mb4_bin NOT NULL
        """
        conn.execute(sql.text(query))


def down(conn):
    for table in ['Bioreplicates', 'Perturbations', 'ExperimentCompartments']:
        query = f"""
            ALTER TABLE {table}
            DROP CONSTRAINT {table}_experimentId,
            DROP COLUMN experimentId,
            CHANGE deprecatedExperimentId experimentId INT DEFAULT NULL
        """
        conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
