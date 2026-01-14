## Bulk downloads

<img
    style="width: 50%; float: right; margin-left: 20px;"
    src="/static/images/help/downloading-data/batch_export.png"
    title="Batch export" />

It's possible to fetch all of the data of a single study or the entire database by navigating to the [/static/export](/static/export) page. There, you can find folders and zip files with the study design and the observational data. There is also an `all_studies.zip` file that includes the entirety of the database.

This data is "raw", in the sense that it's preserved in the format that it was uploaded in. The file `study_design.json` contains all the metadata we collect from an uploader to describe the study. We may have changed the database structure since it was uploaded, but this JSON will reflect the format as it was at the time.

The data is uploaded as an excel spreadsheet, but its individual sheets are extracted into CSV files for the purpose of this bulk export. This is done for the sake of effective compression. As with the metadata, it reflects the structure that was requested at the time it was uploaded.

If using the site for meta-studies, be warned that the same experimental data may be uploaded to multiple different studies, if it's used for different scientific purposes. For instance, growth experiments of a particular microbial community may be shared in one study as targets of a particular modeling approach, and in another study as a control for perturbation experiments. Be sure to examine the study descriptions to understand the connections between them.

## Export of a single study

<img
    style="width: 50%; float: right; margin-left: 20px;"
    src="/static/images/help/study-pages/export_ui_1_2.png"
    title="Export interface" />

The study navigation interface includes an "Export data" button. Pressing it leads to a page where you can download data from selected biological replicates of a study in CSV format. The form allows selecting individual biological replicates to export and changing the checkboxes updates the preview on the right-hand side.

Once the desired combination of data is selected, the "Download ZIP file" button groups it into CSV files and compresses them into a single zip archive. A "README" file is also included with information about the study and the selected experiments.

The URL shown next to the download button can be used to fetch the selected subset of data on the command-line. This can be particularly useful when working on a remote server, or when the data from multiple studies needs to be processed in batches.

## API access

It's also possible to get fine-grained access to the data by using the application's REST API, described in the developer documentation: <https://mgrowthdb.readthedocs.io/en/stable/api.html>.

At this time, this endpoint is publicly available, but it requires familiarity with either a programming language like Python, or command-line skills with curl. It should be fairly straightforward to use in those cases, but since it requires extensive API documentation, it's been moved to the programmer-friendly "Read the Docs" platform.
