#! /bin/sh

set -e

echo "This script will DROP the development database and recreate it"
read -p "Type 'RESET' to continue: " -r
if [[ $REPLY != RESET ]]
then
  exit 1
fi

# Reset dev database
mysql -u root --password=nVI8imBD3bl24pcP --port=3307 --protocol=tcp <<EOF
  drop database if exists BacterialGrowth;
  create database BacterialGrowth;
  grant all on BacterialGrowth.* to bacterial_growth;
EOF

bin/dbconsole < db/schema.sql

# Create an admin user
echo "INSERT INTO Users (uuid, orcidId, orcidToken, name, isAdmin) VALUES ('_admin', '<placeholder>', '<placeholder>', 'The μGrowthDB team', 1)" | bin/dbconsole

# Download and insert external data
python scripts/external/chebi/download_dump.py
python scripts/external/chebi/insert_data.py

python scripts/external/ncbi/download_dump.py
python scripts/external/ncbi/insert_data.py

# Bootstrap studies
python scripts/bootstrap/create_initial_studies.py
