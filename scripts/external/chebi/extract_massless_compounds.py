import re
import json
from pathlib import Path
from glob import glob

base_dir = Path('var/external_data/chebi')

raw_data      = {}
massless_data = {}

for filename in sorted(base_dir.glob('raw_data/batch_???.json')):
    with open(filename) as f:
        raw_data.update(json.load(f))

for chebi_id, entity in raw_data.items():
    if not entity['data']:
        continue

    structure_data = entity['data'].get('default_structure', {}) or {}
    chemical_data  = entity['data'].get('chemical_data', {}) or {}

    mass = chemical_data.get('mass', None)

    if mass:
        continue

    children = []
    for relation in entity['data']['ontology_relations']['incoming_relations']:
        if relation['relation_type'] != 'is a':
            continue

        relation_chebi_id = str(relation['init_id'])
        if relation_chebi_id not in raw_data:
            continue

        name          = entity['data']['ascii_name']
        relation_name = relation['init_name']

        # We're looking for the same name with a suffix, examples:
        # - succinate:  succinate(1−), succinate(2−)
        # - NAD:        NADH, NAD+, NAD zwitterion
        # - penicillin: penicillin N, penicillin O
        #
        if not relation_name.startswith(name):
            continue

        relation_data = raw_data[relation_chebi_id]['data']

        relation_chemical_data = relation_data.get('chemical_data', {}) or {}
        relation_mass          = relation_chemical_data.get('mass', None)

        if not relation_mass:
            continue

        children.append({
            "chebi_id": relation_chebi_id,
            "name":     relation_name,
            "mass":     relation_mass,
        })

    if len(children):
        massless_data[f"CHEBI:{chebi_id}"] = {
            'name':       entity['data']['ascii_name'],
            'definition': entity['data']['definition'],
            'children':   children,
        }

with open(base_dir / 'massless_data.json', 'w') as f:
    json.dump(massless_data, f, indent=2)
