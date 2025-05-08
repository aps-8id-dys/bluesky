"""
Simple, modular Bluesky plans for users.
"""

import warnings

warnings.filterwarnings("ignore")

from bluesky import plan_stubs as bps

# from .shutter_logic_8ide import showbeam, blockbeam, shutteron, shutteroff
from ..devices.ad_eiger_4M import eiger4M
from ..devices.filters_8id import filter_8idi

# from ..callbacks.nexus_data_file_writer import nxwriter
# from aps_8id_bs_instrument.devices import *
from .shutter_logic import post_align
from .shutter_logic import shutteroff


def setup_eiger_tv_mode():
    yield from bps.mv(eiger4M.cam.trigger_mode, "Internal Series")  # 0
    yield from bps.mv(eiger4M.cam.acquire_time, 1)
    yield from bps.mv(eiger4M.cam.acquire_period, 1)

    yield from bps.mv(eiger4M.cam.num_images, 100)
    yield from bps.mv(
        eiger4M.cam.num_triggers, 1
    )  # Need to put num_trigger to 1 for internal mode

    yield from bps.mv(filter_8idi.attenuation_set, 20000)
    yield from bps.sleep(2)
    yield from shutteroff()
    yield from post_align()
