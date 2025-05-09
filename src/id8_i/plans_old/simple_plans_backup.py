"""
Simple, modular Bluesky plans for users.
"""

import warnings

import epics as pe
import numpy as np
import h5py 
import datetime

warnings.filterwarnings("ignore")

from apstools.devices import DM_WorkflowConnector
from apstools.utils import share_bluesky_metadata_with_dm
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp
from ..callbacks.nexus_data_file_writer import nxwriter
from ..devices.registers_device import pv_registers
from ..devices.filters_8id import filter_8ide, filter_8idi
from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import sample, rheometer
from ..devices.softglue import softglue_8idi
from ..devices.slit import sl4
from ..devices.qnw_device import qnw_env1, qnw_env2, qnw_env3
# from aps_8id_bs_instrument.devices import *
from ..initialize_bs_tools import cat
from .sample_info_unpack import sort_qnw
from ..plans.shutter_logic import showbeam, blockbeam, shutteron, shutteroff
from .nexus_utils import create_nexus_format_metadata
# from .shutter_logic_8ide import showbeam, blockbeam, shutteron, shutteroff


def create_run_metadata_dict(det=None,
                             sample = sample,
                             ):
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
    md["det_dist"] = 12500
    md["I0"] = 1
    md["I1"] = 1
    md["incident_beam_size_nm_xy"] = 10_000
    md["incident_energy_spread"] = 1
    md["pix_dim_x"] = 75e-3
    md["pix_dim_y"] = 75e-3
    md["t0"] = det.cam.acquire_time.get()
    md["t1"] = det.cam.acquire_period.get()
    # md["acquire_time"] = det.cam.acquire_time.get()
    # md["acquire_period"] = det.cam.acquire_period.get()
    # Will change to Ophyd in the future
    md["nexus_filename"] = pv_registers.metadata_full_path.get()
    md["dataDir"] = pv_registers.file_path.get()
    md["xdim"] = 1
    md["ydim"] = 1
    md["sample_x"] = sample.x.position
    md["sample_y"] = sample.y.position
    md["sample_z"] = sample.z.position
    md["rheometer_x"] = rheometer.x.position
    md["rheometer_y"] = rheometer.y.position
    md["rheometer_z"] = rheometer.z.position
    md["sl4_h_size"] = sl4.h.size.position
    md["sl4_h_center"] = sl4.h.center.position
    md["sl4_v_size"] = sl4.v.size.position
    md["sl4_v_center"] = sl4.v.center.position

    md["qnw1_temp"] = qnw_env1.readback.get()
    md["qnw2_temp"] = qnw_env2.readback.get()
    md["qnw3_temp"] = qnw_env3.readback.get()

    md["att_8ide"] = filter_8ide.attenuation_readback.get()
    md["att_8idi"] = filter_8idi.attenuation_readback.get()
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


def simple_acquire_int_series_nexus(det):
    """Just run the acquisition and save the file, nothing else."""
    file_path = det.hdf1.file_path.get()
    base_file_name = det.hdf1.file_name.get()
    metadata_fname = f"{file_path}/{base_file_name}_metadata.hdf"
    create_nexus_format_metadata(metadata_fname)
    yield from bp.count([det])


def setup_det_int_series(det, acq_time, acq_period, num_frames, file_name):
    """Setup the Eiger4M cam module for internal acquisition (0) mode and populate the hdf plugin"""
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()
    
    file_path = f"/gdata/dm/8IDI/{cycle_name}/{exp_name}/data/{file_name}/"

    yield from bps.mv(det.cam.trigger_mode, "Internal Series")  # 0
    yield from bps.mv(det.cam.acquire_time, acq_time)
    yield from bps.mv(det.cam.acquire_period, acq_period)
    yield from bps.mv(det.hdf1.file_name, file_name)
    yield from bps.mv(det.hdf1.file_path, file_path)
    yield from bps.mv(det.cam.num_images, num_frames)
    yield from bps.mv(
        det.cam.num_triggers, 1
    )  # Need to put num_trigger to 1 for internal mode
    yield from bps.mv(det.hdf1.num_capture, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, file_path)
    yield from bps.mv(pv_registers.metadata_full_path, f"{file_path}{file_name}.hdf")


def setup_det_ext_trig(det, acq_time, acq_period, num_frames, file_name):
    """Setup the Eiger4M cam module for external trigger (3) mode and populate the hdf plugin"""
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()
    
    file_path = f"/gdata/dm/8IDI/{cycle_name}/{exp_name}/data/{file_name}/"

    yield from bps.mv(det.cam.trigger_mode, "External Enable")  # 3
    yield from bps.mv(det.cam.acquire_time, acq_time)
    yield from bps.mv(det.cam.acquire_period, acq_period)
    yield from bps.mv(det.hdf1.file_name, file_name)
    yield from bps.mv(det.hdf1.file_path, file_path)
    # In External trigger mode, then num_images is not writable.
    # yield from bps.mv(det.cam.num_images, num_frames)
    yield from bps.mv(det.cam.num_triggers, num_frames)
    yield from bps.mv(det.hdf1.num_capture, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, file_path)
    yield from bps.mv(pv_registers.metadata_full_path, f"{file_path}{file_name}.hdf")


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
    analysis_type
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
        type=analysis_type,
        dq="all",
        verbose=False,
        saveG2=False,
        overwrite=False,
        analysisMachine=analysisMachine,
    )

    workflow_name_run = pv_registers.workflow_name.get()

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


def eiger_acq_int_series(det=eiger4M, 
                         acq_period=1, 
                         num_frame=10, 
                         num_rep=3, 
                         att_level=0, 
                         sample_move=False,
                         ):
    acq_time = acq_period

    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(5)
    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(5)

    # yield from post_align()
    yield from shutteroff()

    (
        header_name,
        meas_num,
        qnw_index,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    ) = sort_qnw()
    yield from bps.mv(pv_registers.measurement_num, meas_num + 1)
    # yield from bps.mv(pv_registers.sample_name, sample_name)
    sample_name = pv_registers.sample_name.get()

    temp_name = int(temp * 10)

    sample_pos_register = pv_registers.sample_position_register(qnw_index)
    sam_pos = int(sample_pos_register.get())

    samx_list = np.linspace(x_cen - x_radius, x_cen + x_radius, num=x_pts)
    samy_list = np.linspace(y_cen - y_radius, y_cen + y_radius, num=y_pts)

    for ii in range(num_rep):

        pos_index = np.mod(sam_pos+ii, x_pts * y_pts)

        try:
            if sample_move:
                x_pos = samx_list[np.mod(pos_index, x_pts)]
                y_pos = samy_list[int(np.floor(pos_index / y_pts))]
                yield from bps.mv(sample.x, x_pos, sample.y, y_pos)
                yield from bps.mv(sample_pos_register, pos_index)
            else:
                pass
        except Exception as e:
            print(f"Error occurred in sample motion: {e}")
        finally:
            pass

        # filename = f"{header_name}_{sample_name}_a{att_level:04}_t{temp_name:04d}_f{num_frame:06d}_r{ii+1:05d}"
        filename = f"{header_name}_{sample_name}_a{att_level:04}_f{num_frame:06d}_r{ii+1:05d}"

        yield from setup_det_int_series(det, acq_time, acq_period, num_frame, filename)

        md = create_run_metadata_dict(det)
        # (uid,) = yield from simple_acquire_ext_trig(det, md)
        yield from showbeam()
        yield from bps.sleep(0.1)
        yield from simple_acquire_int_series(det, md)
        yield from blockbeam()

        try:
            qmap_file_run = pv_registers.qmap_file.get()
            experiment_name_run = pv_registers.experiment_name.get()
            analysisMachine_run = pv_registers.analysis_machine.get()
            analysis_type_run = pv_registers.analysis_type.get()

            yield from kickoff_dm_workflow(
                experiment_name=experiment_name_run,
                file_name=f"{filename}.h5",
                qmap_file=qmap_file_run,
                run=cat[-1],
                analysisMachine=analysisMachine_run,
                analysis_type=analysis_type_run
            )
        except Exception as e:
            print(f"Error occurred in DM Workflow: {e}")
        finally:
            pass


def eiger_acq_ext_trig(
    det=eiger4M,
    acq_time=1,
    acq_period=2,
    num_frame=10,
    num_rep=3,
    att_level=0,
    sample_move=False,
):

    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(5)
    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(5)

    # yield from post_align()
    yield from shutteron()
    yield from showbeam()

    yield from setup_softglue_ext_trig(acq_time, acq_period, num_frame)

    (
        header_name,
        meas_num,
        qnw_index,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    ) = sort_qnw()
    yield from bps.mv(pv_registers.measurement_num, meas_num + 1)
    # yield from bps.mv(pv_registers.sample_name, sample_name)
    sample_name = pv_registers.sample_name.get()

    temp_name = int(temp * 10)

    sample_pos_register = pv_registers.sample_position_register(qnw_index)
    sam_pos = sample_pos_register.get()

    samx_list = np.linspace(x_cen - x_radius, x_cen + x_radius, num=x_pts)
    samy_list = np.linspace(y_cen - y_radius, y_cen + y_radius, num=y_pts)

    for ii in range(num_rep):
        pos_index = np.mod(sam_pos+ii, x_pts * y_pts)

        try:
            if sample_move:
                yield from bps.mv(
                    sample.x,
                    samx_list[np.mod(pos_index, x_pts)],
                    sample.y,
                    samy_list[int(np.floor(pos_index / y_pts))],
                )
                yield from bps.mv(sample_pos_register, pos_index)
            else:
                pass
        except Exception as e:
            print(f"Error occurred in sample motion: {e}")
        finally:
            pass

        # filename = f"{header_name}_{sample_name}_a{att_level:04}_t{temp_name:04d}_f{num_frame:06d}_r{ii+1:05d}"
        filename = f"{header_name}_{sample_name}_a{att_level:04}_f{num_frame:06d}_r{ii+1:05d}"

        yield from setup_det_ext_trig(det, acq_time, acq_period, num_frame, filename)

        md = create_run_metadata_dict(det)
        # (uid,) = yield from simple_acquire_ext_trig(det, md)
        yield from simple_acquire_ext_trig(det, md)

        try:
            qmap_file_run = pv_registers.qmap_file.get()
            experiment_name_run = pv_registers.experiment_name.get()
            analysisMachine_run = pv_registers.analysis_machine.get()
            analysis_type_run = pv_registers.analysis_type.get()

            yield from kickoff_dm_workflow(
                experiment_name=experiment_name_run,
                file_name=f"{filename}.h5",
                qmap_file=qmap_file_run,
                run=cat[-1],
                analysisMachine=analysisMachine_run,
                analysis_type=analysis_type_run
            )
        except Exception as e:
            print(f"Error occurred in DM Workflow: {e}")
        finally:
            pass


def eiger_acq_flyscan(det=eiger4M, 
                         acq_period=1, 
                         num_frame=10, 
                         num_rep=3, 
                         att_level=0, 
                         sample_move=False,
                         flyspeed=0.1
                         ):
    acq_time = acq_period

    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(5)
    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(5)

    # yield from post_align()
    yield from shutteroff()

    (
        header_name,
        meas_num,
        qnw_index,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    ) = sort_qnw()
    yield from bps.mv(pv_registers.measurement_num, meas_num + 1)
    # yield from bps.mv(pv_registers.sample_name, sample_name)
    sample_name = pv_registers.sample_name.get()

    temp_name = int(temp * 10)

    sample_pos_register = pv_registers.sample_position_register(qnw_index)
    sam_pos = int(sample_pos_register.get())

    samx_list = np.linspace(x_cen - x_radius, x_cen + x_radius, num=x_pts)
    samy_list = np.linspace(y_cen - y_radius, y_cen + y_radius, num=y_pts)

    for ii in range(num_rep):
        pos_index = np.mod(sam_pos, x_pts * y_pts)

        try:
            if sample_move:
                x_pos = samx_list[np.mod(pos_index, x_pts)]
                y_pos = samy_list[int(np.floor(pos_index / y_pts))]
                yield from bps.mv(sample.x, x_pos, sample.y, y_pos)
                yield from bps.mv(sample_pos_register, pos_index)
            else:
                pass
        except Exception as e:
            print(f"Error occurred in sample motion: {e}")
        finally:
            pass

        flyspeed_um = int(flyspeed*1e3)
        filename = f"{header_name}_{sample_name}_fs{flyspeed_um:04d}_a{att_level:04}_t{temp_name:04d}_f{num_frame:06d}_r{ii+1:05d}"

        yield from setup_det_int_series(det, acq_time, acq_period, num_frame, filename)

        md = create_run_metadata_dict(det)
        # (uid,) = yield from simple_acquire_ext_trig(det, md)
        extra_acq_time = 1.0
        total_travel = flyspeed*(acq_period*num_frame+extra_acq_time)
        yield from showbeam()
        yield from bps.sleep(0.1)
        yield from bps.mv(sample.y.velocity, flyspeed)
        yield from bps.mvr(sample.y.user_setpoint, total_travel)
        yield from simple_acquire_int_series(det, md)
        yield from blockbeam()
        yield from bps.sleep(1)
        yield from bps.mv(sample.y.velocity, 5)
        yield from bps.mvr(sample.y, -total_travel)

        try:
            qmap_file_run = pv_registers.qmap_file.get()
            experiment_name_run = pv_registers.experiment_name.get()
            analysisMachine_run = pv_registers.analysis_machine.get()
            analysis_type_run = pv_registers.analysis_type.get()

            yield from kickoff_dm_workflow(
                experiment_name=experiment_name_run,
                file_name=f"{filename}.h5",
                qmap_file=qmap_file_run,
                run=cat[-1],
                analysisMachine=analysisMachine_run,
                analysis_type=analysis_type_run
            )
        except Exception as e:
            print(f"Error occurred in DM Workflow: {e}")
        finally:
            pass
