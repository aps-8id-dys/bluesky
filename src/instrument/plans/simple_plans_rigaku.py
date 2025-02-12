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
from ..devices.ad_rigaku_3M import rigaku3M
from ..devices.aerotech_stages import sample, rheometer
from ..devices.slit import sl4
from ..devices.qnw_device import qnw_env1, qnw_env2, qnw_env3
# from aps_8id_bs_instrument.devices import *
from ..initialize_bs_tools import cat
from .select_sample import sort_qnw
from .shutter_logic import showbeam, blockbeam, shutteron, shutteroff
from .nexus_utils import create_nexus_format_metadata
# from .shutter_logic_8ide import showbeam, blockbeam, shutteron, shutteroff



def simple_acquire_ZDT_nexus(det, additional_metadata=None):
    """Just run the acquisition and save the file, nothing else."""
    metadata_fname = pv_registers.metadata_full_path.get()
    create_nexus_format_metadata(metadata_fname, det, additional_metadata)
    yield from bp.count([det])


def simple_acquire_ZDT(det, md):
    """Just run the acquisition and save the file, nothing else."""

    nxwriter.warn_on_missing_content = False
    nxwriter.file_path = det.cam.file_path.get()
    base_file_name = det.cam.file_name.get()
    nxwriter.file_name = f"{nxwriter.file_path}/{base_file_name}.hdf"

    # md = create_run_metadata_dict(det)
    # md["metadatafile"] = str(nxwriter.file_name)
    # md.update(user_md)  # add anything the user supplied

    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        yield from bp.count([det], md=md)

    yield from acquire()
    yield from nxwriter.wait_writer_plan_stub()


def setup_rigaku_ZDT(det, acq_time, acq_period, num_frames, file_name):
    """Setup the Eiger4M cam module for internal acquisition (0) mode and populate the hdf plugin"""
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()
    
    # file_path = f"/gdata/dm/8IDI/{cycle_name}/{exp_name}/data/{file_name}/"

    file_path = f"{cycle_name}/{exp_name}/data/{file_name}/"

    yield from bps.mv(det.cam.acquire_time, acq_time)
    yield from bps.mv(det.cam.acquire_period, acq_period)
    yield from bps.mv(det.cam.file_name, file_name)
    yield from bps.mv(det.cam.file_path, file_path)
    
    yield from bps.mv(det.cam.num_images, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, file_path)
    yield from bps.mv(pv_registers.metadata_full_path, f"{file_path}/{file_name}_metadata.hdf")


def kickoff_dm_workflow(experiment_name, file_name, qmap_file, run,
                        analysisMachine, analysis_type):
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


def rigaku_acq_ZDT(det=rigaku3M, 
                         acq_period=0.000020, 
                         num_frame=100000, 
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

    (header_name, meas_num, qnw_index, temp, sample_name, x_cen, y_cen,
     x_radius, y_radius, x_pts, y_pts,) = sort_qnw()

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

        yield from setup_rigaku_ZDT(det, acq_time, acq_period, num_frame, filename)

        dm_kwargs = {
            "qmap_file":  pv_registers.qmap_file.get(),
            "experiment_name": pv_registers.experiment_name.get(),
            "analysisMachine": pv_registers.analysis_machine.get(),
            "analysis_type": pv_registers.analysis_type.get(),
        }

        # dm_kwargs_string = {
        #     "/entry/instrument/datamanagement/workflow_kwargs": json.dumps(dm_kwargs) }
        # md = create_run_metadata_dict(det)

        yield from showbeam()
        yield from bps.sleep(0.1)
        # yield from simple_acquire_ZDT(det, md)
        # yield from simple_acquire_ZDT_nexus(det, dm_kwargs_string)
        yield from simple_acquire_ZDT_nexus(det)
        yield from blockbeam()

        try:
            yield from kickoff_dm_workflow(
                file_name=f"{filename}.h5", run=cat[-1], **dm_kwargs
            )
        except Exception as e:
            print(f"Error occurred in DM Workflow: {e}")
        finally:
            pass
