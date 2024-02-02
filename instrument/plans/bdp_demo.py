"""
APS BDP demo: 2024-02
"""

__all__ = """
    bdp_demo_plan
    reset_xpcs_index
    setup_user
""".split()
# bdp_developer_run_daq_and_wf
__all__ += """
    bdp_demo_run_daq_and_wf
    bdp_developer_run_daq_and_wf
    prj_test
    _pick_area_detector
    _xpcsFileNameBase
    _xpcsDataDir
""".split()

import logging
import pathlib

from apstools.utils import cleanupText
from ophyd import Signal

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp

from .._iconfig import iconfig
from ..callbacks.nexus_data_file_writer import nxwriter
from ..devices import DM_WorkflowConnector
from ..devices import dm_experiment
from ..devices import motor
from ..devices import sim1d
from ..framework import RE
from ..framework import cat
from ..utils import MINUTE
from ..utils import SECOND
from ..utils import build_run_metadata_dict
from ..utils import dm_api_ds
from ..utils import dm_api_proc
from ..utils import share_bluesky_metadata_with_dm
from . import lineup2
from .ad_setup_plans import write_if_new

logger = logging.getLogger(__name__)
logger.info(__file__)

sensor = Signal(name="sensor", value=1.23456)  # TODO: developer
xpcs_header = Signal(name="xpcs_header", value=RE.md.get("xpcs_header", "A001"))
xpcs_index = Signal(name="xpcs_index", value=RE.md.get("xpcs_index", 0))

DEFAULT_DETECTOR_NAME = "eiger4M"
DM_WORKFLOW_NAME = iconfig.get("DM_WORKFLOW_NAME", "example-01")
TITLE = "BDP_XPCS_demo"  # keep this short, single-word
DESCRIPTION = "Demonstrate XPCS data acquisition and analysis."
DEFAULT_RUN_METADATA = {"title": TITLE, "description": DESCRIPTION}
DEFAULT_WAITING_TIME = 2 * MINUTE  # time limit for bluesky reporting
# bluesky will raise TimeoutError if DM workflow is not done by DEFAULT_WAITING_TIME
DAQ_UPLOAD_WAIT_PERIOD = 1.0 * SECOND
DAQ_UPLOAD_PREFIX = "ftp://s8ididm:2811"

QMAP_BASE = pathlib.Path("/home/beams/8IDIUSER/Documents/Miaoqi/standard_qmaps")
QMAPS = {
    "adsim4M": QMAP_BASE / "adsim4M_qmap_d36_s360.h5",
    "eiger4M": QMAP_BASE / "eiger4M_qmap_d36_s360.h5",
}


def setup_user(dm_experiment_name: str, index: int = 0):
    """
    Configure bluesky session for this user.

    PARAMETERS

    dm_experiment_name *str*:

    .. note:: Set ``index=-1`` to continue with current 'xpcs_index' value.
    """
    from ..utils import dm_isDaqActive
    from ..utils import dm_start_daq
    from ..utils import validate_experiment_dataDirectory

    validate_experiment_dataDirectory(dm_experiment_name)
    yield from bps.mv(dm_experiment, dm_experiment_name)

    if index >= 0:
        yield from write_if_new(xpcs_index, index)
    RE.md["xpcs_index"] = xpcs_index.get()

    # Needed when data acquisition (Bluesky, EPICS, ...) writes to Voyager.
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


def reset_xpcs_index(index: int = 0):
    """
    (Re)set the 'xpcs_index'.  Default=0.

    Data directory and file names are defined by the 'xpcs_header' and
    the`xpcs_index'.  The `xpcs_index' increments at the start of each
    'bdp_demo_plan()', the data acquisition plan. The 'xpcs_header' is specified
    as a kwarg, as in this example: 'bdp_demo_plan(header="B123")'
    """
    yield from write_if_new(xpcs_index, index)


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

    # Create an ophyd object to manage the workflow.
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    yield from bps.mv(dm_workflow.concise_reporting, dm_concise)

    # # WorkflowCache is useful when a plan uses multiple workflows.
    # # For XPCS, it is of little value but left here for demonstration.
    # wf_cache = WorkflowCache()
    # wf_cache.define_workflow("XCPS", dm_workflow)

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


def bdp_demo_run_daq_and_wf(
    # workflow_name: str = DM_WORKFLOW_NAME,
    title: str = TITLE,
    description: str = DESCRIPTION,
    demo: int = 0,
    # ------ workflow args
    location: str = "local",  # or "polaris"
    # internal kwargs ----------------------------------------
    dm_waiting_time=DEFAULT_WAITING_TIME,
    dm_wait=False,
    dm_concise=False,
    # user-supplied metadata ----------------------------------------
    md: dict = DEFAULT_RUN_METADATA,
):
    """Run the named DM workflow with the Bluesky RE."""
    workflow_name = f"xpcs8-apsu-dev-{location}"
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

    # Create an ophyd object to manage the workflow.
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    yield from bps.mv(dm_workflow.concise_reporting, dm_concise)

    # # WorkflowCache is useful when a plan uses multiple workflows.
    # # For XPCS, it is of little value but left here for demonstration.
    # wf_cache = WorkflowCache()
    # wf_cache.define_workflow("XCPS", dm_workflow)

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
        # such as pete7.h5 (will also need pete7.hdf)
        filePath=_md["data_management"][
            "storageDirectory"
        ],  # FIXME: name of the raw file
        experiment=dm_experiment.get(),
        qmap="name of qmap file.h5",  # FIXME
        smoooth="sqmap",
        gpuID=-1,
        beginFrame=1,
        endFrame=-1,
        strideFrame=1,
        avgFrame=1,
        type="Multitau",
        dq="all",
        verbose=False,
        saveG2=False,
        overwrite=False,
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


def _header_index():
    return f"{xpcs_header.get()}_{xpcs_index.get():03d}"


def _xpcsDataDir(title: str, nframes: int = 0):
    experiment = dm_api_ds().getExperimentByName(dm_experiment.get())
    return f"{experiment['dataDirectory']}/{_xpcsFileNameBase(title, nframes)}"


def _xpcsFileNameBase(title: str, nframes: int = 0):
    return f"{_header_index()}_{title}-{nframes:05d}"


def _xpcsFullFileName(title: str, suffix: str = ".hdf", nframes: int = 0):
    base = _xpcsFileNameBase(title, nframes)
    return f"{_xpcsDataDir(title, nframes)}/{base}{suffix}"


def bdp_demo_plan(
    title: str = TITLE,
    description: str = DESCRIPTION,
    header: str = xpcs_header.get(),
    analysisMachine="amazonite",  # or "adamite", or "polaris"
    qmap_file: str = str(QMAPS.get(DEFAULT_DETECTOR_NAME, "/path/to/qmap_file.hdf")),
    # detector parameters ----------------------------------------
    detector_name: str = DEFAULT_DETECTOR_NAME,
    acquire_time: float = 0.01,
    acquire_period: float = 0.01,
    num_exposures: int = 1,
    num_images: int = 1_000,
    num_triggers: int = 1,
    # DM workflow kwargs ----------------------------------------
    wf_smooth="sqmap",
    wf_gpuID=-1,
    wf_beginFrame=1,
    wf_endFrame=-1,
    wf_strideFrame=1,
    wf_avgFrame=1,
    wf_type="Multitau",
    wf_dq="all",
    wf_verbose=False,
    wf_saveG2=False,
    wf_overwrite=False,
    # internal kwargs ----------------------------------------
    dm_waiting_time=DEFAULT_WAITING_TIME,
    dm_wait=False,
    dm_concise=False,
    nxwriter_warn_missing: bool = False,
    # user-supplied metadata ----------------------------------------
    md: dict = DEFAULT_RUN_METADATA,
):
    """
    Acquire XPCS data with the chosen detector and run a DM workflow.
    """
    from ..utils.aps_data_management import dm_api_daq
    from ..utils.aps_data_management import dm_daq_wait_upload_plan
    from .ad_setup_plans import setup_hdf5_plugin

    #
    # *** Prepare. ***
    #
    analysisMachine = analysisMachine.lower()  # to be safe
    if analysisMachine in ("adamite", "amazonite"):
        workflow_name = "xpcs8-apsu-dev-local"
    elif analysisMachine in ("polaris"):
        workflow_name = "xpcs8-apsu-dev-polaris"
    else:
        raise ValueError(
            f"Received {analysisMachine=!r}."
            '  Must be one of these: "adamite", "amazonite", "polaris"'
        )

    det = _pick_area_detector(detector_name)
    experiment_name = dm_experiment.get()
    if len(experiment_name) == 0:
        raise RuntimeError("Must run setup_user() first.")
    experiment = dm_api_ds().getExperimentByName(experiment_name)
    logger.info("DM experiment: %s", experiment_name)

    yield from write_if_new(xpcs_header, header)
    yield from bps.mvr(xpcs_index, 1)
    # update the RunEngine metadata (and store on disk)
    RE.md["xpcs_header"] = xpcs_header.get()
    RE.md["xpcs_index"] = xpcs_index.get()

    # 'title' must be safe to use as a file name (no spaces or special chars)
    safe_title = cleanupText(title)
    data_path = pathlib.Path(_xpcsDataDir(safe_title, num_images))
    if data_path.exists():
        raise FileExistsError(
            # fmt: off
            f"Found existing directory '{data_path}'."
            "  Will not overwrite."
            # fmt: on
        )
    # AD will create this directory if not exists.
    file_name_base = _xpcsFileNameBase(safe_title, num_images)
    yield from setup_hdf5_plugin(
        det.hdf1, data_path, file_name_base, num_capture=num_images
    )

    qmap_path = QMAPS[det.name]
    if str(qmap_file).strip() == "":
        qmap_file = str(qmap_path)
    if not pathlib.Path(qmap_file).exists():
        raise FileNotFoundError(f"QMAP file: {qmap_file!r}")
    # upload QMAP to @voyager
    daqInfo_qmap_upload = dm_api_daq().upload(
        experimentName=experiment_name, 
        dataDirectory=DAQ_UPLOAD_PREFIX + str(qmap_path.parent),
        daqInfo={"experimentFilePath": qmap_path.name},
    )
    logger.info("DM DAQ upload id: %r", daqInfo_qmap_upload["id"])

    nxwriter.warn_on_missing_content = nxwriter_warn_missing
    nxwriter.file_path = data_path
    nxwriter.file_name = data_path / (file_name_base + ".hdf")

    # _md is for a bluesky open run
    _md = dict(
        detector_name=detector_name,
        acquire_time=acquire_time,
        acquire_period=acquire_period,
        num_capture=num_images,
        num_exposures=num_exposures,
        num_images=num_images,
        num_triggers=num_triggers,
        qmap_file=qmap_path.name,
        owner=dm_api_proc().username,
        workflow=workflow_name,
        title=title,
        safe_title=safe_title,
        description=description,
        header=xpcs_header.get(),
        metadatafile=str(nxwriter.file_name),
        index=xpcs_index.get(),
        dataDir=str(data_path),
        concise=dm_concise,
        # instrument metadata (expected by nxwriter)
        # TODO: set from actual instrument values
        X_energy=12.0,
        incident_beam_size_nm_xy=1,
        I0=1,
        I1=1,
        incident_energy_spread=1,
    )
    _md = build_run_metadata_dict(
        _md,
        # ALL following kwargs are stored under RE.md["data_management"]
        smooth=wf_smooth,
        gpuID=wf_gpuID,
        beginFrame=wf_beginFrame,
        endFrame=wf_endFrame,
        strideFrame=wf_strideFrame,
        avgFrame=wf_avgFrame,
        type=wf_type,
        dq=wf_dq,
        verbose=wf_verbose,
        saveG2=wf_saveG2,
        overwrite=wf_overwrite,
        analysisMachine=analysisMachine,
    )
    _md.update(md)  # user md takes highest priority

    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    yield from bps.mv(dm_workflow.concise_reporting, dm_concise)

    #
    # *** Run the data acquisition. ***
    #
    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        from .ad_setup_plans import ad_acquire_setup
        from .ad_setup_plans import eiger4M_acquire_setup

        # https://bcda-aps.github.io/apstools/latest/examples/de_1_adsim_hdf5_custom_names.html#HDF5:-AD_EpicsFileNameHDF5Plugin
        yield from ad_acquire_setup(
            det,
            acquire_time=acquire_time,
            acquire_period=acquire_period,
            num_capture=num_images,
            num_exposures=num_exposures,
            num_images=num_images,
            num_triggers=num_triggers,
            path=data_path,
        )

        if det.name == "eiger4M":
            yield from eiger4M_acquire_setup(det)

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
    yield from nxwriter.wait_writer_plan_stub()  # NeXus metadata file
    yield from dm_daq_wait_upload_plan(daqInfo_qmap_upload["id"], DAQ_UPLOAD_WAIT_PERIOD)

    #
    # *** Start the APS Data Management workflow. ***
    #
    logger.info(
        "DM workflow %r, filePath=%r",
        workflow_name,
        pathlib.Path(det.hdf1.full_file_name.get()).name,
    )
    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=dm_wait,
        timeout=dm_waiting_time,
        # all kwargs after this line are DM argsDict content
        # such as pete7.h5 (will also need pete7.hdf)
        # filePath=nxwriter.file_name.name,
        filePath=pathlib.Path(det.hdf1.full_file_name.get()).name,
        experiment=dm_experiment.get(),
        qmap=qmap_path.name,
        # from the plan's API
        smooth=wf_smooth,
        gpuID=wf_gpuID,
        beginFrame=wf_beginFrame,
        endFrame=wf_endFrame,
        strideFrame=wf_strideFrame,
        avgFrame=wf_avgFrame,
        type=wf_type,
        dq=wf_dq,
        verbose=wf_verbose,
        saveG2=wf_saveG2,
        overwrite=wf_overwrite,
        analysisMachine=analysisMachine,
    )

    # upload bluesky run metadata to APS DM
    share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

    logger.info("Finished: bdp_demo_plan()")


def prj_test(detector_name: str = DEFAULT_DETECTOR_NAME, index: int = 0):
    """Developer shortcut plan."""
    yield from setup_user("20240131-jemian", index=index)
    qmap_path = QMAPS.get(detector_name)
    if qmap_path is None:
        raise FileNotFoundError(f"QMAP file {qmap_path} not found.")
    yield from bdp_demo_plan(
        header="A002",
        detector_name=detector_name,
        qmap_file=str(qmap_path),
        dm_wait=False,
        dm_concise=True,
        analysisMachine="adamite",
    )
