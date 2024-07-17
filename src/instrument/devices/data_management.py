"""
Connect with APS Data Management workflows.

from: https://github.com/APS-1ID-MPE/hexm-bluesky/blob/main/instrument/devices/data_management.py
"""

__all__ = """
    dm_experiment
    DM_WorkflowConnector
    dm_workflow
""".split()


import logging

from ophyd import Signal

from ..dm.aps_data_management import dm_api_proc

# from apstools.devices import DM_WorkflowConnector
from ._apstools_data_management import DM_WorkflowConnector

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # allow any log content at this level
logger.info(__file__)

# TODO: 'labels=("DM")' kwarg is ignored for non-EPICS devices.  Refactor to ophyd_registry?
dm_workflow = DM_WorkflowConnector(name="dm_workflow")
dm_workflow.owner.put(dm_api_proc().username)
# RE(dm_workflow.run_as_plan(workflow="example-01", filePath="/home/beams/S1IDTEST/.bashrc"))

# TODO: make this an EpicsSignal instead
dm_experiment = Signal(name="dm_experiment", value="")
