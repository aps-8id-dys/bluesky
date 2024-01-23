"""
APS BDP demo: 2024-02
"""

__all__ = """
    bdp_demo_acquire_and_workflow
    bdp_developer_run_daq_and_wf
    prj_test
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

# from ..utils import get_workflow_last_stage
# from ..utils import WorkflowCache
from ..utils import MINUTE
from ..utils import build_run_metadata_dict
from ..utils import dm_api_ds
from ..utils import dm_api_proc
from ..utils import dm_file_ready_to_process
from ..utils import dm_get_daqs
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
DM_FILE_READY_CHECK_INTERVAL_S = 1.0


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
    uids = yield from lineup2(
        [sim1d], motor, -0.55, 0.55, 79
    )  # TODO: md=_md in apstools 1.6.18
    logger.debug("Bluesky RunEngine uids=%s", uids)
    return uids


def bdp_developer_run_daq_and_wf(
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

    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
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

    # TODO: Wait for file writing.
    #   For any data transfers or file writing to complete before running the workflow.
    # while not dm_files_ready_to_process(filename, experiment_name):
    #     yield from bps.sleep(1)  # TODO: What interval?

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

    logger.info("Finished: bdp_developer_run_daq_and_wf()")


def _pick_area_detector(detector_name):
    from ..devices import adsim4M
    from ..devices import eiger4M
    from ..devices import lambda2M

    detectors = {d.name: d for d in (adsim4M, eiger4M, lambda2M) if d is not None}
    det = detectors.get(detector_name)
    if det is None:
        raise KeyError(
            f"Available detectors: {', '.join(detectors.keys())}."
            f"  Received: {detector_name!r}"
        )
    return det


def _get_experiment_data_path(experiment_name):
    import pathlib

    daqs = dm_get_daqs(experiment_name)
    if len(daqs) == 0:
        raise RuntimeError(
            f"No APS Data Management DAQ running for {experiment_name=!r}."
            "  Need at least one running."
        )
    # pick the path from the first one
    data_path = daqs[0]["dataDirectory"]
    if data_path.startswith("@voyager:"):
        data_path = data_path[len("@voyager:") :]
    return pathlib.Path(data_path)


def bdp_demo_acquire_and_workflow(
    workflow_name: str = DM_WORKFLOW_NAME,
    title: str = TITLE,
    description: str = DESCRIPTION,
    # detector parameters ----------------------------------------
    detector_name: str = "eiger4M",
    acquire_time: float = 0.01,
    acquire_period: float = 0.01,
    num_capture: int = 1,
    num_exposures: int = 1,
    num_images: int = 1_000,
    num_triggers: int = 1,
    # internal kwargs ----------------------------------------
    dm_waiting_time=DEFAULT_WAITING_TIME,
    dm_wait=False,
    dm_concise=False,
    # user-supplied metadata ----------------------------------------
    md: dict = DEFAULT_RUN_METADATA,
):
    """
    Acquire XPCS data with the chosen detector and run a DM workflow.
    """
    #
    # *** Prepare. ***
    #
    det = _pick_area_detector(detector_name)

    experiment_name = dm_experiment.get()
    if len(experiment_name) == 0:
        raise RuntimeError("Must run setup_user() first.")
    experiment = dm_api_ds().getExperimentByName(experiment_name)
    logger.info("DM experiment: %s", experiment_name)

    data_path = _get_experiment_data_path(experiment_name)

    # _md is for a bluesky open run
    _md = build_run_metadata_dict(
        md,
        detector_name=detector_name,
        acquire_time=acquire_time,
        acquire_period=acquire_period,
        num_capture=num_capture,
        num_exposures=num_exposures,
        num_images=num_images,
        num_triggers=num_triggers,
        owner=dm_api_proc().username,
        workflow=workflow_name,
        title=title,
        description=description,
        dataDir=experiment["dataDirectory"],
        concise=dm_concise,
        storageDirectory=experiment["storageDirectory"],
    )

    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    yield from bps.mv(dm_workflow.concise_reporting, dm_concise)

    #
    # *** Run the data acquisition. ***
    #
    def acquire():
        if detector_name == "eiger4M":
            from .ad_setup_plans import eiger4M_daq_setup

            # TODO: setup HDF5 plugin
            yield from eiger4M_daq_setup(
                acquire_time=acquire_time,
                acquire_period=acquire_period,
                num_capture=num_capture,
                num_exposures=num_exposures,
                num_images=num_images,
                num_triggers=num_triggers,
                path=data_path,
            )
        uid = yield from bp.count([det], md=_md)
        return uid

    uids = yield from acquire()

    if uids is None:
        run = cat[-1]  # risky
    elif isinstance(uids, str):
        run = cat[uids]
    else:
        run = cat[uids[0]]  # assumption

    #
    # *** Wait for data writing & transfers to complete. ***
    #
    filenames = [
        # TODO: HDF detector images
        # TODO: XPCS experiment metadata
        # TODO: logs
    ]
    for filename in filenames:
        while not dm_file_ready_to_process(filename, experiment_name):
            yield from bps.sleep(DM_FILE_READY_CHECK_INTERVAL_S)

    #
    # *** Start the APS Data Management workflow. ***
    #
    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=dm_wait,
        timeout=dm_waiting_time,
        # all kwargs after this line are DM argsDict content
        filePath=_md["data_management"]["storageDirectory"],
    )

    # upload bluesky run metadata to APS DM
    share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

    logger.info("Finished: bdp_demo_acquire_and_workflow()")


def prj_test():
    """Developer shortcut plan."""
    yield from setup_user("20240110-jemian")
    # yield from bdp_developer_run_daq_and_wf(demo=demo, dm_wait=True)
    yield from bdp_demo_acquire_and_workflow(dm_wait=True)
