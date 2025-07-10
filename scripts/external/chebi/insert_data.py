import csv
from pathlib import Path

from db import get_session
from app.model.orm import Metabolite

import sqlalchemy as sql
from long_task_printer import LongTask

base_dir_path = Path('var/external_data/chebi/')
data_dump     = base_dir_path / 'data_dump.csv'

# Count the number of lines in the file, should be quick:
with open(data_dump) as f:
    # Number of lines minus the header
    metabolite_count = len(f.readlines()) - 1

long_task = LongTask(total_count=metabolite_count)

all_file_ids = set()

with get_session() as db_session:
    all_db_ids = set(db_session.scalars(sql.select(Metabolite.chebiId)).all())

    with open(data_dump) as f:
        reader = csv.DictReader(f)

        for row in reader:
            chebi_id = f"CHEBI:{row['chebiId']}"
            name     = row['name']
            mass     = row['averageMass']

            all_file_ids.add(chebi_id)

            if mass == '':
                mass = None

            with long_task.measure() as progress:
                existing_metabolite = db_session.scalars(
                    sql.select(Metabolite)
                    .where(Metabolite.chebiId == chebi_id)
                ).one_or_none()

                if existing_metabolite:
                    if existing_metabolite.name == name and existing_metabolite.averageMass == mass:
                        print(f"[{progress}] Working on {(chebi_id, name)}: Skip")
                    else:
                        print(f"[{progress}] Working on {(chebi_id, name)}: Update")
                        existing_metabolite.name = name
                        existing_metabolite.averageMass = mass
                        db_session.add(existing_metabolite)
                        db_session.commit()
                else:
                    print(f"[{progress}] Working on: {(chebi_id, name)}: Insert")
                    metabolite = Metabolite(
                        chebiId=chebi_id,
                        name=name,
                        averageMass=mass,
                    )
                    db_session.add(metabolite)
                    db_session.commit()

    print(f"Missing IDs in the file: {all_db_ids.difference(all_file_ids)}")
