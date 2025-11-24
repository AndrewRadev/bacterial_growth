# μGrowthDB

[μGrowthDB](https://mgrowthdb.gbiomed.kuleuven.be) is the first crowd-sourced database for microbial growth data. It supports a range of measurement techniques: Colony Forming Units (CFU), Flow Cytometry, Optical Density, 16S sequencing, qPCR. It also supports storage of accompanying metabolic data.

In this repo, you can find the code of the resource, known issues and discussions, while you are more than welcome to share your thoughts on the resource and of course [contribute](./CONTRIBUTING.md).

## To use μGrowthDB

If you'd like to explore studies and their data, these two documentation resources explain how to do that:

- Searching: <https://mgrowthdb.gbiomed.kuleuven.be/help/searching/>
- Data analysis: <https://mgrowthdb.gbiomed.kuleuven.be/help/data-analysis/>

To upload your own data, you need to authenticate by using [ORCID](https://orcid.org/). Documentation on how to proceed can be found here:

- Upload process: <https://mgrowthdb.gbiomed.kuleuven.be/help/upload-process/>

## Local installation using docker

If you'd like to get the app running to use in a local environment, a docker container can be a working cross-platform choice. The provided Dockerfile is meant for launching the app in production mode and not for development purposes.

First, copy the `.env.example` file to an `.env` file and fill in the environment variables. Ideally, you should set a random string for session encryption. If you want to be able to log in, you'll need to follow [the ORCID documentation](https://info.orcid.org/documentation/integration-guide/) to create an ORCID app and fill in its information. If you skip that part, you'll only have read access to the data.

To start the application, you can run the following docker-compose command in the root of the application:

```
docker compose -f docker-compose-full.yml up --build
```

The file `docker-compose-full.yml` starts a complete app with a mysql server and a redis server. You can "detach" it by adding `-d` to the command-line, or you can keep it running in a terminal or in a systemd service to see the app's logs. To bootstrap the data the application needs, you can run bash inside the running compartment with `docker compose exec`:

```
docker compose -f docker-compose-full.yml exec -it mgrowthdb_app bash
```

While inside the container, you can run the script `./scripts/init.sh` that will create the initial structure, download ontology data from ChEBI and [JensenLab](https://jensenlab.org/), and create a few initial studies:

```
ADMIN_ORCID="1234-1234-1234-1234" ./scripts/init.sh
```

Note the variable `$ADMIN_ORCID`, which is set to the ORCID identifier of the first admin user to be created. If you omit it, the id will be set to `0000-0000-0000-0000`, and you can change it later by manipulating the database. If you provide your own ORCID identifier, you can log in with that and automatically be granted ownership of the initial studies and admin permissions to your local copy of the site. Note, however, that logging in requires setting up an ORCID app as described above.

When updating the application from git, make sure to run migrations (inside the "app" container) to apply database changes before taking the docker container down and then back up:

```
bin/migrations-run
```

## Local installation for development (on Linux or macOS)

First, you should copy the `.env.example` file to `.env` and fill in the environment variables.

To set up a working python environment, it's recommended to use [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) with the given environment file:

```
micromamba create -f micromamba_env.yml
micromamba activate mgrowthdb
```

This will install python version 3.12 and R and activate the environment by name in the current shell. Python dependencies can now be installed using:

```
pip install -r requirements.txt
```

There are a few R dependencies, most notably the package [growthrates](https://cran.r-project.org/package=growthrates), which you can install using `Rscript`:

```
Rscript -e 'install.packages(c("growthrates", "jsonlite"), repos="https://cloud.r-project.org")'
```

In the root of the repository, there is an `.env.example` file that contains environment variables the app needs. You can copy that to `.env` and fill them in with your own values.

In the database config directory, the file [`db/config.toml.example`](db/config.toml.example) contains a template for the database configuration. Copy this file to `db/config.toml` and update it with the correct credentials to access a running mysql database. You can launch one by using the provided "services" dockerfile:

```
docker-compose -f docker-compose-services.yml up --build -d
```

In case you decide to use this, take a look at the file to see the mysql usernames, passwords, etc, for your configuration.

You can manually interact with the configured database using:

```
bin/dbconsole
```

To load the full database structure, you can pipe the schema file into that command:

```
bin/dbconsole < db/schema.sql
```

To make changes to the database, you can create a new migration with an "up" function that makes the change in the forward direction and a "down" function that reverses it:

``` bash
# Bootstrap a new migration file:
bin/migrations-new some_name_for_my_migration

# Edit the migration, created with a timestamp under db/migrations/

# Execute the new migration forward:
bin/migrations-run

# Roll it back and then execute it again to check if your reversal works:
bin/migrations-run down
bin/migrations-run up
```

To launch the application in development mode on <http://localhost:8081>, run:

```
bin/server
```

To launch a background job worker that processes growth modeling requests, run (in another terminal):

```
bin/worker
```

The worker uses redis to coordinate with the app. A redis server is included in the "services" docker-compose config file that should "just work", but you can launch your own and start the server with `REDIS_HOST` and `REDIS_PORT` set to whatever you need.

## Code structure

### Startup: `initialization`

The application starts from `main.py`, which imports and runs code from the "initialization" folder. This includes configuration, routing, static asset compilation, and other utilities that need to be run before the server can start serving requests.

### MVC: `app/model`, `app/view`, `app/pages`

The application loosely follows the model-view-controller (MVC) architecture with these three folders holding the three layers. Inside `model`, we keep domain logic dedicated to a specific unit of data. This could be a wrapper for a database table, like "experiment" or "user", or a logical concept like "submission" that is loaded from data in the session. The functions and classes inside the relevant model are all meant to encapsulate potentially complex logic that reads and writes this data. The "orm" directory contains [SQLAlchemy](https://www.sqlalchemy.org/) ORM models, while the "lib" directory contains more general-purpose code.

The `app/view/templates` folder contains [Jinja2](https://jinja.palletsprojects.com/en/stable/) templates for every page or HTML fragment. The javascript, CSS, and images that are rendered in the main layout are located in the `app/view/static` directory. This follows the default structure of flask apps.

The `app/pages` folder has all the handler functions that instantiate model objects, call utility functions, and inject the output into a template. These are hooked up to URL routes in [`initialization/routes.py`](initialization/routes.py).

Form objects are contained in `app/view/forms`. Their purpose is to encapsulate some view-level logic that transforms data into a user-facing form. For instance, preparing a dropdown with labels that get translated to database values, or a static CSV file into a collection of fields. Some of these use [Flask-WTF](https://flask-wtf.readthedocs.io/en/0.15.x/), but some are plain objects. They are not in `models`, because they are used to generate HTML, so they sit between the model and view layers.

### Database: `db`

This folder contains the database configuration in [`db/config.toml.example`](db/config.toml.example) and an `__init__.py` file with the main functions to access a database connection.

Every database change is encapsulated in a migration file under [`db/migrations`](db/migrations), which has an `up` function and a `down` function. The first one applies the migration, the other rolls it back. Ideally, all migrations should be runnable in order. The [`bin/migrations-new`](bin/migrations-new) script bootstraps a new migration in that folder, while [`bin/migrations-run`](bin/migrations-run) runs all of them that haven't already run.

A snapshot of the database schema can be accessed in [`db/schema.sql`](db/schema.sql). This is regenerated on every migration and should be committed into git. It can be used to learn the current state of the database, or to bootstrap the structure for testing purposes.

### Testing: `tests`

In the long term, all logic should be tested by unit tests in this folder. Right now, tests do not cover 100% of the codebase, but they cover a fair amount of model code and contain a few smoke tests for pages.

After changing the database, you should run `scripts/dev/reset_test_database` to reset the testing database schema.

## How to build the ReadTheDocs locally

```bash
cd docs
make clean
make html
```

## External references

- CSS reset: <https://piccalil.li/blog/a-more-modern-css-reset/>
- SVG Spinners: <https://github.com/n3r4zzurr0/svg-spinners>
- Web icons: <https://github.com/tabler/tabler-icons>
- Freepik icons:
    - Bacteria: <a href="https://www.freepik.com/free-vector/bacteria-icons-set_4425882.htm">Designed by macrovector_official / Freepik</a>
    - Test tube: <a href="https://www.freepik.com/free-vector/black-white-chemical-test-tubes-icons_798687.htm">Designed by Alvaro_cabrera / Freepik</a>
    - Office icons: <a href="https://www.freepik.com/free-vector/business-office-stationery-icons-set-smartphone-tablet-notebook-computer-isolated-vector-illustration_1158166.htm">Designed by macrovector on Freepik</a>

