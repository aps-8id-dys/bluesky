"""
Data acquisition steps as independent bluesky plans.

.. autosummary::
    ~kickoff_dm_workflow
    ~pre_align
    ~setup_det_ext_trig
    ~setup_softglue_ext_trig
    ~simple_acquire

This plan is an example that combines the above plans.

.. autosummary::
    ~example_full_acquisition

Example::

    RE(pre_align())  # Permit detector to open the shutter.
    det = eiger4M
    RE(setup_det_ext_trig(det, 0.1, 1, 10, "A001_001"))
    RE(setup_softglue_ext_trig(0.1, 1, 10))
    (uid,) = RE(simple_acquire(det))
    RE(
        kickoff_dm_workflow(
            "comm202410",
            "A001_001.h5",
            "eiger4m_qmap_1024_s360_d36_linear.h5",
            cat[uid],
            analysisMachine="amazonite"
        )
    )
"""

import pathlib

# import epics as pe

from apstools.devices import DM_WorkflowConnector
from apstools.utils import share_bluesky_metadata_with_dm
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp

from aps_8id_bs_instrument.callbacks.nexus_data_file_writer import nxwriter
from aps_8id_bs_instrument.initialize_bs_tools import cat
from aps_8id_bs_instrument.initialize_bs_tools import oregistry
from aps_8id_bs_instrument.devices.ad_eiger_4M import eiger4M
from aps_8id_bs_instrument.devices.labjack_support import labjack
from aps_8id_bs_instrument.devices.softglue import softglue_8idi


EMPTY_DICT = {}  # Defined as symbol to pass the style checks.
DATA_FOLDER = "/gdata/dm/8IDI/2024-3/comm202410/data/"


def pre_align():
    yield from bps.mv(labjack.logic, 0)
    yield from bps.mv(labjack.operation, 0)


def create_run_metadata_dict(det):
    md = {}
    md["X_energy"] = 10.0  # keV, TODO get from undulator or monochromator
    # TODO
    md["absolute_cross_section_scale"] = 1
    md["bcx"] = 1044
    md["bcy"] = 1416
    md["ccdx"] = 1
    md["ccdx0"] = 1
    md["ccdy"] = 1
    md["ccdy0"] = 1
    md["det_dist"] = 12.5
    md["I0"] = 1
    md["I1"] = 1
    md["incident_beam_size_nm_xy"] = 10_000
    md["incident_energy_spread"] = 1
    md["pix_dim_x"] = 75e-6
    md["pix_dim_y"] = 75e-6
    md["t0"] = det.cam.acquire_time.get()
    md["t1"] = det.cam.acquire_period.get()
    md["xdim"] = 1
    md["ydim"] = 1
    return md


def simple_acquire(det, user_md: dict = EMPTY_DICT):
    """Just run the acquisition and save the file, nothing else."""

    nxwriter.warn_on_missing_content = False
    nxwriter.file_path = det.hdf1.file_path.get()
    base_file_name = det.hdf1.file_name.get()
    nxwriter.file_name = f"{nxwriter.file_path}/{base_file_name}.hdf"

    md = create_run_metadata_dict(det)
    md["metadatafile"] = str(nxwriter.file_name)
    md.update(user_md)  # add anything the user supplied

    # subs_decorator wraps acquire with these two calls to the RE
    # subscription_id = RE.subscribe(nxwriter.receiver)
    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        # TODO: Some users want periodic update of acquisition progress.
        yield from bp.count([det, softglue_8idi], md=md)

    # RE.unsubscribe(subscription_id)

    # Start the acquire. Eiger will wait for external trigger pulse sequence
    yield from acquire()

    # Send the external trigger pulse sequence from softglue.
    # Acquisition starts with this step.
    # FIXME: never gets called until acquire finishes.
    # yield from bps.mv(softglue_8idi.sg_trigger, "1!")

    # Wait for NeXus metadata file content to flush to disk.
    # If next acquisition proceeds without waiting, the
    # metadata file will be spoiled.
    yield from nxwriter.wait_writer_plan_stub()


def setup_det_ext_trig(det, acq_time, acq_period, num_frames, file_name):
    """Setup the cam module for external trigger (3) mode and populate the hdf plugin"""
    yield from bps.mv(det.cam.trigger_mode, 3)  # External External Series

    yield from bps.mv(det.cam.acquire_time, acq_time)
    yield from bps.mv(det.cam.acquire_period, acq_period)
    yield from bps.mv(det.hdf1.file_name, file_name)
    yield from bps.mv(det.hdf1.file_path, DATA_FOLDER + file_name + "/")
    # In External trigger mode, then num_images is not writable.
    # yield from bps.mv(det.cam.num_images, num_frames)
    yield from bps.mv(det.cam.num_triggers, num_frames)


def setup_softglue_ext_trig(acq_time, acq_period, num_frames):
    """Setup external triggering"""
    yield from bps.mv(softglue_8idi.acq_time, acq_time)
    yield from bps.mv(softglue_8idi.acq_period, acq_period)
    # Generate n+1 triggers, in case softglue triggered before area detector.
    yield from bps.mv(softglue_8idi.num_triggers, num_frames + 1)


def kickoff_dm_workflow(
    experiment_name,
    file_name,
    qmap_file,
    run,
    analysisMachine="amazonite",
):
    """Start a DM workflow for this bluesky run."""
    oregistry.auto_register = False  # Ignore re-creations of this device.
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    oregistry.auto_register = True

    forever = 999_999_999_999  # long time, s, disables periodic reports
    workflow_name = "xpcs8-02-gladier-boost"

    yield from bps.mv(dm_workflow.concise_reporting, True)
    yield from bps.mv(dm_workflow.reporting_period, forever)

    # DM argsDict content
    argsDict = dict(
        filePath=str(file_name),
        experimentName=experiment_name,
        qmap=qmap_file,
        smooth="sqmap",
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
        analysisMachine=analysisMachine,
    )

    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=False,
        timeout=forever,
        **argsDict,
    )

    # Upload bluesky run metadata to APS DM.
    share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

    # Users requested the DM workflow job ID be printed to the console.
    dm_workflow._update_processing_data()
    job_id = dm_workflow.job_id.get()
    job_stage = dm_workflow.stage_id.get()
    job_status = dm_workflow.status.get()
    print(f"DM workflow id: {job_id!r}  status: {job_status}  stage: {job_stage}")


def example_full_acquisition():
    """These are the data acquisition steps for a user."""
    det = eiger4M
    yield from setup_det_ext_trig(det, 0.1, 0.1, 1000, "A001_001")

    uids = yield from simple_acquire(det)
    print(f"Bluesky run: {uids=}")
    run = cat[uids[0]]

    try:
        yield from nxwriter.wait_writer_plan_stub()
        image_file_name = pathlib.Path(det.hdf1.full_file_name.get()).name
        print(f"{image_file_name=!r}")

        yield from kickoff_dm_workflow(
            "my_dm_experiment",
            image_file_name,
            "my_qmap_file.h5",
            run,
            analysisMachine="amazonite",
        )
    except Exception as exc:
        print(f"Exception: {exc}")
