#!/usr/bin/env bash


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR=$SCRIPT_DIR/..

echo $BASE_DIR
cd $BASE_DIR
pwd

OLD_INSTRUMENT_PREFIX=aps_8id
NEW_INSTRUMENT_PREFIX=empty

##remove extra folders
rm -rf .ruff_cache
rm -rf *.egg-info
rm -rf build
rm -rf __pycache__

##reset analysis folder
rm -rf ./src/instrument/analysis/*
sed -i '6,$d' ./src/instrument/analysis/__init__.py

##reset callbacks folder
rm -rf ./src/instrument/callbacks/*
sed -i '6,$d' ./src/instrument/callbacks/__init__.py

##reset devices folder
rm -rf ./src/instrument/devices/*
sed -i '6,$d' ./src/instrument/devices/__init__.py

##reset plans folder
rm -rf ./src/instrument/plans/*
sed -i '6,$d' ./src/instrument/plans/__init__.py

##remove custom scripts
rm -rf ./scripts/user

##rename absolute calls to the new package in scripts


##rename parts inside pyproject.toml
## line 2 name
## line 3 version back to 0.0.1
## line 4 Description back to generic
## line 32 homepage to blank
## line 33 Downloads to blank
## line 44 change package name
##consider always calling the package folder "instrument"/"queue_server"

##rename README.md
##line1
##line31/32 link to project
##line38 make it generic
