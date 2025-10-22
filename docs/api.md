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

Requests for specific global identifiers like `SMGDB00000001` or `EMGDB000000026` should work for you as well, so you should be able to replicate them by running them in the console. NCBI IDs and ChEBI IDs should also work for you. However, other numeric ids may be different, since updates to the underlying data might force them to be recreated. Try these out by fetching a specific study or experiment and picking bioreplicate ID or measurement context ID from the public entity's metadata.

## General principles

There are two types of results from the API:

- Metadata returned as JSON
- Measurement data returned in CSV format

The JSON endpoints always end in `.json` and the CSV ones end in `.csv`. A single entity might be downloadable in either format if you simply change the suffix. Explore the specific examples below.

The `measurementTimeUnits` key describes what time units measurements will be fetched in from the CSV endpoints. Right now, the API will always return time in hours ("h"), but this might be a configurable option later. For the moment, you can consider this an informational key, rather than something specific to the particular study or experiment.

Successful results will be returned with an HTTP status code of `200`. A request that somehow doesn't fit the requirements of the API will have a response code of `400` ("bad request"). A request for a missing entity will return the code `404` ("not found"). For a JSON endpoint, the body of an unsuccessful response will have an "error" key that describes the issue. For a CSV endpoint, you can expect an error message as a single line of text.

## Search

You can use the "search" endpoint to locate studies with specific properties. At this time, you can only look for studies that measure a specific **microbial strain** or measure a specific **metabolite**.

Example search query that looks for the strain with NCBI Taxonomy ID 411483, [Faecalibacterium duncaniae](https://www.ncbi.nlm.nih.gov/datasets/taxonomy/411483/):

```bash
curl -s "$ROOT_URL/api/v1/search.json?strainNcbiId=411483"
```

Output:

```json
{
  "studies": [
    "SMGDB00000004",
    "SMGDB00000005"
  ],
  "experiments": [
    "EMGDB000000026",
    "EMGDB000000028",
    "EMGDB000000031",
    "EMGDB000000032",
    "EMGDB000000033",
    "EMGDB000000042",
    "EMGDB000000043"
  ],
  "measurementTimeUnits": "h",
  "measurementContexts": [
    {
      "id": 3478,
      "experimentId": "EMGDB000000028",
      "studyId": "SMGDB00000004",
      "techniqueType": "qpcr",
      "techniqueUnits": "Cells/mL",
      "subject": {
        "type": "strain",
        "name": "Faecalibacterium prausnitzii A2-165",
        "NCBId": 411483
      }
    },
    ["...13 more entries..."],
    {
      "id": 5256,
      "experimentId": "EMGDB000000042",
      "studyId": "SMGDB00000005",
      "techniqueType": "fc",
      "techniqueUnits": "Cells/μL",
      "subject": {
        "type": "strain",
        "name": "Faecalibacterium duncaniae",
        "NCBId": 411483
      }
    },
    ["...17 more entries..."]
  ]
}
```

The results include the public identifiers of studies and experiments that include measurements of that strain. You can dig into their details with the additional API calls described below.

The `measurementContexts` array includes the metadata of the measurement contexts that include the strain. You can iterate over the returned data and filter it additionally based on technique, measurement units, and so on.

Example 2: Searching by metabolite, in this case [N-acetylneuraminic acid](https://www.ebi.ac.uk/chebi/CHEBI:17012) with ChEBI ID 17012:

```bash
curl -s "$ROOT_URL/api/v1/search.json?metaboliteChebiId=17012"
```

```json
{
  "studies": [
    "SMGDB00000002"
  ],
  "experiments": [
    "EMGDB000000021",
    "EMGDB000000023"
  ],
  "measurementTimeUnits": "h",
  "measurementContexts": [
    {
      "id": 3107,
      "experimentId": "EMGDB000000021",
      "studyId": "SMGDB00000002",
      "techniqueType": "metabolite",
      "techniqueUnits": "mM",
      "subject": {
        "type": "metabolite",
        "name": "N-acetylneuraminic acid",
        "chebiId": 17012
      }
    },
    ["...7 more entries..."]
  ]
}
```

If you make a request for both strain and metabolite, the results will be the combination of both. In other words, the query will end up creating an `OR` operation. In practice, it might be best to make individual queries and process the results after downloading.

## Public entity metadata

There are three major entities with stable public ids: projects, studies, and experiments. We can fetch names, descriptions, and links to other entities from those central objects.

### Projects

Example project: [PMGDB000001](https://mgrowthdb.gbiomed.kuleuven.be/project/PMGDB000001).

```bash
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

```bash
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

```bash
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
      "dilutionRate": null,
      "initialTemperature": "37.00",
      "mediumName": "Wilkins-Chalgren Anaerobe Broth (WC)",
      "mediumUrl": "https://mediadive.dsmz.de/medium/339"
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
      "dilutionRate": null,
      "initialTemperature": "37.00",
      "mediumName": "Mucin",
      "mediumUrl": null,
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

### For a single measurement context

From one of the above measurement context records, we can find the id of a particular collection of measurements and fetch its metadata as JSON and its specific measurements in CSV format. To fetch the metadata via curl:

```bash
curl -s "$ROOT_URL/api/v1/measurement-context/1440.json"
```

Example output:

```json
{
  "id": 1440,
  "experimentId": "EMGDB000000020",
  "studyId": "SMGDB00000002",
  "bioreplicateId": 60329,
  "bioreplicateName": "Average(BT_WC)",
  "techniqueType": "fc",
  "techniqueUnits": "Cells/μL",
  "subject": {
    "type": "strain",
    "name": "Bacteroides thetaiotaomicron VPI-5482",
    "NCBId": 226186
  },
  "measurementCount": 14,
  "measurementTimeUnits": "h"
}
```

This gives us information about the specifics of the measurement context like what its technique is, what units the value is measured in, and the public ids of its containing experiment and study. To fetch the full dataset for this measurement context with "time" measured in hours:

```bash
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

```bash
curl -s "$ROOT_URL/api/v1/measurement-context/1314.json"
curl -s "$ROOT_URL/api/v1/measurement-context/1314.csv"
```

```json
{
  "id": 1314,
  "experimentId": "EMGDB000000020",
  "studyId": "SMGDB00000002",
  "bioreplicateId": 60315,
  "bioreplicateName": "BT_WC_3",
  "techniqueType": "metabolite",
  "techniqueUnits": "mM",
  "subject": {
    "type": "metabolite",
    "name": "succinate",
    "chebiId": 26806
  },
  "measurementCount": 14,
  "measurementTimeUnits": "h"
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

### For an entire biological replicate

We can perform similar queries for biological replicates, getting the results for multiple measurement contexts in one CSV, grouped by measurement context id. We can get the bioreplicate IDs from the experiment metadata and use them to fetch either the bioreplicate-specific metadata or the measurements in CSV form.

```bash
curl -s "$ROOT_URL/api/v1/bioreplicate/1314.json"
curl -s "$ROOT_URL/api/v1/bioreplicate/1314.csv"
```

```json
{
  "id": 60332,
  "experimentId": "EMGDB000000023",
  "studyId": "SMGDB00000002",
  "name": "Average(BTRI_MUCIN)",
  "biosampleUrl": null,
  "measurementTimeUnits": "h",
  "measurementContexts": [
    {
      "id": 3364,
      "techniqueType": "od",
      "techniqueUnits": "",
      "subject": {
        "type": "bioreplicate",
        "name": "Average(BTRI_MUCIN)"
      }
    },
    ["...17 more entries..."]
  ]
}
```

```csv
measurementContextId,time,value,std
3364,0.0,0.013,0.003
3364,4.0,0.035,0.002
3364,8.0,0.383,0.008
3364,12.0,0.92,0.005
3364,16.0,1.121,0.006
3364,20.0,1.045,0.006
3364,24.0,0.911,0.007
3364,28.0,0.833,0.007
3364,32.0,0.8,0.007
3364,36.0,0.801,0.005
3364,40.0,0.789,0.007
3364,48.0,0.757,0.005
3364,60.0,0.744,0.005
3364,72.0,0.748,0.005
3364,96.0,0.772,0.006
3364,120.0,0.809,0.007
3365,0.0,6.597,0.019
3365,4.0,6.65,0.0
3365,8.0,6.203,0.019
3365,12.0,5.327,0.019
3365,16.0,5.117,0.019
3365,20.0,5.057,0.024
3365,24.0,5.053,0.019
3365,28.0,5.057,0.024
3365,32.0,5.057,0.024
3365,36.0,5.13,0.033
3365,40.0,5.21,0.0
3365,48.0,5.25,0.0
3365,60.0,5.213,0.005
3365,72.0,5.217,0.024
3365,96.0,5.227,0.019
3365,120.0,5.237,0.019
3366,0.0,987.667,27.195
3366,4.0,14638.667,339.884
[...218 more lines...]
```
