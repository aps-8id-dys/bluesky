"""
APS BDP demo: 2024-02
"""

__all__ = """
    prj_test
    run_daq_and_wf
    setup_user
""".split()

import logging

from ophyd import Signal

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp

from .._iconfig import iconfig
from ..devices import DM_WorkflowConnector
from ..devices import dm_experiment
from ..devices import motor
from ..devices import sim1d
from ..framework import cat
from ..plans import lineup2
from ..utils import MINUTE
from ..utils import WorkflowCache
from ..utils import build_run_metadata_dict
from ..utils import dm_api_ds
from ..utils import dm_api_proc
from ..utils import get_workflow_last_stage
from ..utils import share_bluesky_metadata_with_dm



logger = logging.getLogger(__name__)
logger.info(__file__)

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


def count_sensor_plan(md):
    """Standard count plan with custom sensor."""
    uids = yield from bp.count([sensor], md=md)
    logger.debug("Bluesky RunEngine uids=%s", uids)
    return uids


def example_scan(md):
    """Example data acquisition plan."""
    # TODO: user_plan(args, kwargs)
    yield from bps.mv(motor, 1.25)
    uids = yield from lineup2([sim1d], motor, -.55, .55, 79)  # TODO: md=_md in apstools 1.6.18
    logger.debug("Bluesky RunEngine uids=%s", uids)
    return uids


def run_daq_and_wf(
    workflow_name: str = DM_WORKFLOW_NAME,
    title: str = TITLE,
    description: str = DESCRIPTION,
    demo: int = 0,
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
    # # WorkflowCache is useful when a plan uses multiple workflows.
    # # For XPCS, it is of little value but left here for demonstration.
    # wf_cache = WorkflowCache()
    # wf_cache.define_workflow("XCPS", dm_workflow)
    yield from bps.mv(dm_workflow.concise_reporting, dm_concise)

    @bpp.run_decorator(md=_md)
    def user_plan_too(*args, **kwargs):
        yield from bps.trigger_and_read([sensor])
        yield from bps.trigger_and_read([dm_workflow], "dm_workflow")

    #
    # *** Run the data acquisition. ***
    #
    if demo == 0:
        uids = yield from count_sensor_plan(_md)
    elif demo == 1:
        uids = yield from example_scan(_md)
    else:
        uids = yield from user_plan_too()

    if uids is None:
        run = cat[-1]  # risky
    elif isinstance(uids, str):
        run = cat[uids]
    else:
        run = cat[uids[0]]

    #
    # *** Start this APS Data Management workflow after the run completes. ***
    #
    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=dm_wait,
        timeout=dm_waiting_time,
        # all kwargs after this line are DM argsDict content
        filePath=_md["data_management"]["storageDirectory"],
    )

    # yield from wf_cache.wait_workflows(wait=dm_wait)

    # wf_cache._update_processing_data()
    # wf_cache.print_cache_summary()
    # wf_cache.report_dm_workflow_output(get_workflow_last_stage(workflow_name))

    # upload bluesky run metadata to APS DM
    share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

    logger.info("Finished: run_workflow_only()")


def prj_test(demo: int = 0):
    yield from setup_user("20240110-jemian")
    yield from run_daq_and_wf(demo=demo, dm_wait=True)
