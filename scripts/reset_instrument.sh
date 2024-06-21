#!/usr/bin/env bash


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR=$SCRIPT_DIR/..

echo $BASE_DIR
cd $BASE_DIR
pwd

OLD_INSTRUMENT_PREFIX=aps_8id
NEW_INSTRUMENT_PREFIX=empty

OLD_INSTRUMENT_NAME=${OLD_INSTRUMENT_PREFIX}_bs_instrument
NEW_INSTRUMENT_NAME=${NEW_INSTRUMENT_PREFIX}_bs_instrument
OLD_QS_NAME=${OLD_INSTRUMENT_PREFIX}_bs_qserver
NEW_QS_NAME=${NEW_INSTRUMENT_PREFIX}_bs_qserver


##remove extra folders
rm -rf .ruff_cache
rm -rf *.egg-info
rm -rf build
rm -rf __pycache__

##reset analysis folder
rm -rf ./src/$OLD_INSTRUMENT_NAME/analysis/*
touch ./src/$OLD_INSTRUMENT_NAME/analysis/__init__.py

##reset callbacks folder
rm -rf ./src/$OLD_INSTRUMENT_NAME/callbacks/*
touch ./src/$OLD_INSTRUMENT_NAME/callbacks/__init__.py

##reset devices folder
rm -rf ./src/$OLD_INSTRUMENT_NAME/devices/*
touch ./src/$OLD_INSTRUMENT_NAME/devices/__init__.py

##reset plans folder
rm -rf ./src/$OLD_INSTRUMENT_NAME/plans/*
touch ./src/$OLD_INSTRUMENT_NAME/plans/__init__.py

##remove custom scripts
rm -rf ./scripts/user

##rename src/instrument folder
mv src/$OLD_INSTRUMENT_NAME src/$NEW_INSTRUMENT_NAME

##rename qserver
mv src/$OLD_QS_NAME src/$NEW_QS_NAME

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
