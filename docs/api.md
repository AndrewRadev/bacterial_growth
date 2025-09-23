# API documentation (WIP)

All published studies in the app should be exportable through an API of several different granularities:

1. Full study metadata and uploaded data spreadsheet for batch downloads
2. Export UI with selectable bioreplicates per-study (currently exists under `/study/<studyId>/export`, example: [SMGDB00000001/export](https://mgrowthdb.gbiomed.kuleuven.be/study/SMGDB00000001/export/))
3. Fine-grained access to entities by their ID and by searching

Only the second functionality is currently implemented, the rest is in progress as of this version.

For the examples, we'll use curl to demonstrate responses. We'll use a `$ROOT_URL` that could be set to your localhost installation, or could be the public database:

```bash
export ROOT_URL="https://mgrowthdb.gbiomed.kuleuven.be"
```

The JSON output will be formatted for readability and in some places, truncated with a message like `"[...N more entries...]"`.

## Public entity metadata

There are three major entities with stable public ids: projects, studies, and experiments. We can fetch names, descriptions, and links to other entities from those central objects.

### Projects

Example project: [PMGDB000001](https://mgrowthdb.gbiomed.kuleuven.be/project/PMGDB000001).

```
curl -s "$ROOT_URL/api/v1/project/PMGDB000001.json"
```

Output:

```json
{
  "id": "PMGDB000001",
  "name": "Synthetic human gut bacterial community using an automated fermentation system",
  "description": "Six biological replicates for a community initially consisting of five common gut bacterial species that fill different metabolic niches. After an initial 12 hours in batch mode, we switched to chemostat mode and observed the community to stabilize after 2-3 days.",
  "studies": [
    {
      "id": "SMGDB00000001",
      "name": "Synthetic human gut bacterial community using an automated fermentation system"
    }
  ]
}
```

### Studies

Example study: [SMGDB00000002](https://mgrowthdb.gbiomed.kuleuven.be/study/SMGDB00000002/).

```
curl -s "$ROOT_URL/api/v1/study/SMGDB00000002.json"
```

Output:

```json
{
  "id": "SMGDB00000002",
  "name": "Starvation responses impact interaction of human gut bacteria BT-RI",
  "projectId": "PMGDB000002",
  "description": "we used an in vitro batch system containing mucin beads to emulate the dynamic host environment and to study its impact on the interactions between two abundant and prevalent human gut bacteria.",
  "url": "https://doi.org/10.1038/s41396-023-01501-1",
  "timeUnits": "h",
  "uploadedAt": "2025-07-16T12:32:46+00:00",
  "publishedAt": "2025-07-16T12:32:48+00:00",
  "experiments": [
    {
      "id": "EMGDB000000019",
      "name": "BT_MUCIN"
    },
    {
      "id": "EMGDB000000020",
      "name": "BT_WC"
    },
    ["...4 more entries..."]
  ]
}
```

### Experiments

Example experiment: [EMGDB000000019](https://mgrowthdb.gbiomed.kuleuven.be/experiment/EMGDB000000019/)

```
curl -s "$ROOT_URL/api/v1/experiment/EMGDB000000019.json"
```

Example output:

```json
{
  "id": "EMGDB000000019",
  "name": "BT_MUCIN",
  "description": "BT with WC plus mucin beads for 120 h",
  "studyId": "SMGDB00000002",
  "cultivationMode": "batch",
  "communityStrains": [
    {
      "id": 6,
      "NCBId": 818,
      "custom": false,
      "name": "Bacteroides thetaiotaomicron"
    }
  ],
  "compartments": [
    {
      "name": "WC",
      "volume": "60.00",
      "pressure": "1.00",
      "stirringSpeed": 170.0,
      "stirringMode": "linear",
      "O2": null,
      "CO2": "10.00",
      "H2": "10.00",
      "N2": "80.00",
      "inoculumConcentration": "1960000.000",
      "inoculumVolume": "1.00",
      "initialPh": "5.00",
      "initialTemperature": "37.00",
      "mediumName": "Wilkins-Chalgren Anaerobe Broth (WC)",
      "mediumUrl": "Wilkins-Chalgren Anaerobe Broth (WC)"
    },
    {
      "name": "MUCIN",
      "volume": null,
      "pressure": null,
      "stirringSpeed": null,
      "stirringMode": "",
      "O2": null,
      "CO2": null,
      "H2": null,
      "N2": null,
      "inoculumConcentration": null,
      "inoculumVolume": null,
      "initialPh": null,
      "initialTemperature": "37.00",
      "mediumName": "Mucin",
      "mediumUrl": "Mucin"
    }
  ],
  "bioreplicates": [
    {
      "id": 26,
      "name": "Average(BT_MUCIN)",
      "biosampleUrl": null,
      "measurementContexts": [
        {
          "id": 324,
          "techniqueType": "od",
          "techniqueUnits": "",
          "subject": {
            "id": 26,
            "type": "bioreplicate",
            "name": "Average(BT_MUCIN)"
          }
        },
        {
          "id": 325,
          "techniqueType": "ph",
          "techniqueUnits": "",
          "subject": {
            "id": 26,
            "type": "bioreplicate",
            "name": "Average(BT_MUCIN)"
          }
        },
        "[...5 more entries...]"
      ]
    },
    "[...3 more entries...]"
  ]
}
```

## Measurement data downloads (WIP)

TODO

## Search (WIP)

TODO
