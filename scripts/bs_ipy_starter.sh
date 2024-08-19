#!/bin/bash

echo "You chose ipython!"
# Standard BCDA setup at APS defines this pointing to APSshare.
# We choose here to get PyEpics from the conda environment.
unset PYEPICS_LIBCA # TODO: Need to fix this more permenantly
ipython -i -c "%run bs_ipy_profile.ipy"
