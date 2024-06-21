"""
Bluesky plans to acquire images.
"""

__all__ = """
    bdp_acquire
""".split()


import logging

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from ophyd.ophydobj import Kind

from .. import iconfig
from ..devices import lambda2M
from ..initialize import bec

logger = logging.getLogger(__name__)
logger.info(__file__)

HDF5_FILE_TEMPLATE = iconfig["AREA_DETECTOR"].get("HDF5_FILE_TEMPLATE", "%s%s_%6.6d.h5")
DEFAULT_DURATION = 10  # seconds
DEFAULT_FRAME_RATE = 200  # fps  (expect occasional dropped frames at ~1_000 fps)
# computed terms next ...
DEFAULT_ACQUIRE_TIME = 1.0 / DEFAULT_FRAME_RATE
DEFAULT_ACQUIRE_PERIOD = DEFAULT_ACQUIRE_TIME
DEFAULT_N_IMAGES = int(DEFAULT_DURATION * DEFAULT_FRAME_RATE)


def prep_camera(det, n_images, t_acq, t_period, mode):
    """Prepare the cam plugin for acquisition."""
    # fmt: off
    yield from bps.mv(
        det.cam.acquire_period, t_period,
        det.cam.acquire_time, t_acq,
        det.cam.image_mode, mode,
        det.cam.num_images, n_images,
    )
    # fmt: on


def prep_hdf_plugin(plugin, n_images, file_path, file_name):
    """Prepare the hdf1 plugin for acquisition."""
    # these must be set in steps
    # fmt: off
    plugin.enable_on_stage()
    plugin.kind = Kind.config | Kind.normal
    yield from bps.mv(
        plugin.auto_increment, "Yes",
        plugin.auto_save, "Yes",
        plugin.create_directory, -5,
        plugin.file_number, 0,
        plugin.file_template, HDF5_FILE_TEMPLATE,
    )
    print(f"{file_path=}")
    yield from bps.mv(
        # plugin.compression, None,
        # plugin.enable, 1,
        plugin.file_path, file_path,
        plugin.num_capture, n_images,  # save all frames received
    )
    yield from bps.mv(
        plugin.file_name, file_name,
        # avoids: ERROR: capture not supported in Single mode
        plugin.file_write_mode, "Stream",
    )
    # fmt: on


def restore_hdf_plugin(plugin):
    # fmt: off
    yield from bps.mv(
        plugin.file_write_mode, "Single",
    )
    # fmt: on


def bdp_acquire(
    acq_rep=3,
    file_name="Test",
    acquire_time=DEFAULT_ACQUIRE_TIME,
    acquire_period=DEFAULT_ACQUIRE_PERIOD,
    n_images=DEFAULT_N_IMAGES,
    file_path="/home/8ididata/2023-1/bluesky202301",
    method="stream",
    md=None,
):
    """Repeated Acquisition (using Lambda2M detector)."""

    if md is None:
        md = {}

    det = lambda2M

    det.roi1.kind = Kind.omitted  # reset (so we can ignore) it

    n_images = max(n_images, 1)
    image_mode = "Multiple" if n_images > 1 else "Single"

    _md = dict(
        file_name=file_name,
        method=method,
        n_images=n_images,
        acquire_time=acquire_time,
        acquire_period=acquire_period,
        image_mode=image_mode,
        detector_name=det.name,
    )

    # configure the cam
    yield from prep_camera(det, n_images, acquire_time, acquire_period, image_mode)

    print(f"Staging setup {det.stage_sigs=}")
    print(f"Staging setup {det.cam.stage_sigs=}")

    # fmt: off
    if method == "file":
        # configure the HDF plugin, only if used
        md.update(
            dict(
                file_path=file_path,
                file_template=HDF5_FILE_TEMPLATE,
            )
        )
        print(f"{md=}")
        yield from prep_hdf_plugin(det.hdf1, n_images, file_path, file_name)
        print(f"Staging setup {det.hdf1.stage_sigs=}")
    else:
        det.hdf1.disable_on_stage()
        det.hdf1.kind = Kind.omitted
    # fmt: on

    _md.update(md)  # add the user-supplied metadata, if any
    print(f"run metadata: {_md}")

    # BestEffortCallback not necessary here and it slows down the plan.
    bec.disable_plots()
    bec.disable_table()
    for ii in range(acq_rep):
        print(f"Iteration {ii+1} of {acq_rep}...")
        yield from bp.count([det], md=_md)
    bec.enable_plots()
    bec.enable_table()
