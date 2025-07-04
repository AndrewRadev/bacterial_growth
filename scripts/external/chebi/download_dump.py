import csv
import re
import itertools
from pathlib import Path

from bioservices import ChEBI
from long_task_printer import print_with_time, LongTask

from app.model.lib.util import download_file

base_dir = Path('var/external_data/chebi/')
base_dir.mkdir(exist_ok=True)

output_path  = base_dir / 'data_dump.csv'

target_chebi_ids = None

with print_with_time("Downloading and processing MCO owl file"):
    mco_url = 'https://raw.githubusercontent.com/microbial-conditions-ontology/microbial-conditions-ontology/master/mco.owl'
    mco_owl_path = base_dir / 'mco.owl'
    download_file(mco_url, mco_owl_path)

    owl_text      = mco_owl_path.read_text()
    chebi_pattern = re.compile(r'//purl.obolibrary.org/obo/CHEBI_(\d+)')

    target_chebi_ids = {int(chebi_id) for chebi_id in chebi_pattern.findall(owl_text)}

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
