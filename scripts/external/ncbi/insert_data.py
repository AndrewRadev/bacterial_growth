import csv
from pathlib import Path

from db import get_session
from app.model.orm import Taxon

import sqlalchemy as sql
from long_task_printer import LongTask

base_dir_path  = Path('var/external_data/ncbi/')
ncbi_taxa_path = base_dir_path / 'data_dump.csv'

# Count the number of lines in the file, should be quick:
with open(ncbi_taxa_path) as f:
    ncbi_taxa_count = len(f.readlines())

long_task = LongTask(total_count=ncbi_taxa_count, max_samples=500)

with get_session() as db_session:
    with open(ncbi_taxa_path) as f:
        reader = csv.DictReader(f)
        data_to_insert = []

        for row in reader:
            ncbi_id = int(row['ncbiId'])
            name    = row['name']

            with long_task.measure() as progress:
                existing_taxon = db_session.scalars(
                    sql.select(Taxon)
                    .where(Taxon.ncbiId == ncbi_id)
                ).one_or_none()

                if existing_taxon and existing_taxon.name == name:
                    print(f"[{progress}] Working on {(ncbi_id, name)}: Skip")
                elif existing_taxon:
                    print(f"[{progress}] Working on {(ncbi_id, name)}: Update")
                    existing_taxon.name = name
                    db_session.add(existing_taxon)
                    db_session.commit()
                else:
                    print(f"[{progress}] Working on: {(ncbi_id, name)}: Insert")
                    # Accumulate taxa for a batch-insert
                    data_to_insert.append({'ncbiId': ncbi_id, 'name': name})

                if len(data_to_insert) >= 100:
                    db_session.execute(sql.insert(Taxon), data_to_insert)
                    db_session.commit()
                    data_to_insert = []

        # Final insert of any leftovers after the loop:
        if len(data_to_insert) > 0:
            db_session.execute(sql.insert(Taxon), data_to_insert)
            db_session.commit()
            data_to_insert = []
