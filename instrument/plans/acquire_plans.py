"""
Bluesky plans to acquire images.
"""

__all__ = """
    repeated_acquire
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from bluesky import plan_stubs as bps
from bluesky import plans as bp

from ..devices import lambda2M
from . import prepare_count

TEMPLATE = "%s%s_%6.6d.h5"
DEFAULT_FRAME_RATE = 500  # fps  (expect occasional dropped frames at ~1_000 fps)
DEFAULT_ACQUIRE_TIME = 1. / DEFAULT_FRAME_RATE
DEFAULT_ACQUIRE_PERIOD = DEFAULT_ACQUIRE_TIME


def repeated_acquire(
    acq_rep=3,
    file_name="Test",
    acquire_time=DEFAULT_ACQUIRE_TIME,
    acquire_period=DEFAULT_ACQUIRE_PERIOD,
    n_images=10_000,
    file_path="/home/8ididata/2023-1/bluesky202301",
):
    """Repeated Acquisition (using lambda2M)."""
    # fmt: off
    print(f"{file_path=}")
    print(f"{TEMPLATE=}")
    yield from bps.mv(
        lambda2M.hdf1.file_number, 0,
        lambda2M.hdf1.file_template, TEMPLATE,
        lambda2M.hdf1.file_path, file_path,
    )

    print(f"{file_name=}")
    yield from prepare_count(
        lambda2M.hdf1,  # NOTE: ONLY the HDF5 plugin is expected here
        file_name, acquire_time, acquire_period,
        n_images=n_images,
        compression="None",
        auto_save="No",
    )
    # fmt: on

    print(f"Staging setup {lambda2M.stage_sigs=}")
    print(f"Staging setup {lambda2M.cam.stage_sigs=}")
    print(f"Staging setup {lambda2M.hdf1.stage_sigs=}")

    for ii in range(acq_rep):
        print(f"Iteration {ii+1} of {acq_rep}...")
        yield from bp.count([lambda2M])
