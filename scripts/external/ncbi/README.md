# NCBI Taxon Import

To have NCBI taxonomy for use with strain completion, these scripts fetch NCBI ids and names and insert them into the database. There are two main scripts:

- `download_dump.py`: Fetches and processes the data into `var/external_data/ncbi/data_dump.csv`.
- `insert_data.py`: Iterates over the above file and inserts the entries into the database.

## Downloading

From [JensenLab FTP](https://download.jensenlab.org) we download the `organisms_dictionary.tar.gz` file. We use the `organism_entities.tsv` and `organism_groups.tsv` files to build lists of target organisms and their parent taxonomic entities. We use the `organisms_preferred.tsv` file to decide on the "canonical" names for these taxa.

The [METdb resource](https://metdb.sb-roscoff.fr/metdb/) builds a list of micro-eukaryotic marine species. By clicking the `CSV` button on the *Strain Descriptions* panel, one can download the `METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv` file which contains the different taxa available on METdb. This file is committed to git, because it's impractical to automate opening a browser and clicking the button. It might be a good idea to update it occasionally anyway.

The `taxon_selection.py` file includes a function that filters down the lists to unicellular organisms. This was originally an awk script by Savvas Paragkamian.

## Inserting

The code fetches individual `Taxon` records one at a time, if they exist. If the record's name and the one we have from the export are the same, then we don't need to update it. If it has changed, or if we are missing this record, we insert a new one.

If all records are skipped because they weren't changed, the script may run in a few minutes. On an empty database where all (~700k) taxa need to be inserted, it may take around 2 hours, or possibly more, depending on the performance of the machine. During this time, however, the application can be used normally.
