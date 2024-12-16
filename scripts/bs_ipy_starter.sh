#!/bin/bash

echo "You chose ipython!"
# Standard BCDA setup at APS defines this pointing to APSshare.
# We choose here to get PyEpics from the conda environment.
# Use this environment: conda activate bluesky_2024_3
unset PYEPICS_LIBCA # TODO: Need to fix this more permenantly

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )" # This allows for command to be run from anywhere

ipython -i -c "%run $SCRIPT_DIR/bs_ipy_profile.ipy"
