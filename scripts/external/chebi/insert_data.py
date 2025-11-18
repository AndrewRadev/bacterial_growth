import csv
import json
from pathlib import Path

import numpy as np
import sqlalchemy as sql
from long_task_printer import LongTask

from db import get_session
from app.model.orm import Metabolite

base_dir_path      = Path('var/external_data/chebi/')
data_dump_path     = base_dir_path / 'data_dump.csv'
massless_data_path = base_dir_path / 'massless_data.json'

# Count the number of lines in the file, should be quick:
with open(data_dump_path) as f:
    # Number of lines minus the header
    metabolite_count = len(f.readlines()) - 1

with open(massless_data_path) as f:
    massless_data = json.load(f)

batch_size = 100
long_task = LongTask(total_count=metabolite_count, max_samples=batch_size * 5)

all_file_ids = set()

with get_session() as db_session:
    all_db_ids = set(db_session.scalars(sql.select(Metabolite.chebiId)).all())

    with open(data_dump_path) as f:
        reader = csv.DictReader(f)
        data_to_insert = []

        for row in reader:
            chebi_id   = f"CHEBI:{row['chebiId']}"
            name       = row['name']
            mass       = row['averageMass']
            definition = row['definition']

            mass_is_estimation = False

            all_file_ids.add(chebi_id)

            if mass == '':
                mass = None

            if chebi_id in massless_data:
                mass = np.average([float(c['mass']) for c in massless_data[chebi_id]['children']])
                mass_is_estimation = True

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

                        existing_metabolite.name             = name
                        existing_metabolite.averageMass      = mass
                        existing_metabolite.massIsEstimation = mass_is_estimation
                        existing_metabolite.definition       = definition

                        db_session.add(existing_metabolite)
                        db_session.commit()
                else:
                    print(f"[{progress}] Working on: {(chebi_id, name)}: Insert")
                    # Accumulate taxa for a batch-insert
                    data_to_insert.append({
                        'chebiId':          chebi_id,
                        'name':             name,
                        'averageMass':      mass,
                        'massIsEstimation': mass_is_estimation,
                        'definition':       definition,
                    })

                if len(data_to_insert) >= batch_size:
                    db_session.execute(sql.insert(Metabolite), data_to_insert)
                    db_session.commit()
                    data_to_insert = []

        # Final insert of any leftovers after the loop:
        if len(data_to_insert) > 0:
            db_session.execute(sql.insert(Metabolite), data_to_insert)
            db_session.commit()

    print(f"Missing IDs in the file: {all_db_ids.difference(all_file_ids)}")
