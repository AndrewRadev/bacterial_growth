# Release notes

## `v1.1.0`

Code: <https://github.com/msysbio/bacterial_growth/releases/tag/v1.1.0>

### User-level

* Stable public IDs for experiments
* New techniques: qPCR
* New units: biomass concentrations in g/L
* UI improvements to upload process, modeling interface
* Perturbation information now shown on the study page
* Sidebar open/close state remembered
* Various bugfixes

### Development-level

* External data sync: Scripts to download and apply NCBI and ChEBI dumps
* Full docker setup for installing on Windows machines
* Developer documentation
* Internal refactoring: consistent ids for study, project, and experiment; consistent subject IDs
* Improvements to database stability (SQLAlchemy pooling)

## `v1.0.0`

Code: <https://github.com/msysbio/bacterial_growth/releases/tag/v1.0.0>

Rebuild of the microbial growth database. Migrated from a streamlit app to a flask-based website, made lots of backend and UI changes.
