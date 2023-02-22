#!/bin/bash

# Manage the bluesky queueserver.

SHELL_SCRIPT_NAME=${BASH_SOURCE:-${0}}
if [ -z "$STARTUP_DIR" ] ; then
    # If no startup dir is specified, use the directory with this script
    STARTUP_DIR=$(dirname "${SHELL_SCRIPT_NAME}")
fi

#--------------------
# change the program defaults here
export BDP_CONDA_BASE=/APSshare/miniconda/x86_64
export BDP_CONDA_ENV=bluesky_2023_1
export CONDA_ENV_HOME="${HOME}/micromamba/envs"
export DATABROKER_CATALOG=8idi_xpcs
export REDIS_ADDR=localhost
export USER_GROUP_PERMISSIONS_FILE="${STARTUP_DIR}/user_group_permissions.yaml"
export USER_GROUP_PERMISSIONS_RELOAD=ON_STARTUP
#--------------------

# activate conda environment
source "${BDP_CONDA_BASE}/etc/profile.d/conda.sh"
echo "activate Python environment for bluesky and queueserver"
conda activate "${CONDA_ENV_HOME}/${BDP_CONDA_ENV}"

start-re-manager \
    --redis-addr "${REDIS_ADDR}" \
    --startup-dir "${STARTUP_DIR}" \
    --update-existing-plans-devices ENVIRONMENT_OPEN \
    --user-group-permissions "${USER_GROUP_PERMISSIONS_FILE}" \
    --user-group-permissions-reload "${USER_GROUP_PERMISSIONS_RELOAD}" \
    --zmq-publish-console ON \
    --keep-re
