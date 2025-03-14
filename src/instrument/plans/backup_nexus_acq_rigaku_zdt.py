"""
Simple, modular Bluesky plans for users.
"""

import warnings

import epics as pe
import numpy as np
import h5py 
import datetime
import os

warnings.filterwarnings("ignore")

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp
# from ..callbacks.nexus_data_file_writer import nxwriter
from ..devices.registers_device import pv_registers
from ..devices.filters_8id import filter_8ide, filter_8idi
from ..devices.ad_rigaku_3M import rigaku3M
from ..devices.aerotech_stages import sample, rheometer
from ..devices.slit import sl4
from ..devices.qnw_device import qnw_env1, qnw_env2, qnw_env3
# from aps_8id_bs_instrument.devices import *
from ..initialize_bs_tools import cat
from .sample_info_unpack import sort_qnw
from .shutter_logic import showbeam, blockbeam, shutteron, shutteroff, post_align
from .nexus_utils import create_nexus_format_metadata
from .move_sample import mesh_grid_move
from .util_8idi import get_machine_name, temp2str
from dm.proc_web_service.api.workflowProcApi import WorkflowProcApi
from dm.common.utility.configurationManager import ConfigurationManager

def setup_rigaku_ZDT_series(acq_time, acq_period, num_frames, file_name):
    """Setup the rigaku3M cam module for internal acquisition (0) mode and populate the hdf plugin"""
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()
    
    file_path = f"{exp_name}/data/{file_name}"

    yield from bps.mv(rigaku3M.cam.acquire_time, acq_time)
    yield from bps.mv(rigaku3M.cam.acquire_period, acq_period)
    yield from bps.mv(rigaku3M.cam.file_name, f"{file_name}.bin")
    yield from bps.mv(rigaku3M.cam.file_path, file_path)
    yield from bps.mv(rigaku3M.cam.num_images, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, f"/gdata/dm/8IDI/{cycle_name}/{file_path}")
    yield from bps.mv(pv_registers.metadata_full_path, f"/gdata/dm/8IDI/{cycle_name}/{file_path}/{file_name}_metadata.hdf")

    os.makedirs(f"/gdata/dm/8IDI/{cycle_name}/{file_path}", mode=0o770, exist_ok=True)


def rigaku_acq_ZDT_series(acq_period=1, 
                         num_frame=10, 
                         num_rep=3,
                         wait_time=0.0, 
                         sample_move=True,
                         process=True
                         ):
    
    try:

        # Setup DM analysis
        if process:
            configManager = ConfigurationManager.getInstance()  # Object that tracks beamline-specific configuration
            dmuser, password = configManager.parseLoginFile()
            serviceUrl = configManager.getProcWebServiceUrl()
            workflowProcApi = WorkflowProcApi(dmuser, password, serviceUrl) # user/password/url info passed to DM API

        acq_time = acq_period

        # yield from bps.mv(filter_8idi.attenuation_set, att_level)
        # yield from bps.sleep(2)
        # yield from bps.mv(filter_8idi.attenuation_set, att_level)
        # yield from bps.sleep(2)

        yield from post_align()
        yield from shutteroff()

        (header_name, meas_num, qnw_index, temp, temp_zone, sample_name, 
        x_cen, y_cen, x_radius, y_radius, x_pts, y_pts,
        ) = sort_qnw()
        yield from bps.mv(pv_registers.measurement_num, meas_num + 1)
        yield from bps.mv(pv_registers.sample_name, sample_name)
        sample_name = pv_registers.sample_name.get()

        temp_name = temp2str(temp)
        att_level = int(filter_8idi.attenuation_readback.get())

        for ii in range(num_rep):

            yield from bps.sleep(wait_time)

            if sample_move:
                yield from mesh_grid_move(qnw_index, x_cen, x_radius, x_pts, y_cen, y_radius, y_pts)

            filename = f"{header_name}_{sample_name}_a{att_level:04}_f{num_frame:06d}_t{temp_name}C_r{ii+1:05d}"

            yield from setup_rigaku_ZDT_series(acq_time, acq_period, num_frame, filename)

            yield from showbeam()
            yield from bps.sleep(0.1)
            yield from bp.count([rigaku3M])
            yield from blockbeam()

            metadata_fname = pv_registers.metadata_full_path.get()
            create_nexus_format_metadata(metadata_fname, det=rigaku3M)

            # Start DM analysis
            if process:
                exp_name = pv_registers.experiment_name.get()
                qmap_file = pv_registers.qmap_file.get()
                workflow_name = pv_registers.workflow_name.get()
                analysis_machine = get_machine_name()
                argsDict = {"experimentName": exp_name, 
                            "filePath": f"{filename}.bin.000", 
                            "qmap": f"{qmap_file}",
                            "analysisMachine": f"{analysis_machine}",
                            "gpuID": -2,
                            "avgFrame": 1
                            }
                job = workflowProcApi.startProcessingJob(dmuser, f"{workflow_name}", argsDict=argsDict)
                print(f"Job {job['id']} processing {filename}")

    except Exception as e:
        print(f"Error occurred during measurement: {e}")
    finally:
        pass


