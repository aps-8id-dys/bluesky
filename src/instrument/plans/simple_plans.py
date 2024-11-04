"""
Simple, modular Bluesky plans for users.
"""

import warnings

import epics as pe
import numpy as np

warnings.filterwarnings("ignore")

from apstools.devices import DM_WorkflowConnector
from apstools.utils import share_bluesky_metadata_with_dm
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp

from ..callbacks.nexus_data_file_writer import nxwriter
from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import sample
from ..devices.softglue import softglue_8idi
from ..initialize_bs_tools import cat
from .select_sample import sort_qnw
from .shutter_logic import blockbeam
from .shutter_logic import post_align
from .shutter_logic import showbeam
from .shutter_logic import shutteroff
from .shutter_logic import shutteron

EMPTY_DICT = {}  # Defined as symbol to pass the style checks.

# These variables most likely won't change so keep them outside functions
CYCLE_NAME = pe.caget("8idi:StrReg26", as_string=True)
WORKFLOW_NAME = pe.caget("8idi:StrReg27", as_string=True)
EXP_NAME = pe.caget("8idi:StrReg25", as_string=True)


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
    md["metadatafile"] = pe.caget("8idi:StrReg30")
    md["xdim"] = 1
    md["ydim"] = 1
    return md


def softglue_start_pulses():
    """Tell the FPGA to start generating pulses."""
    yield from bps.mv(softglue_8idi.start_pulses, "1!")


def softglue_stop_pulses():
    """Tell the FPGA to stop generating pulses."""
    yield from bps.mv(softglue_8idi.stop_pulses, "1!")


def simple_acquire_ext_trig(det, md):
    """Just run the acquisition and save the file, nothing else."""

    nxwriter.warn_on_missing_content = False
    nxwriter.file_path = det.hdf1.file_path.get()
    base_file_name = det.hdf1.file_name.get()
    nxwriter.file_name = f"{nxwriter.file_path}/{base_file_name}.hdf"

    # md = create_run_metadata_dict(det)
    # md["metadatafile"] = str(nxwriter.file_name)
    # md.update(user_md)  # add anything the user supplied

    # subs_decorator wraps acquire with these two calls to the RE
    # subscription_id = RE.subscribe(nxwriter.receiver)
    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        # TODO: Some users want periodic update of acquisition progress.
        # Softglue is a detector here, so it is triggered with the area detector.
        yield from bp.count([det], md=md)

    # RE.unsubscribe(subscription_id)

    # Start the acquire. Eiger will wait for external trigger pulse sequence
    yield from softglue_start_pulses()
    yield from acquire()
    yield from softglue_stop_pulses()

    # Wait for NeXus metadata file content to flush to disk.
    # If next acquisition proceeds without waiting, the
    # metadata file will be spoiled.
    yield from nxwriter.wait_writer_plan_stub()


def simple_acquire_int_series(det, md):
    """Just run the acquisition and save the file, nothing else."""

    nxwriter.warn_on_missing_content = False
    nxwriter.file_path = det.hdf1.file_path.get()
    base_file_name = det.hdf1.file_name.get()
    nxwriter.file_name = f"{nxwriter.file_path}/{base_file_name}.hdf"

    # md = create_run_metadata_dict(det)
    # md["metadatafile"] = str(nxwriter.file_name)
    # md.update(user_md)  # add anything the user supplied

    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        yield from bp.count([det], md=md)

    yield from acquire()
    yield from nxwriter.wait_writer_plan_stub()


def setup_det_ext_trig(det, acq_time, acq_period, num_frames, file_name):
    """Setup the Eiger4M cam module for external trigger (3) mode and populate the hdf plugin"""

    data_full_path = f"/gdata/dm/8IDI/{CYCLE_NAME}/{EXP_NAME}/data/{file_name}/"

    yield from bps.mv(det.cam.trigger_mode, "External Enable")  # 3
    yield from bps.mv(det.cam.acquire_time, acq_time)
    yield from bps.mv(det.cam.acquire_period, acq_period)
    yield from bps.mv(det.hdf1.file_name, file_name)
    yield from bps.mv(det.hdf1.file_path, data_full_path)
    # In External trigger mode, then num_images is not writable.
    # yield from bps.mv(det.cam.num_images, num_frames)
    yield from bps.mv(det.cam.num_triggers, num_frames)
    yield from bps.mv(det.hdf1.num_capture, num_frames)

    pe.caput("8idi:StrReg24", file_name)
    pe.caput("8idi:StrReg30", f"{data_full_path}{file_name}.hdf")


def setup_det_int_series(det, acq_time, acq_period, num_frames, file_name):
    """Setup the Eiger4M cam module for internal acquisition (0) mode and populate the hdf plugin"""
    data_full_path = f"/gdata/dm/8IDI/{CYCLE_NAME}/{EXP_NAME}/data/{file_name}/"

    yield from bps.mv(det.cam.trigger_mode, "Internal Series")  # 0
    yield from bps.mv(det.cam.acquire_time, acq_time)
    yield from bps.mv(det.cam.acquire_period, acq_period)
    yield from bps.mv(det.hdf1.file_name, file_name)
    yield from bps.mv(det.hdf1.file_path, data_full_path)
    yield from bps.mv(det.cam.num_images, num_frames)
    yield from bps.mv(
        det.cam.num_triggers, 1
    )  # Need to put num_trigger to 1 for internal mode
    yield from bps.mv(det.hdf1.num_capture, num_frames)

    pe.caput("8idi:StrReg24", file_name)
    pe.caput("8idi:StrReg30", f"{data_full_path}{file_name}.hdf")


def setup_softglue_ext_trig(acq_time, acq_period, num_frames):
    """Setup external triggering"""
    yield from bps.mv(softglue_8idi.acq_time, acq_time)
    yield from bps.mv(softglue_8idi.acq_period, acq_period)
    # Generate n+1 triggers, in case softglue triggered before area detector.
    # Because we are also sending signal to softglue to stop the pulse train,
    # so add 10 more pulses to be on the safe side.
    yield from bps.mv(softglue_8idi.num_triggers, num_frames + 10)


def kickoff_dm_workflow(
    experiment_name,
    file_name,
    qmap_file,
    run,
    analysisMachine,
):
    """Start a DM workflow for this bluesky run."""
    # oregistry.auto_register = False  # Ignore re-creations of this device.
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    # oregistry.auto_register = True

    forever = 999_999_999_999  # long time, s, disables periodic reports

    yield from bps.mv(dm_workflow.concise_reporting, True)
    yield from bps.mv(dm_workflow.reporting_period, forever)

    # DM argsDict content
    argsDict = dict(
        filePath=str(file_name),
        experimentName=experiment_name,
        qmap=qmap_file,
        smooth="sqmap",
        gpuID=-2,
        beginFrame=3,
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

    workflow_name_run = pe.caget("8idi:StrReg27", as_string=True)

    yield from dm_workflow.run_as_plan(
        workflow=workflow_name_run,
        wait=False,
        timeout=forever,
        **argsDict,
    )

    # Upload bluesky run metadata to APS DM.
    share_bluesky_metadata_with_dm(experiment_name, workflow_name_run, run)

    # Users requested the DM workflow job ID be printed to the console.
    dm_workflow._update_processing_data()
    job_id = dm_workflow.job_id.get()
    job_stage = dm_workflow.stage_id.get()
    job_status = dm_workflow.status.get()
    print(f"DM workflow id: {job_id!r}  status: {job_status}  stage: {job_stage}")


def eiger_acq_ext_trig(
    det=eiger4M,
    acq_time=1,
    acq_period=2,
    num_frame=10,
    num_rep=3,
    att_level=0,
    sample_move=False,
):
    pe.caput("8idPyFilter:FL3:sortedIndex", att_level)

    yield from post_align()
    yield from shutteron()
    yield from showbeam()

    yield from setup_softglue_ext_trig(acq_time, acq_period, num_frame)

    (
        header_name,
        qnw_index,
        sam_pos,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    ) = sort_qnw()
    temp_name = int(temp * 10)

    samx_list = np.linspace(x_cen - x_radius, x_cen + x_radius, num=x_pts)
    samy_list = np.linspace(y_cen - y_radius, y_cen + y_radius, num=y_pts)

    for ii in range(num_rep):
        pos_index = np.mod(sam_pos, x_pts * y_pts)
        pos_index = pos_index + ii + 1

        try:
            if sample_move:
                yield from bps.mv(
                    sample.x,
                    samx_list[np.mod(pos_index, x_pts)],
                    sample.y,
                    samy_list[int(np.floor(pos_index / y_pts))],
                )
                str_index = f"8idi:Reg{int(190+qnw_index)}"
                pe.caput(str_index, pos_index)
            else:
                pass
        except Exception as e:
            print(f"Error occurred in sample motion: {e}")
        finally:
            pass

        filename = f"{header_name}_{sample_name}_a{att_level:04}_t{temp_name:04d}_f{num_frame:06d}_r{ii+1:05d}"

        yield from setup_det_ext_trig(det, acq_time, acq_period, num_frame, filename)

        md = create_run_metadata_dict(det)
        # (uid,) = yield from simple_acquire_ext_trig(det, md)
        yield from simple_acquire_ext_trig(det, md)

        try:
            qmap_file_run = pe.caget("8idi:StrReg23", as_string=True)
            experiment_name_run = pe.caget("8idi:StrReg25", as_string=True)
            analysisMachine_run = pe.caget("8idi:StrReg29", as_string=True)

            yield from kickoff_dm_workflow(
                experiment_name=experiment_name_run,
                file_name=f"{filename}.h5",
                qmap_file=qmap_file_run,
                run=cat[-1],
                analysisMachine=analysisMachine_run,
            )
        except Exception as e:
            print(f"Error occurred in DM Workflow: {e}")
        finally:
            pass


def eiger_acq_int_series(
    det=eiger4M, acq_period=1, num_frame=10, num_rep=3, att_level=0, sample_move=False
):
    acq_time = acq_period
    pe.caput("8idPyFilter:FL3:sortedIndex", att_level)

    yield from post_align()
    yield from shutteroff()

    (
        header_name,
        qnw_index,
        sam_pos,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    ) = sort_qnw()
    temp_name = int(temp * 10)

    samx_list = np.linspace(x_cen - x_radius, x_cen + x_radius, num=x_pts)
    samy_list = np.linspace(y_cen - y_radius, y_cen + y_radius, num=y_pts)

    for ii in range(num_rep):
        pos_index = np.mod(sam_pos, x_pts * y_pts)

        try:
            if sample_move:
                x_pos = samx_list[np.mod(pos_index, x_pts)]
                y_pos = samy_list[int(np.floor(pos_index / y_pts))]
                yield from bps.mv(sample.x, x_pos, sample.y, y_pos)
                str_index = f"8idi:Reg{int(190+qnw_index)}"
                pe.caput(str_index, pos_index)
            else:
                pass
        except Exception as e:
            print(f"Error occurred in sample motion: {e}")
        finally:
            pass

        filename = f"{header_name}_{sample_name}_a{att_level:04}_t{temp_name:04d}_f{num_frame:06d}_r{ii+1:05d}"

        yield from setup_det_int_series(det, acq_time, acq_period, num_frame, filename)

        md = create_run_metadata_dict(det)
        # (uid,) = yield from simple_acquire_ext_trig(det, md)
        yield from showbeam()
        yield from simple_acquire_int_series(det, md)
        yield from blockbeam()

        try:
            qmap_file_run = pe.caget("8idi:StrReg23", as_string=True)
            experiment_name_run = pe.caget("8idi:StrReg25", as_string=True)
            analysisMachine_run = pe.caget("8idi:StrReg29", as_string=True)

            yield from kickoff_dm_workflow(
                experiment_name=experiment_name_run,
                file_name=f"{filename}.h5",
                qmap_file=qmap_file_run,
                run=cat[-1],
                analysisMachine=analysisMachine_run,
            )
        except Exception as e:
            print(f"Error occurred in DM Workflow: {e}")
        finally:
            pass
