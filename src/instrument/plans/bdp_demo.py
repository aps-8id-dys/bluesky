"""
APS BDP demo: 2024-02
"""

__all__ = """
    xpcs_bdp_demo_plan
    xpcs_reset_index
    xpcs_setup_user
""".split()
# __all__ += """
#     prj_test
#     _pick_area_detector
#     _xpcsFileNameBase
#     _xpcsDataDir
# """.split()

import logging
import pathlib

from apstools.devices import DM_WorkflowConnector
from apstools.utils import SECOND
from apstools.utils import build_run_metadata_dict
from apstools.utils import cleanupText
from apstools.utils import dm_api_daq
from apstools.utils import dm_api_ds
from apstools.utils import dm_api_filecat
from apstools.utils import dm_api_proc

# see `def` below: from apstools.utils import dm_daq_wait_upload_plan
try:
    from apstools.utils import dm_isDaqActive
except ImportError:
    from ..utils.aps_data_management import dm_isDaqActive  # TODO hoist to apstools
from apstools.utils import dm_start_daq
from apstools.utils import share_bluesky_metadata_with_dm
from apstools.utils import validate_experiment_dataDirectory
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp
from dm.common.exceptions.objectNotFound import ObjectNotFound
from ophyd import Signal

from ..callbacks.nexus_data_file_writer import nxwriter
from ..devices import adsim4M
from ..devices import eiger4M
from ..devices import lambda2M
from ..initialize_bs_tools import RE
from ..initialize_bs_tools import cat
from ..utils.iconfig_loader import iconfig
from .ad_setup_plans import setup_hdf5_plugin
from .ad_setup_plans import write_if_new

logger = logging.getLogger(__name__)
logger.info(__file__)

dm_experiment = Signal(name="dm_experiment", value="")
xpcs_header = Signal(name="xpcs_header", value=RE.md.get("xpcs_header", "A001"))
xpcs_index = Signal(name="xpcs_index", value=RE.md.get("xpcs_index", 0))

DEFAULT_DETECTOR_NAME = "eiger4M"
DM_WORKFLOW_NAME = iconfig.get("DM_WORKFLOW_NAME", "example-01")
TITLE = "CAC_demo"  # keep this short, single-word
DESCRIPTION = "Demonstrate XPCS data acquisition and analysis."
DEFAULT_RUN_METADATA = {
    "title": TITLE,
    "description": DESCRIPTION,
    "cycle": "2024-3",
}
DEFAULT_REPORTING_PERIOD = (
    10 * SECOND
)  # time between reports about an active DM workflow
# DEFAULT_WAITING_TIME = 10 * MINUTE  # time limit for bluesky reporting
DEFAULT_WAITING_TIME = 999_999_999_999 * SECOND  # unlimited (effectively)
# bluesky will raise TimeoutError if DM workflow is not done by DEFAULT_WAITING_TIME
DAQ_UPLOAD_WAIT_PERIOD = 1.0 * SECOND
DAQ_UPLOAD_PREFIX = "ftp://s8ididm:2811"

QMAP_BASE = pathlib.Path("/home/beams/8IDIUSER/Documents/Miaoqi/standard_qmaps")
QMAPS = {  # only used in test plans
    "adsim4M": QMAP_BASE / "adsim4M_qmap_d36_s360.h5",
    "eiger4M": QMAP_BASE / "eiger4M_qmap_d36_s360.h5",
    "eiger4M_0811_1": QMAP_BASE / "eiger4m_qmap_after_windowadjust.h5",
}


# TODO: hoist to apstools.utils
def dm_daq_wait_upload_plan(id: str, period: float = 10 * SECOND):
    """plan: Wait for DAQ uploads to finish."""
    api = dm_api_daq()
    uploadInfo = api.getUploadInfo(id)
    uploadStatus = uploadInfo.get("status")
    while uploadStatus not in "done failed skipped aborted aborting".split():
        yield from bps.sleep(period)
        uploadInfo = api.getUploadInfo(id)
        uploadStatus = uploadInfo.get("status")
    logger.debug("DM DAQ upload info: %s", uploadInfo)
    if uploadStatus != "done":
        raise ValueError(
            f"DM DAQ upload status: {uploadStatus!r}, {id=!r}."
            f"  Processing error message(s): {uploadInfo['errorMessage']}."
        )


def xpcs_setup_user(dm_experiment_name: str, index: int = -1):
    """
    Configure bluesky session for this user.

    PARAMETERS

    dm_experiment_name *str*:

    .. note:: Set ``index=-1`` to continue with current 'xpcs_index' value.
    """

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
        msg = (
            f"Starting DM DAQ: experiment {dm_experiment_name!r}"
            f" in data directory {data_directory!r}."
        )
        logger.info(msg)
        print(msg)  # Was not showing up in the logs.
        dm_start_daq(dm_experiment_name, data_directory)


def xpcs_reset_index(index: int = 0):
    """
    (Re)set the 'xpcs_index'.  Default=0.

    Data directory and file names are defined by the 'xpcs_header' and
    the`xpcs_index'.  The `xpcs_index' increments at the start of each
    'xpcs_bdp_demo_plan()', the data acquisition plan. The 'xpcs_header' is specified
    as a kwarg, as in this example: 'xpcs_bdp_demo_plan(header="B123")'
    """
    yield from write_if_new(xpcs_index, index)


def _pick_area_detector(detector_name):
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


def xpcs_bdp_demo_plan(
    title: str = TITLE,
    description: str = DESCRIPTION,
    header: str = xpcs_header.get(),
    analysisMachine: str = "amazonite",
    qmap_file: str = "",
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
    dm_concise=False,
    dm_wait=False,
    dm_reporting_period=DEFAULT_REPORTING_PERIOD,
    dm_reporting_time_limit=DEFAULT_WAITING_TIME,
    nxwriter_warn_missing: bool = False,
    # user-supplied metadata ----------------------------------------
    md: dict = DEFAULT_RUN_METADATA,
):
    """
    Acquire XPCS data with the chosen detector and run a DM workflow.
    """

    #
    # *** Prepare. ***
    #
    ANALYSIS_MACHINES = """
        adamite
        amazonite
        califone
        polaris
    """.lower().split()
    analysisMachine = analysisMachine.lower()  # to be safe
    if analysisMachine not in ANALYSIS_MACHINES:
        raise ValueError(
            f"Received {analysisMachine=!r}."
            f"  Must be one of these: {ANALYSIS_MACHINES!r}"
        )
    workflow_name = "xpcs8-02-gladier-boost"

    det = _pick_area_detector(detector_name)
    experiment_name = dm_experiment.get()
    if len(experiment_name) == 0:
        raise RuntimeError("Must run xpcs_setup_user() first.")

    # Make sure the experiment actually exists.
    dm_experiment_object = dm_api_ds().getExperimentByName(experiment_name)
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
            f"Found existing directory '{data_path}'.  Will not overwrite."
            # fmt: on
        )
    # AD will create this directory if not exists.
    file_name_base = _xpcsFileNameBase(safe_title, num_images)
    yield from setup_hdf5_plugin(
        det.hdf1, data_path, file_name_base, num_capture=num_images
    )

    qmap_path = pathlib.Path(qmap_file)
    if not qmap_path.exists():
        raise FileNotFoundError(f"QMAP file: {qmap_file!r}")
    elif not qmap_path.is_file():
        raise FileNotFoundError(f"Not a file: {qmap_file!r}")
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
        metadatafile=nxwriter.file_name.name,
        index=xpcs_index.get(),
        dataDir=str(data_path),
        concise=dm_concise,
        cycle="2024-2",  # TODO get from apstools v1.6.20 ApsMachine...
        # instrument metadata (expected by nxwriter)
        # values from pete7.hdf
        # TODO: set from actual instrument values
        absolute_cross_section_scale=1,
        bcx=1044,
        bcy=1416,
        ccdx=1,
        ccdx0=1,
        ccdy=1,
        ccdy0=1,
        det_dist=12.5,
        I0=1,
        I1=1,
        incident_beam_size_nm_xy=10_000,
        incident_energy_spread=1,
        pix_dim_x=75e-6,
        pix_dim_y=75e-6,
        t0=acquire_time,
        t1=acquire_period,
        X_energy=13.321,
        xdim=1,
        ydim=1,
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
    yield from bps.mv(
        dm_workflow.concise_reporting,
        dm_concise,
        dm_workflow.reporting_period,
        dm_reporting_period,
    )

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
    yield from dm_daq_wait_upload_plan(
        daqInfo_qmap_upload["id"], DAQ_UPLOAD_WAIT_PERIOD
    )
    # TODO: Did the DAQ see that the detector image file write was complete?
    # Check metadata catalog and find the file.
    # HOWTO check the metadata catalog?
    dm_file_cat_api = dm_api_filecat()
    _pre = dm_experiment_object["storageDirectory"]
    _full_file_name = det.hdf1.full_file_name.get()
    _file = _full_file_name.lstrip(_pre).lstrip("/")
    _file_found = False
    print(f"{_full_file_name=!r}")
    print(f"{_pre=!r}")
    print(f"{_file=!r}")
    print(f"{_file_found=!r}")
    for _i in range(120):  # wild guess: after some time, file should be found
        try:
            dm_file_cat_api.getExperimentFile(dm_experiment_object["name"], _file)
            _file_found = True
            break
        except ObjectNotFound:
            if (_i % 10) == 0:
                print(f"Waiting for DM DAQ to find image file: {_file!r}")
            yield from bps.sleep(1)
    if not _file_found:
        raise FileNotFoundError(f"DM DAQ did not file image file {_file!r}")

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
        timeout=dm_reporting_time_limit,
        # all kwargs after this line are DM argsDict content
        filePath=pathlib.Path(det.hdf1.full_file_name.get()).name,
        experimentName=dm_experiment.get(),
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
    job = dm_workflow.getJob()
    msg = (
        f"{job['submissionTimestamp']}"
        f" DM workflow job: id={job['id']!r}"
        f" status={job['status']!r}"
    )
    logger.info(msg)
    print(msg)

    logger.info("Finished: xpcs_bdp_demo_plan()")


def prj_test(
    detector_name: str = DEFAULT_DETECTOR_NAME,
    index: int = 0,
    num_trys: int = 10,
):
    """Developer shortcut plan."""
    yield from xpcs_setup_user("dm-test-bs-MC", index=index)
    qmap_path = QMAPS.get(detector_name)
    if qmap_path is None:
        raise FileNotFoundError(f"QMAP file {qmap_path} not found.")

    for n in range(num_trys):
        logger.info("run #%d of %d", n, num_trys)
        yield from xpcs_bdp_demo_plan(
            header="A001",
            detector_name=detector_name,
            qmap_file=str(qmap_path),
            dm_wait=False,
            dm_concise=True,
            analysisMachine="adamite",
        )


def mc_test(
    detector_name: str = DEFAULT_DETECTOR_NAME,
    index: int = 0,
    num_trys: int = 10,
):
    """Developer shortcut plan."""
    qmap_path = QMAPS.get(detector_name)
    if qmap_path is None:
        raise FileNotFoundError(f"QMAP file {qmap_path} not found.")

    for n in range(num_trys):
        logger.info("run #%d of %d", n, num_trys)
        yield from xpcs_bdp_demo_plan(
            header="G10",
            detector_name=detector_name,
            qmap_file=str(qmap_path),
            dm_wait=False,
            dm_concise=True,
            analysisMachine="adamite",
            wf_gpuID=0,
            acquire_time=0.01,
            acquire_period=0.01,
            num_images=1_000,
        )
