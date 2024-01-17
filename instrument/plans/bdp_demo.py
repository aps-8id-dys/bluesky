"""
APS BDP demo: 2024-02
"""

__all__ = """
    setup_user
    run_workflow_only
""".split()

import logging

from ophyd import Signal

from bluesky import plan_stubs as bps
from bluesky import plans as bp

# from bluesky import preprocessors as bpp

logger = logging.getLogger(__name__)
logger.info(__file__)

from .._iconfig import iconfig  # noqa
from ..devices import DM_WorkflowConnector  # noqa
from ..devices import dm_experiment  # noqa
from ..framework import cat  # noqa
from ..utils import MINUTE  # noqa
from ..utils import WorkflowCache  # noqa
from ..utils import build_run_metadata_dict  # noqa
from ..utils import dm_api_ds  # noqa
from ..utils import dm_api_proc  # noqa
from ..utils import get_workflow_last_stage  # noqa
from ..utils import share_bluesky_metadata_with_dm  # noqa

sensor = Signal(name="sensor", value=1.23456)  # TODO: developer

DM_WORKFLOW_NAME = iconfig.get("DM_WORKFLOW_NAME", "example-01")
TITLE = "BDP XPCS demo"
DESCRIPTION = "Demonstrate XPCS data acquisition and analysis."
DEFAULT_RUN_METADATA = {"title": TITLE, "description": DESCRIPTION}
DEFAULT_WAITING_TIME = (
    2 * MINUTE
)  # bluesky will raise TimeoutError if DM workflow is not done in this time


def setup_user(dm_experiment_name: str):
    """
    Configure bluesky session for this user.

    PARAMETERS

    dm_experiment_name *str*:
    """
    from ..utils import dm_isDaqActive
    from ..utils import dm_start_daq

    # Check that named experiment actually exists now.
    # Raises dm.ObjectNotFound if does not exist.
    dm_api_ds().getExperimentByName(dm_experiment_name)
    yield from bps.mv(dm_experiment, dm_experiment_name)

    # Full path to directory where new data will be written.
    # XPCS new data is written to APS Voyager storage (path
    # starting with ``/gdata/``).  Use "@voyager" in this case.
    # DM sees this and knows not copy from voyager to voyager.
    data_directory = "@voyager"

    # Check DM DAQ is running for this experiment, if not then start it.
    if not dm_isDaqActive(dm_experiment_name):
        # Need another DAQ if also writing to a different directory (off voyager).
        # A single DAQ can be used to cover any subdirectories.
        # Anything in them will be uploaded.
        logger.info(
            "Starting DM DAQ: experiment %r in data directory %r",
            dm_experiment_name,
            data_directory,
        )
        dm_start_daq(dm_experiment_name, data_directory)

    # TODO: What else?


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
    # WorkflowCache is useful when a plan uses multiple workflows.
    # For XPCS, it is of little value but left here for demonstration.
    wf_cache = WorkflowCache()
    wf_cache.define_workflow("XCPS", dm_workflow)
    yield from bps.mv(dm_workflow.concise_reporting, dm_concise)

    def user_data_acquisition_wrapper_plan():
        """Wrapper for user's data acquisition plan."""
        # TODO: user_plan(args, kwargs)
        uid = yield from bp.count([sensor], md=_md)
        logger.debug("Bluesky RunEngine uid=%s", uid)
        return uid

    uid = yield from user_data_acquisition_wrapper_plan()
    print(f"DIAGNOSTIC outer: {uid=}")

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

    # upload bluesky run metadata to APS DM
    run = cat[uid]
    share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

    logger.info("Finished: run_workflow_only()")
