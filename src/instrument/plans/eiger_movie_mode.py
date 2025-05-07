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
from .sample_info_unpack import sort_qnw
from .shutter_logic import showbeam, blockbeam, shutteron, shutteroff, post_align
from .nexus_utils import create_nexus_format_metadata
from .move_sample import mesh_grid_move
from .util_8idi import get_machine_name, temp2str
# from .shutter_logic_8ide import showbeam, blockbeam, shutteron, shutteroff
from dm.proc_web_service.api.workflowProcApi import WorkflowProcApi
from dm.common.utility.configurationManager import ConfigurationManager

def setup_eiger_tv_mode():

    yield from bps.mv(eiger4M.cam.trigger_mode, "Internal Series")  # 0
    yield from bps.mv(eiger4M.cam.acquire_time, 1)
    yield from bps.mv(eiger4M.cam.acquire_period, 1)

    yield from bps.mv(eiger4M.cam.num_images, 100)
    yield from bps.mv(eiger4M.cam.num_triggers, 1)  # Need to put num_trigger to 1 for internal mode

    yield from bps.mv(filter_8idi.attenuation_set, 20000)
    yield from bps.sleep(2)
    yield from shutteroff()
    yield from post_align()
