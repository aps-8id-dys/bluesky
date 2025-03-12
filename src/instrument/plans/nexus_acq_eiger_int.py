"""
Simple, modular Bluesky plans for users.
"""

import warnings

import epics as pe
import numpy as np
import h5py 
import datetime

warnings.filterwarnings("ignore")

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp
# from ..callbacks.nexus_data_file_writer import nxwriter
from ..devices.registers_device import pv_registers
from ..devices.filters_8id import filter_8ide, filter_8idi
from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import sample, rheometer
from ..devices.slit import sl4
from ..devices.qnw_device import qnw_env1, qnw_env2, qnw_env3
# from aps_8id_bs_instrument.devices import *
from ..initialize_bs_tools import cat
from .select_sample import sort_qnw
from .shutter_logic import showbeam, blockbeam, shutteron, shutteroff, post_align
from .nexus_utils import create_nexus_format_metadata
from .move_sample import mesh_grid_move
from .util_8idi import get_machine_name, temp2str
# from .shutter_logic_8ide import showbeam, blockbeam, shutteron, shutteroff
from dm.proc_web_service.api.workflowProcApi import WorkflowProcApi
from dm.common.utility.configurationManager import ConfigurationManager

def setup_eiger_int_series(acq_time, acq_period, num_frames, file_name):
    """Setup the Eiger4M cam module for internal acquisition (0) mode and populate the hdf plugin"""
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()
    
    file_path = f"/gdata/dm/8IDI/{cycle_name}/{exp_name}/data/{file_name}"

    yield from bps.mv(eiger4M.cam.trigger_mode, "Internal Series")  # 0
    yield from bps.mv(eiger4M.cam.acquire_time, acq_time)
    yield from bps.mv(eiger4M.cam.acquire_period, acq_period)
    yield from bps.mv(eiger4M.hdf1.file_name, file_name)
    yield from bps.mv(eiger4M.hdf1.file_path, file_path)
    yield from bps.mv(eiger4M.cam.num_images, num_frames)
    yield from bps.mv(eiger4M.cam.num_triggers, 1)  # Need to put num_trigger to 1 for internal mode
    yield from bps.mv(eiger4M.hdf1.num_capture, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, file_path)
    yield from bps.mv(pv_registers.metadata_full_path, f"{file_path}/{file_name}_metadata.hdf")

def eiger_acq_int_series(acq_period=1, 
                         num_frame=10, 
                         num_rep=3, 
                         att_level=0, 
                         sample_move=True,
                         process=True
                         ):
    
    # Setup DM analysis
    if process:
        configManager = ConfigurationManager.getInstance()  # Object that tracks beamline-specific configuration
        dmuser, password = configManager.parseLoginFile()
        serviceUrl = configManager.getProcWebServiceUrl()
        workflowProcApi = WorkflowProcApi(dmuser, password, serviceUrl) # user/password/url info passed to DM API
    
    acq_time = acq_period

    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(2)
    yield from bps.mv(filter_8idi.attenuation_set, att_level)
    yield from bps.sleep(2)
    yield from post_align()
    yield from shutteroff()

    (header_name, meas_num, qnw_index, temp, sample_name, 
     x_cen, y_cen, x_radius, y_radius, x_pts, y_pts,
    ) = sort_qnw()
    yield from bps.mv(pv_registers.measurement_num, meas_num + 1)
    yield from bps.mv(pv_registers.sample_name, sample_name)
    sample_name = pv_registers.sample_name.get()

    temp_name = temp2str(temp)

    for ii in range(num_rep):

        if sample_move:
            yield from mesh_grid_move(qnw_index, x_cen, x_radius, x_pts, y_cen, y_radius, y_pts)

        # filename = f"{header_name}_{sample_name}_a{att_level:04}_f{num_frame:06d}_t{temp_name}C_r{ii+1:05d}"
        filename = f"{header_name}_{sample_name}_a{att_level:04}_f{num_frame:06d}_r{ii+1:05d}"

        yield from setup_eiger_int_series(acq_time, acq_period, num_frame, filename)

        metadata_fname = pv_registers.metadata_full_path.get()
        create_nexus_format_metadata(metadata_fname, det=eiger4M)

        yield from showbeam()
        yield from bps.sleep(0.1)
        yield from bp.count([eiger4M])
        yield from blockbeam()

        # Start DM analysis
        if process:
            exp_name = pv_registers.experiment_name.get()
            qmap_file = pv_registers.qmap_file.get()
            workflow_name = pv_registers.workflow_name.get()
            # analysis_machine = pv_registers.analysis_machine.get()
            analysis_machine = get_machine_name()
            argsDict = {"experimentName": exp_name, 
                        "filePath": f"{filename}.h5", 
                        "qmap": f"{qmap_file}",
                        "analysisMachine": f"{analysis_machine}",
                        "gpuID": -2
                        }
            job = workflowProcApi.startProcessingJob(dmuser, f"{workflow_name}", argsDict=argsDict)
            print(f"Job {job['id']} processing {filename}")
