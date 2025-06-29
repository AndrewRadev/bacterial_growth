import os
import sys
import csv
import re
from pathlib import Path

import pandas as pd
from datetime import date
from long_task_printer import print_with_time

from app.model.lib.util import download_file, untar

# Relative import of a selection function:
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from taxon_selection import filter_unicellular

metdb_dump = Path(__file__).parent / 'METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv'
if not metdb_dump.exists():
    print(f"Missing data dump from MetDB, please download first: {metdb_dump}")
    exit(1)

selected_taxa = filter_unicellular(metdb_dump)

jensenlab_url = 'https://download.jensenlab.org/organisms_dictionary.tar.gz'

base_dir_path = Path('var/external_data/ncbi/')
base_dir_path.mkdir(exist_ok=True)

organisms_tar_gz_path = base_dir_path / 'organisms_dictionary.tar.gz'

organisms_dir_path = base_dir_path / 'organisms_dictionary'
organisms_dir_path.mkdir(exist_ok=True)

with print_with_time("Downloading JensenLab data dump"):
    download_file(jensenlab_url, organisms_tar_gz_path)

with print_with_time("Extracting JensenLab data dump"):
    untar(organisms_tar_gz_path, organisms_dir_path, file_list=[
        'organisms_entities.tsv',
        'organisms_groups.tsv',
        'organisms_preferred.tsv',
    ])

entity_data          = {}
unicellular_ncbi_ids = []
preferred_names      = {}
identifiers          = set()

with print_with_time("Generating filtered NCBI data dump"):
    with open(organisms_dir_path / 'organisms_preferred.tsv') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            serial = row[0]
            name   = row[1]

            preferred_names[serial] = name

    with open(organisms_dir_path / 'organisms_entities.tsv') as f_in:
        reader = csv.reader(f_in, delimiter='\t')

        for (serial, type, ncbi_id) in reader:
            entity_data[serial] = (type, ncbi_id)

    with open(organisms_dir_path / 'organisms_groups.tsv') as f_in:
        reader = csv.reader(f_in, delimiter='\t')

        for (taxon_serial, parent_serial) in reader:
            if taxon_serial not in entity_data: continue
            if parent_serial not in entity_data: continue

            parent_ncbi_id = int(entity_data[parent_serial][1])
            if parent_ncbi_id not in selected_taxa:
                continue

            if taxon_serial not in preferred_names:
                # print(f"> Warning: missing name for {ncbi_id}")
                continue

            taxon_ncbi_id = int(entity_data[taxon_serial][1])

            identifiers.add((taxon_ncbi_id, preferred_names[taxon_serial]))

    with open(base_dir_path / 'ncbi_taxa.csv', 'w') as f_out:
        writer = csv.DictWriter(
            f_out,
            fieldnames=['ncbiId', 'name'],
            dialect='unix',
            quoting=csv.QUOTE_MINIMAL,
        )

        for (ncbi_id, name) in sorted(identifiers):
            writer.writerow({'ncbiId': ncbi_id, 'name': name})
