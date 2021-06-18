#! /usr/bin/env sh

# create the path for sqlite data
mkdir -p /mblocks/server/main
python scripts/initial_database.py
python scripts/initial_data.py
python scripts/initial_services.py
