#!/bin/bash

echo "You chose ipython!"
# Standard BCDA setup at APS defines this pointing to APSshare.
# We choose here to get PyEpics from the conda environment.
unset PYEPICS_LIBCA # TODO: Need to fix this more permenantly

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ipython -i -c "%run $SCRIPT_DIR/bs_ipy_profile.ipy"