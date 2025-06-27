import csv
from pathlib import Path

import pandas as pd
from datetime import date
from long_task_printer import print_with_time

from app.model.lib.util import download_file, gunzip

# TODO (2025-06-26) use Mco.owl to pick chebi ids, limit results to those.
# -> Print missing chebi ids
# -> Print names in the database that are not in the dumps

base_url = 'https://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited'
base_dir = Path('var/external_data/')

# names_gz_path      = base_dir / 'names_3star.tsv.gz'
# names_path         = base_dir / 'names_3star.tsv'
# chemical_data_path = base_dir / 'chemical_data_3star.tsv'

names_gz_path      = base_dir / 'names.tsv.gz'
names_path         = base_dir / 'names.tsv'
chemical_data_path = base_dir / 'chemical_data.tsv'

output_path = base_dir / 'combined_dump.csv'

with print_with_time("Downloading raw files"):
    download_file(f"{base_url}/names.tsv.gz",      names_gz_path)
    download_file(f"{base_url}/chemical_data.tsv", chemical_data_path)

    # download_file(f"{base_url}/names_3star.tsv.gz",      names_gz_path)
    # download_file(f"{base_url}/chemical_data_3star.tsv", chemical_data_path)

    gunzip(names_gz_path, names_path)

data = {}

with print_with_time("Parsing data into memory"):
    with open(names_path) as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            if row['LANGUAGE'] != 'en':
                continue
            if row['TYPE'] != 'IUPAC NAME':
                continue

            # TODO (2025-06-26) Collect all IUPAC names, use unique "name" index instead?

            chebi_id = int(row['COMPOUND_ID'])
            if chebi_id not in data:
                data[chebi_id] = {
                    'name':        row['NAME'],
                    'averageMass': None,
                }

    with open(chemical_data_path) as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            if row['TYPE'] != 'MASS':
                continue

            chebi_id = int(row['COMPOUND_ID'])
            if chebi_id not in data:
                continue

            data[chebi_id]['averageMass'] = row['CHEMICAL_DATA']

with print_with_time("Creating combined dump"):
    with open(output_path, 'w') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['chebiId', 'name', 'averageMass'],
        )
        writer.writeheader()

        for chebi_id in sorted(data.keys()):
            writer.writerow({
                'chebiId': chebi_id,
                **data[chebi_id]
            })
