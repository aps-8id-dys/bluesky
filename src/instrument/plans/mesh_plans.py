"""
XPCS plans for scanning over a mesh.

.. automodule::
    ~mesh_list_grid_scan
    ~xpcs_mesh
    ~xpcs_mesh_with_dm
"""

import datetime
import logging
import pathlib

import apstools.plans
import numpy as np
from apstools.devices import DM_WorkflowConnector
from apstools.utils import MINUTE
from apstools.utils import SECOND
from apstools.utils import cleanupText
from apstools.utils import dm_api_daq
from apstools.utils import dm_api_ds
from apstools.utils import dm_api_filecat
from apstools.utils import share_bluesky_metadata_with_dm
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
from dm.common.exceptions.objectNotFound import ObjectNotFound
from toolz import partition

logger = logging.getLogger(__name__)
logger.info(__file__)

try:
    from apstools.utils import dm_daq_wait_upload_plan
except ImportError:
    from ..utils.aps_data_management import dm_daq_wait_upload_plan
from ..callbacks.nexus_data_file_writer import nxwriter  # noqa: E402
from ..devices.xpcs_support import xpcs_dm  # noqa: E402
from ..initialize_bs_tools import RE  # noqa: E402
from ..initialize_bs_tools import cat  # noqa: E402
from ..initialize_bs_tools import oregistry  # noqa: E402
from .ad_setup_plans import setup_hdf5_plugin  # noqa: E402

ANALYSIS_MACHINES = """
    adamite
    amazonite
    califone
    polaris
""".lower().split()
DAQ_UPLOAD_PREFIX = "ftp://s8ididm:2811"
DAQ_UPLOAD_WAIT_PERIOD = 1.0 * SECOND
MASTER_EXTENSION = ".hdf"
SUGGESTION = {
    "analysisMachine": "amazonite",
    "area_det_name": "eiger4M",
    "description": "Demonstrate XPCS mesh and DM workflow.",
    "QMAP_file": "",
    "smooth": "sqmap",
    "title": "RENAME_XPCS_MESH",  # keep this short, single-word
}


def mesh_list_grid_scan(
    detectors,
    *args,
    number_of_collection_points,
    snake_axes=False,
    per_step=None,
    md=None,
):
    """
    Scan over a multi-dimensional mesh.

    Collect a total of 'n' points; each motor has its own set of positions.

    Motors are specified by their **names** (matching the queueserver
    interface). The ophyd registry is searched by name for the motor object.

    Calls: ``apstools.plans.xpcs_mesh.mesh_list_grid_scan()``.  See that plan
    for a detailed description of its arguments.
    """
    # Translate the motor names into motor objects.
    axes_parameters = []
    for motor_name, pos_list in partition(2, args):
        if isinstance(motor_name, str):
            motor_object = oregistry.find(motor_name)
        else:
            # Assume caller provided actual motor object.
            motor_object = motor_name
        axes_parameters += [motor_object, pos_list]

    # Use same-named plan from apstools.
    uid = yield from apstools.plans.mesh_list_grid_scan(
        detectors,
        *axes_parameters,
        number_of_collection_points=number_of_collection_points,
        snake_axes=snake_axes,
        per_step=per_step,
        md=md,
    )
    return uid


def validate_xpcs_mesh_inputs(
    area_det_name,
    data_path,
    qmap_file,
    analysisMachine,
):
    """Raise exception if inputs to xpcs_mesh plan are not valid."""
    if area_det_name != "eiger4M":
        raise RuntimeError(f"{area_det_name=!r}, Must use 'eiger4M' now.")

    if len(xpcs_dm.experiment_name.get()) == 0:
        raise RuntimeError("Must run xpcs_setup_user2() first.")

    if data_path.exists():
        msg = f"Data path '{data_path}' exists.  Will not overwrite."
        raise FileExistsError(msg)

    if not pathlib.Path(qmap_file).exists():
        raise FileNotFoundError(f"QMAP file: {qmap_file!r}")

    if analysisMachine not in ANALYSIS_MACHINES:
        raise ValueError(
            f"Received {analysisMachine=!r}."
            f"  Must be one of these: {ANALYSIS_MACHINES!r}"
        )


def wait_daq_image_file_upload(
    dm_experiment,
    full_file_name,
    period=60 * SECOND,
):
    """
    Wait for image file to be uploaded by DAQ.

    Check metadata catalog and find the file.
    """
    # TODO: Hoist to apstools?
    dm_file_cat_api = dm_api_filecat()
    _pre = dm_experiment["storageDirectory"]
    _file = full_file_name.lstrip(_pre).lstrip("/")
    _file_found = False
    print(f"{full_file_name=!r}")
    print(f"{_pre=!r}")
    print(f"{_file=!r}")
    print(f"{_file_found=!r}")
    for _i in range(int(period)):  # wild guess: file should be found <60s
        try:
            dm_file_cat_api.getExperimentFile(dm_experiment["name"], _file)
            _file_found = True
            break
        except ObjectNotFound:
            if (_i % 10) == 0:
                print(f"Waiting for DM DAQ to find image file: {_file!r}")
            yield from bps.sleep(1)
    if not _file_found:
        raise FileNotFoundError(f"DM DAQ did not file image file {_file!r}")


def xpcs_mesh(
    area_det_name="eiger4M",
    detectors=None,
    m1="sample.x",
    s1=0,
    e1=1,
    n1=3,
    m2="sample.y",
    s2=0,
    e2=2,
    n2=5,
    number_of_collection_points=20,
    snake_axes=False,
    acquire_time=0.001,
    acquire_period=0.001,
    nframes=1_000,
    # header_index="A001",
    md=None,
):
    """
    Measure XPCS in repeated passes through a 2-D mesh as a single bluesky run.

    Only used for data collection after alignment is complete.

    Mesh is defined by two positioner axes m1 & m2. Each axis has parameters for
    start, end, and number of points (s, e, n). These define a mesh of size (n1 x
    n2).  The mesh is converted to a list of m1 & m2 positions to be measured in
    sequence.

    The actual number of data collections, number_of_collection_points, is not
    required to be equal to the number of mesh points.  The list of mesh
    coordinates wll be repeated as necessary to collect the required number of
    collection points.

    The sequence of mesh points will consider 'snake_axes', which reverses the
    sequence of 'm2' points on each increment of 'm1'.

    At each collection, the area detector will acquire 'nframes' with
    acquisition parameters 'acquire_time' & 'acquire_period'.
    """
    # Only used for XPCS data collection
    # Area detector is configured different for each of these.

    if detectors is None:
        detectors = []
    m1_positions = np.linspace(s1, e1, n1).tolist()
    m2_positions = np.linspace(s2, e2, n2).tolist()

    area_det = oregistry.find(area_det_name)
    if area_det in detectors:
        # fmt: off
        yield from bps.mv(
            area_det.cam.acquire_time, acquire_time,
            area_det.cam.acquire_period, acquire_period,
            area_det.cam.num_images, nframes,
        )
        # fmt: on
        # TODO: add user control of detector trigger_mode
        # Includes configuration of soft glue as needed.
        # Probably will need more user keywords for this.

    yield from mesh_list_grid_scan(
        [area_det] + detectors,
        oregistry.find(name=m1),
        m1_positions,
        oregistry.find(name=m2),
        m2_positions,
        number_of_collection_points=number_of_collection_points,
        snake_axes=snake_axes,
        md=None,
    )


def xpcs_mesh_with_dm(
    title=SUGGESTION["title"],  # used as part of file name
    description=SUGGESTION["description"],
    header: str = xpcs_dm.header.get(),
    # ---- parameters for data acquisition
    area_det_name=SUGGESTION["area_det_name"],
    detectors=None,
    m1="sample.x",
    s1=0,
    e1=1,
    n1=3,
    m2="sample.y",
    s2=0,
    e2=2,
    n2=5,
    number_of_collection_points=20,
    snake_axes=False,
    acquire_time=0.001,
    acquire_period=0.001,
    nframes=1_000,
    # ---- instrument settings
    X_energy=12.0,
    # ---- parameters for analysis code (in DM workflow)
    analysisMachine=SUGGESTION["analysisMachine"],
    qmap_file=SUGGESTION["QMAP_file"],
    wf_smooth=SUGGESTION["smooth"],
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
    # ----
    md: dict = None,
):
    """
    Plan: acquire with xpcs_mesh() then execute DM workflow.
    """
    ############################################################
    #! 'title' must be safe to use as a file name (no spaces or special chars)
    safe_title = cleanupText(title)
    data_path = pathlib.Path(
        xpcs_dm.data_path(
            safe_title,
            number_of_collection_points,
        )
    )
    yield from bps.mv(xpcs_dm.header, header)
    ############################################################
    #! Check inputs before configuration. Fail early, fail hard!

    validate_xpcs_mesh_inputs(
        area_det_name,
        data_path,
        qmap_file,
        analysisMachine,
    )

    ############################################################
    #! Area detector.

    if detectors is None:
        detectors = []

    area_det = oregistry.find(area_det_name)

    ############################################################
    #! DM parameters

    dm_experiment_object = dm_api_ds().getExperimentByName(
        xpcs_dm.experiment_name.get()
    )
    workflow_name = "xpcs8-02-gladier-boost"
    logger.info("DM experiment: %s", xpcs_dm.experiment_name.get())

    ############################################################
    #! Organize metadata: BS, DM

    md_bs = dict(  # bluesky plan metadata dict
        area_det_name=area_det_name,
        detectors=detectors,
        m1=m1,
        s1=s1,
        e1=e1,
        n1=n1,
        m2=m2,
        s2=s2,
        e2=e2,
        n2=n2,
        number_of_collection_points=number_of_collection_points,
        snake_axes=snake_axes,
        acquire_time=acquire_time,
        acquire_period=acquire_period,
        nframes=nframes,
        X_energy=X_energy,
        # md about the DM but not in md_dm
        workflow_name=workflow_name,
        experiment_name=xpcs_dm.experiment_name.get(),
    )
    md_dm = dict(  # will be passed verbatim to DM workflow, as **md_dm
        analysisMachine=analysisMachine,
        avgFrame=wf_avgFrame,
        beginFrame=wf_beginFrame,
        dq=wf_dq,
        endFrame=wf_endFrame,
        gpuID=wf_gpuID,
        overwrite=wf_overwrite,
        qmap_file=qmap_file,
        saveG2=wf_saveG2,
        smooth=wf_smooth,
        strideFrame=wf_strideFrame,
        type=wf_type,
        verbose=wf_verbose,
    )

    ############################################################
    #! Setup area detector HDF5 plugin (with data_path)

    master_file_base = xpcs_dm.filename_base(
        # no path, no extension
        safe_title,
        number_of_collection_points,
    )
    yield from setup_hdf5_plugin(
        area_det.hdf1,
        data_path,
        master_file_base,
        num_capture=number_of_collection_points,
    )

    ############################################################
    #! DM DAQ upload will copy the QMAP file to voyager.
    #
    # Upload is used for any files not written directly to voyager.

    qmap_path = pathlib.Path(qmap_file)
    # TODO: check dm_isDaqActive here?
    daqInfo_qmap_upload = dm_api_daq().upload(
        experimentName=xpcs_dm.experiment_name.get(),
        dataDirectory=DAQ_UPLOAD_PREFIX + str(qmap_path.parent),
        daqInfo={"experimentFilePath": qmap_path.name},
    )
    logger.info("DM DAQ upload id: %r", daqInfo_qmap_upload["id"])

    ############################################################
    #! NeXus master file

    hdf5_master_file = master_file_base + MASTER_EXTENSION
    nxwriter.warn_on_missing_content = False
    nxwriter.file_path = data_path
    nxwriter.file_name = data_path / hdf5_master_file

    ############################################################
    #! Data Acquisition: run the bluesky plan, wait for the files

    dm_workflow = DM_WorkflowConnector(name="dm_workflow")

    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        from .ad_setup_plans import ad_acquire_setup
        from .ad_setup_plans import eiger4M_acquire_setup

        # fmt: off
        yield from bps.mv(
            dm_workflow.concise_reporting, False,
            dm_workflow.reporting_period, 10 * SECOND,
        )
        yield from xpcs_dm.increment_index()
        RE.md["xpcs_header"] = xpcs_dm.header.get()
        RE.md["xpcs_index"] = xpcs_dm.index.get()
        # fmt: on
        md_xpcs_mesh = {
            "title": title,
            "description": description,
            "datetime": str(datetime.datetime.now()),
        }
        md_xpcs_mesh.update(md_bs)
        md_xpcs_mesh["data_management"] = md_dm
        md_xpcs_mesh.update(md or {})  # user md takes highest priority

        # https://bcda-aps.github.io/apstools/latest/examples/de_1_adsim_hdf5_custom_names.html#HDF5:-AD_EpicsFileNameHDF5Plugin
        yield from ad_acquire_setup(
            area_det,
            acquire_time=acquire_time,
            acquire_period=acquire_period,
            num_capture=nframes,
            num_exposures=1,
            num_images=nframes,
            num_triggers=1,
            path=data_path,
        )

        if area_det.name == "eiger4M":
            yield from eiger4M_acquire_setup(area_det)

        # fmt: off
        uid = yield from xpcs_mesh(
            area_det_name, detectors,
            m1, s1, e1, n1,
            m2, s2, e2, n2,
            number_of_collection_points=number_of_collection_points,
            snake_axes=snake_axes,
            md=md_xpcs_mesh,
        )
        # fmt: on
        return uid

    uid = yield from acquire()
    run = cat[uid]

    yield from nxwriter.wait_writer_plan_stub()  # hdf5_master_file
    ad_file = area_det.hdf1.full_file_name.get()
    yield from dm_daq_wait_upload_plan(
        daqInfo_qmap_upload["id"], DAQ_UPLOAD_WAIT_PERIOD
    )
    yield from wait_daq_image_file_upload(dm_experiment_object, ad_file)

    ############################################################
    #! Start DM workflow (optional: and wait for it to finish)

    logger.info(
        "DM workflow %r, filePath=%r",
        workflow_name,
        pathlib.Path(ad_file).name,
    )
    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=False,
        timeout=10 * MINUTE,
        # all kwargs after this line are DM argsDict content
        filePath=pathlib.Path(ad_file).name,
        experimentName=xpcs_dm.experiment_name.get(),
        qmap=qmap_path.name,
        **md_dm,  # all other kwargs
    )

    ############################################################
    #! Upload bluesky run metadata to APS DM

    share_bluesky_metadata_with_dm(
        xpcs_dm.experiment_name.get(),
        workflow_name,
        run,
    )

    ############################################################
    #! complete

    logger.info("Finished: xpcs_mesh()")
