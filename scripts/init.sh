#! /bin/sh

set -e

# Ensure that python modules can find their imports:
export PYTHONPATH=.

#
# Create database if it doesn't exist
#
DB_NAME=$(echo "SHOW DATABASES LIKE 'BacterialGrowth'" | bin/dbconsole | tail -1)

if [ "$DB_NAME" = "BacterialGrowth" ]; then
  # Database exists, only run migrations
  bin/migrations-run
else
  # Database does not exist, create it through a root connection:
  query="CREATE DATABASE BacterialGrowth; GRANT ALL ON BacterialGrowth.* TO bacterial_growth;"

  if [ -n "$DOCKER" ]; then
    echo "$query" | mysql \
      -u root \
      --password=nVI8imBD3bl24pcP \
      --host=mgrowthdb_mysql \
      --port=3306 \
      --protocol=tcp
  else
    echo "$query" | mysql \
      -u root \
      --password=nVI8imBD3bl24pcP \
      --host=localhost \
      --port=3307 \
      --protocol=tcp
  fi

  bin/dbconsole < db/schema.sql
fi

#
# If there are no users, create an admin one with the ID from $ADMIN_ORCID:
#
USER_COUNT=$(echo "SELECT COUNT(*) from Users;" | bin/dbconsole | tail -1)
if [ "$USER_COUNT" -eq 0 ]; then
  ORCID_ID=${ADMIN_ORCID:-"0000-0000-0000-0000"}

  echo "> No users in the database, creating an admin with ORCID: $ORCID_ID"

  echo "INSERT INTO Users (uuid, orcidId, name, isAdmin) VALUES ('_admin', '$ORCID_ID', 'The μGrowthDB team', 1)" | bin/dbconsole
fi

#
# Download and insert external data
#
if [ -f "var/external_data/ncbi/data_dump.csv" ]; then
  echo "> ChEBI data dump already downloaded"
else
  python scripts/external/chebi/download_dump.py
fi
python scripts/external/chebi/insert_data.py

if [ -f "var/external_data/ncbi/data_dump.csv" ]; then
  echo "> NCBI data dump already downloaded"
else
  python scripts/external/ncbi/download_dump.py
fi
python scripts/external/ncbi/insert_data.py

#
# Create initial studies:
#
python scripts/bootstrap/create_initial_studies.py
