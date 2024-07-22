#!/bin/bash

# Start the bluesky queueserver.

#--------------------
# change the program defaults here
# CONDA: pre-defined in GitHub Actions workflow
export CONDA=${CONDA:-/APSshare/miniconda/x86_64}
export CONDA_ENVIRONMENT="${BLUESKY_CONDA_ENV:-__BLUESKY_CONDA_ENV_not_defined__}"
if [ "${DATABROKER_CATALOG}" == "" ]; then
    SCRIPT_DIR=$(dirname $(readlink -f "${0}"))
    DATABROKER_CATALOG=$(grep DATABROKER_CATALOG ${SCRIPT_DIR}/../src/instrument/iconfig.yml  | awk '{print $NF}')
    echo "Using catalog ${DATABROKER_CATALOG}"
fi
export QS_SERVER_HOST=$(hostname)  # or host (that passes $(hostname) test below)
export QS_UPDATE_PLANS_DEVICES=ENVIRONMENT_OPEN
export QS_USER_GROUP_PERMISSIONS_FILE="${SCRIPT_DIR}/../src/instrument/config/user_group_permissions.yaml"
export QS_USER_GROUP_PERMISSIONS_RELOAD=ON_STARTUP

# REDIS_ADDR is __always__ localhost.
# Override if it is not, but you may encounter access issues.  YOYO.
export REDIS_ADDR=localhost
#--------------------

# QS and redis must be on the same workstation
if [ "$(hostname)" != "${QS_SERVER_HOST}" ]; then
    echo "Must run queueserver on ${QS_SERVER_HOST}.  This is $(hostname)"
    exit 1
fi

SHELL_SCRIPT_NAME=${BASH_SOURCE:-${0}}
if [ -z "$STARTUP_DIR" ] ; then
    # If no startup dir is specified, use the directory with this script
    export STARTUP_DIR=$(dirname "${SHELL_SCRIPT_NAME}")
fi

# echo "CONDA_EXE = '${CONDA_EXE}'"
if [ ! -f "${CONDA_EXE}" ]; then
    echo "No 'conda' command available."
    exit 1
fi

# In GitHub Actions workflow,
# $ENV_NAME is an environment variable naming the conda environment to be used
if [ -z "${ENV_NAME}" ] ; then
    ENV_NAME="${CONDA_ENVIRONMENT}"
fi

if [ "${CONDA_DEFAULT_ENV}" != "${ENV_NAME}" ]; then
    echo "Activating conda environment ${ENV_NAME}"
    CONDA_BASE="$(dirname $(dirname $(readlink -f ${CONDA_EXE})))"
    source "${CONDA_BASE}/etc/profile.d/conda.sh"
    conda activate "${ENV_NAME}"
fi
# echo "conda env list = $(conda env list)"

# #--------------------
# echo "Environment: $(env | sort)"
# echo "------"
# echo "CONDA_ENVIRONMENT=${CONDA_ENVIRONMENT}"
# echo "CONDA=${CONDA}"
# echo "DATABROKER_CATALOG=${DATABROKER_CATALOG}"
# echo "QS_SERVER_HOST=${QS_SERVER_HOST}"
# echo "QS_UPDATE_PLANS_DEVICES=${QS_UPDATE_PLANS_DEVICES}"
# echo "QS_USER_GROUP_PERMISSIONS_FILE=${QS_USER_GROUP_PERMISSIONS_FILE}"
# echo "QS_USER_GROUP_PERMISSIONS_RELOAD=${QS_USER_GROUP_PERMISSIONS_RELOAD}"
# echo "REDIS_ADDR=${REDIS_ADDR}"
# echo "SHELL_SCRIPT_NAME=${SHELL_SCRIPT_NAME}"
# echo "STARTUP_DIR=${STARTUP_DIR}"
# #--------------------

# Start the bluesky queueserver (QS)
start-re-manager \
    --redis-addr "${REDIS_ADDR}" \
    --startup-dir "${STARTUP_DIR}" \
    --update-existing-plans-devices "${QS_UPDATE_PLANS_DEVICES}" \
    --user-group-permissions "${QS_USER_GROUP_PERMISSIONS_FILE}" \
    --user-group-permissions-reload "${QS_USER_GROUP_PERMISSIONS_RELOAD}" \
    --zmq-publish-console ON \
    --keep-re
