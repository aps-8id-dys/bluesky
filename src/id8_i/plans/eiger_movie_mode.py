"""
Simple, modular Bluesky plans for users.
"""

import warnings

from apsbits.core.instrument_init import oregistry
from bluesky import plan_stubs as bps

from .shutter_logic import post_align
from .shutter_logic import shutteroff

warnings.filterwarnings("ignore")

eiger4M = oregistry = oregistry["eiger4M"]
filter_8idi = oregistry["filter_8idi"]


def setup_eiger_tv_mode():
    """Configure the Eiger detector for TV/movie mode.

    This function sets up the Eiger detector for continuous image acquisition
    with internal triggering. It configures the acquisition parameters and
    sets the attenuation level for safe viewing.
    """
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
