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

batch_size = 100
long_task = LongTask(total_count=metabolite_count, max_samples=batch_size * 5)

all_file_ids = set()

with get_session() as db_session:
    all_db_ids = set(db_session.scalars(sql.select(Metabolite.chebiId)).all())

    with open(data_dump) as f:
        reader = csv.DictReader(f)
        data_to_insert = []

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
                    # Accumulate taxa for a batch-insert
                    data_to_insert.append({'chebiId': chebi_id, 'name': name, 'averageMass': mass})

                if len(data_to_insert) >= batch_size:
                    db_session.execute(sql.insert(Metabolite), data_to_insert)
                    db_session.commit()
                    data_to_insert = []

        # Final insert of any leftovers after the loop:
        if len(data_to_insert) > 0:
            db_session.execute(sql.insert(Metabolite), data_to_insert)
            db_session.commit()

    print(f"Missing IDs in the file: {all_db_ids.difference(all_file_ids)}")
