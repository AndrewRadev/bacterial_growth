# API documentation (WIP)

All published studies in the app should be exportable through an API of several different granularities:

1. Full study metadata and uploaded data spreadsheet for batch downloads
2. Export UI with selectable bioreplicates per-study (currently exists under `/study/<studyId>/export`, example: [SMGDB00000001/export](https://mgrowthdb.gbiomed.kuleuven.be/study/SMGDB00000001/export/))
3. Fine-grained access to entities by their ID and by searching

Only the second functionality is currently implemented, the rest is in progress as of this version. The following document describes the third functionality, fine-grained API access.

For the examples, we'll use curl to demonstrate responses. We'll use a `$ROOT_URL` that could be set to your localhost installation, or could be the public database:

```bash
export ROOT_URL="https://mgrowthdb.gbiomed.kuleuven.be"
```

The JSON output will be formatted for readability and in some places, truncated with a message like `"[...N more entries...]"`.

## Search (WIP)

TODO

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
  "uploadedAt": "2025-06-05T16:52:49+00:00",
  "publishedAt": "2025-06-05T16:52:53+00:00",
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
      "id": 60031,
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
      "initialPh": "6.70",
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
      "id": 60111,
      "name": "Average(BT_MUCIN)",
      "biosampleUrl": null,
      "measurementContexts": [
        {
          "id": 1431,
          "techniqueType": "od",
          "techniqueUnits": "",
          "subject": {
            "id": 60111,
            "type": "bioreplicate",
            "name": "Average(BT_MUCIN)"
          }
        },
        {
          "id": 1432,
          "techniqueType": "ph",
          "techniqueUnits": "",
          "subject": {
            "id": 60111,
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

## Measurement data

From one of the above measurement context records, we can find the id of a particular collection of measurements and fetch its metadata as JSON and its specific measurements in CSV format. To fetch the metadata via curl:

```
curl -s "$ROOT_URL/api/v1/measurement-context/1440.json"
```

Example output:

```json
{
  "id": 1440,
  "experimentId": "EMGDB000000020",
  "studyId": "SMGDB00000002",
  "bioreplicateName": "Average(BT_WC)",
  "techniqueType": "fc",
  "techniqueUnits": "Cells/μL",
  "subject": {
    "id": 60031,
    "type": "strain",
    "name": "Bacteroides thetaiotaomicron",
    "NCBId": 818
  },
  "measurementCount": 13
}
```

This gives us information about the specifics of the measurement context like what its technique is, what units the value is measured in, and the public ids of its containing experiment and study. To fetch the full dataset for this measurement context with "time" measured in hours:

```
curl -s "$ROOT_URL/api/v1/measurement-context/1440.csv"
```

Example output:

```csv
time,value,std
0.0,2619.0,477.072
4.0,36072.333,1522.018
12.0,1003028.333,30201.503
16.0,1106725.0,85176.706
24.0,857815.0,62848.275
28.0,778893.333,47670.388
32.0,962915.0,55489.511
38.0,675345.0,26650.222
48.0,348478.333,102905.344
60.0,111021.667,28523.155
72.0,45606.667,13966.714
96.0,13413.333,4155.786
120.0,3215.0,461.808
```

If the measurement context does not have standard deviation values, the "std" column will be present, but empty. Example measurement and its data:

```
curl -s "$ROOT_URL/api/v1/measurement-context/1314.json"
curl -s "$ROOT_URL/api/v1/measurement-context/1314.csv"
```

```json
{
  "id": 1314,
  "experimentId": "EMGDB000000020",
  "studyId": "SMGDB00000002",
  "bioreplicateName": "BT_WC_3",
  "techniqueType": "metabolite",
  "techniqueUnits": "mM",
  "subject": {
    "id": 710,
    "type": "metabolite",
    "name": "succinate",
    "chebiId": 26806
  },
  "measurementCount": 14
}
```

```csv
time,value,std
0.0,0.57,
4.0,0.53,
8.0,2.19,
12.0,5.04,
16.0,7.67,
24.0,9.58,
28.0,10.66,
32.0,10.67,
38.0,10.69,
48.0,10.99,
60.0,11.06,
72.0,10.94,
96.0,11.0,
120.0,11.03,
```
