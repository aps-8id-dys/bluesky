"""
Connect with APS Data Management workflows.

from: https://github.com/APS-1ID-MPE/hexm-bluesky/blob/main/instrument/devices/data_management.py
"""

__all__ = """
    DM_WorkflowConnector
    dm_workflow
""".split()

import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # allow any log content at this level
logger.info(__file__)

from apstools.devices import DM_WorkflowConnector

DM_STATION_NAME = str(os.environ.get("DM_STATION_NAME", "unknown")).lower()


dm_workflow = DM_WorkflowConnector(name="dm_workflow", labels=["DM"])
dm_workflow.owner.put(DM_STATION_NAME)
# RE(dm_workflow.run_as_plan(workflow="example-01", filePath="/home/beams/S1IDTEST/.bashrc"))
