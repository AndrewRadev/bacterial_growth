import csv
import re
from pathlib import Path

import pandas as pd
from datetime import date
from long_task_printer import print_with_time

from app.model.lib.util import download_file, gunzip

##################
# Note: This file is currently not used, the "ascii names" accessible through
# the API don't seem to be present in any of the flat files. This makes it
# difficult to figure out which names to use to maintain compatibility.
#
print("File currently not used")
exit(1)
##################

chebi_url = 'https://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited'
mco_url   = 'https://raw.githubusercontent.com/microbial-conditions-ontology/microbial-conditions-ontology/master/mco.owl'
base_dir  = Path('var/external_data/chebi/')

base_dir.mkdir(exist_ok=True)

names_gz_path      = base_dir / 'names.tsv.gz'
names_path         = base_dir / 'names.tsv'
chemical_data_path = base_dir / 'chemical_data.tsv'
mco_owl_path       = base_dir / 'mco.owl'

output_path = base_dir / 'combined_dump.csv'

with print_with_time("Downloading raw data files"):
    download_file(f"{chebi_url}/names.tsv.gz",      names_gz_path)
    download_file(f"{chebi_url}/chemical_data.tsv", chemical_data_path)
    download_file(mco_url, mco_owl_path)

    gunzip(names_gz_path, names_path)

target_chebi_ids = None

with print_with_time("Processing MCO owl file"):
    with open(mco_owl_path, 'r') as owlfile:
        owl_text = owlfile.read()

    chebi_pattern = re.compile(r'//purl.obolibrary.org/obo/CHEBI_(\d+)')
    target_chebi_ids = {int(chebi_id) for chebi_id in chebi_pattern.findall(owl_text)}

data = {}

with print_with_time("Parsing data into memory"):
    with open(names_path) as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            if row['LANGUAGE'] != 'en':
                continue
            if row['SOURCE'] != 'KEGG COMPOUND':
                continue

            chebi_id = int(row['COMPOUND_ID'])
            if chebi_id not in target_chebi_ids:
                continue

            if chebi_id not in data:
                data[chebi_id] = {
                    'name':        row['NAME'].lower(),
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
            dialect='unix',
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()

        for chebi_id in sorted(data.keys()):
            writer.writerow({'chebiId': chebi_id, **data[chebi_id]})
