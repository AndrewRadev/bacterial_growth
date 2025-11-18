import csv
import re
import itertools
import json
from pathlib import Path
from datetime import datetime, UTC

import requests
from long_task_printer import print_with_time, LongTask

from app.model.lib.util import download_file

base_dir = Path('var/external_data/chebi/')
base_dir.mkdir(exist_ok=True)

output_path = base_dir / 'data_dump.csv'
raw_data_path = base_dir / 'raw_data'

raw_data_path.mkdir(exist_ok=True)

target_chebi_ids = {
    # dihydrogen (hydrogen molecule):
    18276,
}

with print_with_time("Downloading and processing MCO owl file"):
    mco_url = 'https://raw.githubusercontent.com/microbial-conditions-ontology/microbial-conditions-ontology/master/mco.owl'
    mco_owl_path = base_dir / 'mco.owl'
    download_file(mco_url, mco_owl_path)

    owl_text      = mco_owl_path.read_text()
    chebi_pattern = re.compile(r'//purl.obolibrary.org/obo/CHEBI_(\d+)')

    target_chebi_ids |= {int(chebi_id) for chebi_id in chebi_pattern.findall(owl_text)}

with print_with_time("Downloading and processing MetaboLights JSON file"):
    metabolights_url = 'http://ftp.ebi.ac.uk/pub/databases/metabolights/eb-eye/metabolites_complete.json'
    metabolights_json = base_dir / 'metabolights.json'
    download_file(metabolights_url, metabolights_json)

    with metabolights_json.open() as f:
        metabolights_pattern = re.compile(r'CHEBI:\s*(\d+)')

        for raw_id in json.load(f):
            if match := re.search(metabolights_pattern, raw_id):
                target_chebi_ids.add(int(match[1]))

data = {}

chebi_base_url = 'https://www.ebi.ac.uk/chebi/backend/api/public'
page_size      = 100

with print_with_time("Fetching data from ChEBI API"):
    long_task = LongTask(total_count=(len(target_chebi_ids) // page_size))

    for index, chebi_ids in enumerate(itertools.batched(sorted(target_chebi_ids), page_size)):
        with long_task.measure() as progress:
            print(progress)

            response = requests.post(f"{chebi_base_url}/compounds/", data={
                'chebi_ids': chebi_ids,
            })
            entities = response.json()

            with open(raw_data_path / f'batch_{index:03}.json', 'w') as f:
                json.dump(entities, f, indent=2)

            for chebi_id, entity in entities.items():
                if entity['id_type'] != 'PRIMARY_ID':
                    continue

                if not entity['data']:
                    continue

                definition    = entity['data'].get('definition', None)
                chemical_data = entity['data'].get('chemical_data', None) or {}
                mass          = chemical_data.get('mass', None)

                data[int(chebi_id)] = {
                    'name':        entity['data']['ascii_name'],
                    'averageMass': mass,
                    'definition':  definition,
                }

with print_with_time("Creating data dump"):
    with open(output_path, 'w') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['chebiId', 'name', 'averageMass', 'definition'],
            dialect='unix',
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()

        for chebi_id in sorted(data.keys()):
            writer.writerow({'chebiId': chebi_id, **data[chebi_id]})

# Record time of this update:
with open('var/external_data/last_chebi_update.txt', 'w') as f:
    f.write(datetime.now(UTC).isoformat())
