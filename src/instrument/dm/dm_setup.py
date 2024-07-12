"""
Setup for for this beam line's APS Data Management Python API client.
"""

__all__ = """
    DM_WORKFLOW_OWNER
""".split()


import logging
import os
import pathlib

from ..utils.iconfig_loader import iconfig

logger = logging.getLogger(__name__)

logger.info(__file__)

DM_SETUP_FILE = iconfig.get("DM_SETUP_FILE")
DM_WORKFLOW_OWNER = os.environ.get("DM_STATION_NAME", "unknown").lower()

if DM_SETUP_FILE is None:
    logger.info("APS DM setup file is not defined.  Not configuring.")
else:
    # parse environment variables from bash script
    setup_file = pathlib.Path(DM_SETUP_FILE)
    logger.info("APS DM environment file: %s", str(setup_file))
    print(f"APS DM environment file '{setup_file}'")
    environment_variables = {}
    export_ = "export "
    for line in open(setup_file).readlines():
        if not line.strip().startswith(export_):
            continue
        assignment = line.strip()[len(export_) :]
        k, v = assignment.split("=")
        environment_variables[k] = v

    os.environ.update(environment_variables)
    DM_WORKFLOW_OWNER = environment_variables.get("DM_STATION_NAME", "unknown").lower()
    logger.info("APS DM workflow owner: %s", DM_WORKFLOW_OWNER)
