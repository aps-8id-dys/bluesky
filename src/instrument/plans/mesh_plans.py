"""
XPCS plans for scanning over a mesh.

.. automodule::
    ~mesh_list_grid_scan
    ~xpcs_mesh

..
    usage: boost_corr [-h] -r RAW_FILENAME -q QMAP_FILENAME [-o OUTPUT_DIR] [-s SMOOTH] [-i GPU_ID] [-begin_frame BEGIN_FRAME] [-end_frame END_FRAME] [-stride_frame STRIDE_FRAME]
                    [-avg_frame AVG_FRAME] [-t TYPE] [-dq TYPE] [--verbose] [--dryrun] [--overwrite] [-c CONFIG.JSON]

    Compute Multi-tau/Twotime correlation for XPCS datasets on GPU/CPU

    optional arguments:
    -h, --help            show this help message and exit
    -r RAW_FILENAME, --raw RAW_FILENAME
                            the filename of the raw data file (imm/rigaku/hdf)
    -q QMAP_FILENAME, --qmap QMAP_FILENAME
                            the filename of the qmap file (h5/hdf)
    -o OUTPUT_DIR, --output OUTPUT_DIR
                            [default: cluster_results] the output directory for the result file. If not exit, the program will create this directory.
    -s SMOOTH, --smooth SMOOTH
                            [default: sqmap] smooth method to be used in Twotime correlation.
    -i GPU_ID, --gpu_id GPU_ID
                            [default: -1] choose which GPU to use. if the input is -1, then CPU is used
    -begin_frame BEGIN_FRAME
                            [default: 1] begin_frame specifies which frame to begin with for the correlation. This is useful to get rid of the bad frames in the beginning.
    -end_frame END_FRAME  [default: -1] end_frame specifies the last frame used for the correlation. This is useful to get rid of the bad frames in the end. If -1 is used, end_frame will be set to
                            the number of frames, i.e. the last frame
    -stride_frame STRIDE_FRAME
                            [default: 1] stride_frame defines the stride.
    -avg_frame AVG_FRAME  [default: 1] stride_frame defines the number of frames to be averaged before the correlation.
    -t TYPE, --type TYPE  [default: "Multitau"] Analysis type: ["Multitau", "Twotime", "Both"].
    -dq TYPE, --dq_selection TYPE
                            [default: "all"] dq_selection: a string that select the dq list, eg. '1, 2, 5-7' selects [1,2,5,6,7]. If 'all', all dynamic qindex will be used.
    --verbose, -v         verbose
    --dryrun, -dr         dryrun: only show the argument without execution.
    --overwrite, -ow      whether to overwrite the existing result file.
    -c CONFIG.JSON, --config CONFIG.JSON
                            configuration file to be used. if the same key is passed as an argument, the value in the configure file will be omitted.      

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
from apstools.utils import dm_daq_wait_upload_plan
from apstools.utils import share_bluesky_metadata_with_dm
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
from dm.common.exceptions.objectNotFound import ObjectNotFound
from toolz import partition

logger = logging.getLogger(__name__)
logger.info(__file__)

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
    "QMAP_file": "/path/to/qmap/file.hdf5",
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

    Collect a total of $n$ points; each motor is on an independent trajectory.

    Here, the motors are specified as motor **names** (to match the queueserver
    interface). With the names, the ophyd registry is searched for the actual
    motor object.

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
        number_of_collection_points,
        snake_axes=snake_axes,
        per_step=per_step,
        md=md,
    )
    return uid


def position_list(start, end, numPts):
    """Return a list of positions from start to end with numPts points."""
    return np.linspace(start, end, numPts).tolist()


def validate_xpcs_mesh_inputs(
    area_det_name,
    data_path,
    qmap_file,
    analysisMachine,
):
    """Raise exception if inputs to xpcs_mesh plan are not valid."""
    if area_det_name != "eiger4m":
        raise RuntimeError(f"{area_det_name=!r}, Must use 'eiger4m' now.")

    if len(xpcs_dm.experiment_name.get()) == 0:
        raise RuntimeError("Must run xpcs_setup_user() first.")

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
    """Wait for image file to be uploaded by DAQ."""
    # TODO: Did the DAQ see that the detector image file write was complete?
    # Check metadata catalog and find the file.
    # HOWTO check the metadata catalog?
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
    # header_index="A001",
    # ---- parameters for analysis code (in DM workflow)
    # see https://github.com/azjk/boost_corr?tab=readme-ov-file#usage
    qmap_file=SUGGESTION["QMAP_file"],
    smooth=SUGGESTION["smooth"],
    analysisMachine=SUGGESTION["analysisMachine"],
    # FIXME:
    # ----
    md: dict = None,
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
    # 'title' must be safe to use as a file name (no spaces or special chars)
    safe_title = cleanupText(title)
    data_path = pathlib.Path(
        xpcs_dm.data_path(
            safe_title,
            number_of_collection_points,
        )
    )

    ############################################################
    # Fail early, fail hard!  Check inputs before configuration.

    validate_xpcs_mesh_inputs(
        area_det_name,
        data_path,
        qmap_file,
        analysisMachine,
    )

    ############################################################
    # Area detector is configured different for each of these.

    if detectors is None:
        detectors = []
    m1_positions = position_list(s1, e1, n1)
    m2_positions = position_list(s2, e2, n2)

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

    ############################################################
    # DM parameters

    dm_experiment_object = dm_api_ds().getExperimentByName(
        xpcs_dm.experiment_name.get()
    )
    workflow_name = "xpcs8-02-gladier-boost"
    logger.info("DM experiment: %s", xpcs_dm.experiment_name.get())

    ############################################################
    # Organize metadata: BS, DM

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
        # md about the DM
        analysisMachine=analysisMachine,
        workflow_name=workflow_name,
        experiment_name=xpcs_dm.experiment_name.get(),
    )
    md_dm = dict(
        qmap_file=qmap_file,
        smooth=smooth,
        # FIXME:
    )

    ############################################################
    # Setup area detector HDF5 plugin (with data_path)

    master_file_base = xpcs_dm.filename_base(
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
    # DM DAQ upload the QMAP file to @voyager

    qmap_path = pathlib.Path(qmap_file)
    daqInfo_qmap_upload = dm_api_daq().upload(
        experimentName=xpcs_dm.experiment_name.get(),
        dataDirectory=DAQ_UPLOAD_PREFIX + str(qmap_path.parent),
        daqInfo={"experimentFilePath": qmap_path.name},
    )
    logger.info("DM DAQ upload id: %r", daqInfo_qmap_upload["id"])

    ############################################################
    # NeXus master file

    hdf5_master_file = master_file_base + MASTER_EXTENSION
    nxwriter.warn_on_missing_content = False
    nxwriter.file_path = data_path
    nxwriter.file_name = data_path / hdf5_master_file

    ############################################################
    # Data Acquisition: run the bluesky plan, wait for the files

    dm_workflow = DM_WorkflowConnector(name="dm_workflow")

    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        # fmt: off
        yield from bps.mv(
            dm_workflow.concise_reporting, False,
            dm_workflow.reporting_period, 10 * SECOND,
            xpcs_dm.header, header,
        )
        yield from xpcs_dm.increment_index()
        RE.md["xpcs_header"] = xpcs_dm.header.get()
        RE.md["xpcs_index"] = xpcs_dm.index.get()
        # fmt: on
        md_xpcs_mesh = {
            "title": title,
            "description": description,
            "datetime": str(datetime.datetime.now()),
            "catalog": cat.name,
        }
        md_xpcs_mesh.update(md_bs)
        md_xpcs_mesh["data_management"] = md_dm
        md_xpcs_mesh.update(md)  # user md takes highest priority

        uid = yield from mesh_list_grid_scan(
            [area_det] + detectors,
            m1,
            m1_positions,
            m2,
            m2_positions,
            number_of_collection_points=number_of_collection_points,
            snake_axes=snake_axes,
            md=md_xpcs_mesh,
        )
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
    # Start DM workflow (optional: and wait for it to finish)

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
        # from the plan's API
        smooth=smooth,
        # FIXME:
        analysisMachine=analysisMachine,
    )

    ############################################################
    # Upload bluesky run metadata to APS DM

    share_bluesky_metadata_with_dm(
        xpcs_dm.experiment_name.get(),
        workflow_name,
        run,
    )

    ############################################################
    # complete

    logger.info("Finished: xpcs_mesh()")
