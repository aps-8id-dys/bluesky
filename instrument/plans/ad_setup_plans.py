"""
Bluesky plans to setup various Area Detectors for acquisition.
"""

__all__ = """
    eiger4M_daq_setup
""".split()

import logging
from bluesky import plan_stubs as bps
from ..devices import eiger4M

logger = logging.getLogger(__name__)
logger.info(__file__)

class DetectorStateError(RuntimeError):
    """For custom errors in this module."""

def eiger4M_daq_setup(
    acquire_time : float,
    acquire_period : float,
    num_capture : int = 1,
    num_exposures : int = 1,
    num_images : int = 10_000,
    num_triggers : int = 1,
):
    det = eiger4M
    cam = det.cam

    # Check the configuration of the detector now.
    attrs = {
        "data_source": (2, "Stream"),
        "fw_enable": (0, "Disable"),
        "fw_state": ["disabled"],
        "initialize": (0, "Done"),
        "stream_decompress": (0, "Disable"),
        "stream_enable": (1, "Enable"),
        "stream_state": ["ready"],
        "trigger_mode": (0, "Internal Series"),  # values specific to Eiger4M
    }

    # Raise DetectorStateError on the first fail.
    for k, v in attrs.items():
        if getattr(cam, k).get() not in v:
            raise DetectorStateError(
                f"{det.name} PV {getattr(cam, k).pvname!r} not in {v!r}"
            )

    # Make the settings.
    yield from bps.mv(
        cam.acquire_time, acquire_time,
        cam.acquire_period, acquire_period,
        cam.num_capture, num_capture,
        cam.num_exposures, num_exposures,
        cam.num_images, num_images,
        cam.num_triggers, num_triggers,
    )
