# ChEBI metabolite import

To have metabolites for use with completion, these scripts fetch information from ChEBI and insert it into the database:

- `download_dump.py`: Fetches and processes the data into `var/external_data/chebi/data_dump.csv`.
- `insert_data.py`: Iterates over the above file and inserts the entries into the database.

## Downloading

We use the Microbial Conditions Ontology (MCO) to build a corpus of metabolites of interest in microbial ecology studies. The MCO data is downloaded from [GitHub](https://raw.githubusercontent.com/microbial-conditions-ontology/microbial-conditions-ontology/master/mco.owl). At this time, the data hasn't been updated in 6 years (since 2019), and the repository has open issues with no responses, so it may not be actively maintained. In the future, we may move to a different data file that indicates entities of interest.

We take the ChEBI ids from the MCO file and we use the `bioservices` package and fetch metabolite data 50 entries at a time. We use the `chebiAsciiName` from that response as the canonical name for the metabolite. This process may fail if the connection to the ChEBI API fails, in which case it's recommended to retry. It may take some time to finish.

## Inserting

The code fetches individual `Metabolite` records one at a time, if they exist. If the record's data and the data we have from the export are the same, then we don't need to update it. If it has changed, or if we are missing this record, we insert a new one.

At this time, there are only around 2.5k metabolite records, so the insertion script should finish fairly quickly.
