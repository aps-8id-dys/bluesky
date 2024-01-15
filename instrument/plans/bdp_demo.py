"""
APS BDP demo: 2024-02
"""

__all__ = """
    setup_user
    run_workflow_only
""".split()

import logging

from bluesky import plan_stubs as bps

# from bluesky import plans as bp

logger = logging.getLogger(__name__)
logger.info(__file__)

from .._iconfig import iconfig  # noqa
from ..devices import dm_experiment  # noqa
from ..devices import DM_WorkflowConnector  # noqa
from ..utils import build_run_metadata_dict  # noqa
from ..utils import dm_api_ds  # noqa
from ..utils import dm_api_proc  # noqa
from ..utils import get_workflow_last_stage  # noqa
from ..utils import MINUTE  # noqa
from ..utils import WorkflowCache  # noqa

DM_WORKFLOW_NAME = iconfig.get("DM_WORKFLOW_NAME", "example-01")
TITLE = "BDP XPCS demo"
DESCRIPTION = "Demonstrate XPCS data acquisition and analysis."
DEFAULT_RUN_METADATA = {"title": TITLE, "description": DESCRIPTION}
DEFAULT_WAITING_TIME = 2 * MINUTE  # bluesky will raise TimeoutError if DM is not done


def setup_user(dm_experiment_name: str):
    """Configure bluesky session for this user."""
    # Check that named experiment actually exists now.
    # Raises dm.ObjectNotFound if does not exist.
    dm_api_ds().getExperimentByName(dm_experiment_name)
    yield from bps.mv(dm_experiment, dm_experiment_name)
    # TODO: What else?
    """
    Check DM DAQ is running for this experiment, if not then start it.  There is
    a DAQ API for this.

    DAQ should be started before bluesky writes any files.

    User option to stop DAQ after bluesky run (default: False).

    There is a function to inform if DAQ is active:
    <!-- [3:29 PM] Parraga, Hannah -->
    production/src/python/dm/aps_beamline_tools/common/dataTransferMonitor.py

    def isDaqActive(self, experimentName: str) -> bool:

    https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/HowTos/Getting-Started

    Look at:
    dataTransferMonitor.DataTransferMonitor.isDaqActive(experiment_name)
    """


def run_workflow_only(
    workflow_name: str = DM_WORKFLOW_NAME,
    title: str = TITLE,
    description: str = DESCRIPTION,
    # internal kwargs ----------------------------------------
    dm_waiting_time=DEFAULT_WAITING_TIME,
    dm_wait=False,
    dm_concise=False,
    # user-supplied metadata ----------------------------------------
    md: dict = DEFAULT_RUN_METADATA,
):
    """Run the named DM workflow with the Bluesky RE."""
    experiment_name = dm_experiment.get()
    if len(experiment_name) == 0:
        raise RuntimeError("Must run setup_user() first.")
    experiment = dm_api_ds().getExperimentByName(experiment_name)
    logger.info("DM experiment: %s", experiment_name)
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")

    # _md is for a bluesky open run
    _md = build_run_metadata_dict(
        md,
        owner=dm_api_proc().username,
        workflow=workflow_name,
        title=title,
        description=description,
        dataDir=experiment["dataDirectory"],
        concise=dm_concise,
        storageDirectory=experiment["storageDirectory"],
    )

    dm_workflow = DM_WorkflowConnector(name="dm_workflow", labels=["DM"])
    wf_cache = WorkflowCache()
    wf_cache.define_workflow("XCPS", dm_workflow)
    yield from bps.mv(dm_workflow.concise_reporting, dm_concise)

    # TODO: data acquisition here

    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=dm_wait,
        timeout=dm_waiting_time,
        # all kwargs after this line are DM argsDict content
        filePath=_md["data_management"]["storageDirectory"],
    )

    yield from wf_cache.wait_workflows(wait=dm_wait)

    wf_cache._update_processing_data()
    wf_cache.print_cache_summary()
    wf_cache.report_dm_workflow_output(get_workflow_last_stage(workflow_name))
    logger.info("Finished: run_workflow_only()")
    # TODO: update DM workflow metadata
