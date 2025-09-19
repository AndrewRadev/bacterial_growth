# API documentation (WIP)

All published studies in the app should be exportable through an API of several different granularities:

1. Full study metadata and uploaded data spreadsheet for batch downloads
2. Export UI with selectable bioreplicates per-study (currently exists under `/study/<studyId>/export`, example: [SMGDB00000001/export](https://mgrowthdb.gbiomed.kuleuven.be/study/SMGDB00000001/export/))
3. Fine-grained access to entities by their ID and by searching

Only the second functionality is currently implemented, the rest is in progress as of this version.
