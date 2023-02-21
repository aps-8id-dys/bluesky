#!/bin/bash

# Manage the bluesky queueserver.

#--------------------
# change the program defaults here
export DATABROKER_CATALOG=8idi_xpcs
export CONDA_ENV_HOME="${HOME}/micromamba/envs"
export BDP_CONDA_ENV=bluesky_2023_1
export BDP_CONDA_BASE=/APSshare/miniconda/x86_64
#--------------------

# activate conda environment
source "${BDP_CONDA_BASE}/etc/profile.d/conda.sh"
echo "activate Python environment for bluesky and queueserver"
conda activate "${CONDA_ENV_HOME}/${BDP_CONDA_ENV}"

SHELL_SCRIPT_NAME=${BASH_SOURCE:-${0}}
if [ -z "$STARTUP_DIR" ] ; then
    # If no startup dir is specified, use the directory with this script
    STARTUP_DIR=$(dirname "${SHELL_SCRIPT_NAME}")
fi

start-re-manager \
    --startup-dir "${STARTUP_DIR}" \
    --update-existing-plans-devices ENVIRONMENT_OPEN \
    --zmq-publish-console ON \
    --keep-re
