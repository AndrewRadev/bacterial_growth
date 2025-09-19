# Installation

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

In the database config directory, the file `db/config.toml.example` contains a template for the database configuration. Copy this file to `db/config.toml` and update it with the correct credentials to access a running mysql database. You can launch one by using the provided "services" dockerfile:

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
