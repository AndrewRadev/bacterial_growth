import csv
import re
import itertools
import json
from pathlib import Path

from bioservices import ChEBI
from long_task_printer import print_with_time, LongTask

from app.model.lib.util import download_file

base_dir = Path('var/external_data/chebi/')
base_dir.mkdir(exist_ok=True)

output_path  = base_dir / 'data_dump.csv'

target_chebi_ids = {
    # dihydrogen (hydrogen molecule):
    5785,
}

with print_with_time("Downloading and processing MCO owl file"):
    mco_url = 'https://raw.githubusercontent.com/microbial-conditions-ontology/microbial-conditions-ontology/master/mco.owl'
    mco_owl_path = base_dir / 'mco.owl'
    download_file(mco_url, mco_owl_path)

    owl_text      = mco_owl_path.read_text()
    chebi_pattern = re.compile(r'//purl.obolibrary.org/obo/CHEBI_(\d+)')

    target_chebi_ids = {int(chebi_id) for chebi_id in chebi_pattern.findall(owl_text)}

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
chebi_api = ChEBI()

with print_with_time("Fetching data from ChEBI API"):
    long_task = LongTask(total_count=(len(target_chebi_ids) // 50))

    for chebi_ids in itertools.batched(sorted(target_chebi_ids), 50):
        with long_task.measure() as progress:
            print(progress)

            entities = chebi_api.getCompleteEntityByList(chebi_ids)

            for entity in entities:
                chebi_id = int(entity.chebiId.split(':')[-1])
                data[chebi_id] = {
                    'name':        entity.chebiAsciiName,
                    'averageMass': getattr(entity, 'mass', None),
                }

with print_with_time("Creating data dump"):
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
