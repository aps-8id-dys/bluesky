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
from ophyd.ophydobj import Kind

from ..devices import lambda2M
from ..devices import lambda2Mpva
from ..framework import bec

AD_HDF5_FILE_TEMPLATE = "%s%s_%6.6d.h5"
DEFAULT_DURATION = 10  # seconds
DEFAULT_FRAME_RATE = 200  # fps  (expect occasional dropped frames at ~1_000 fps)
# computed terms next ...
DEFAULT_ACQUIRE_TIME = 1.0 / DEFAULT_FRAME_RATE
DEFAULT_ACQUIRE_PERIOD = DEFAULT_ACQUIRE_TIME
DEFAULT_N_IMAGES = int(DEFAULT_DURATION * DEFAULT_FRAME_RATE)
LAMBDA2M_CAMERAS = dict(file=lambda2M, stream=lambda2Mpva)


def prep_camera(det, n_images, t_acq, t_period, mode):
    """Prepare the cam plugin for acquisition."""
    yield from bps.mv(
        det.cam.acquire_period, t_period,
        det.cam.acquire_time, t_acq,
        det.cam.image_mode, mode,
        det.cam.num_images, n_images,
    )


def prep_hdf_plugin(plugin, n_images, file_path, file_name):
    """Prepare the hdf1 plugin for acquisition."""
    # these must be set in steps
    yield from bps.mv(
        plugin.auto_increment, "Yes",
        plugin.auto_save, "Yes",
        plugin.create_directory, -5,
        plugin.file_number, 0,
        plugin.file_template, AD_HDF5_FILE_TEMPLATE,
    )
    yield from bps.mv(
        # plugin.compression, None,
        # plugin.enable, 1,
        plugin.file_path, file_path,
        plugin.num_capture, n_images,  # save all frames received
    )
    yield from bps.mv(
        plugin.file_name, file_name,
    )


def bdp_acquire(
    acq_rep=3,
    file_name="Test",
    acquire_time=DEFAULT_ACQUIRE_TIME,
    acquire_period=DEFAULT_ACQUIRE_PERIOD,
    n_images=DEFAULT_N_IMAGES,
    file_path="/home/8ididata/2023-1/bluesky202301",
    method="stream",
    md={},
):
    """Repeated Acquisition (using Lambda2M detector)."""

    det = LAMBDA2M_CAMERAS[method]  # pick the detector instance
    for m, det in LAMBDA2M_CAMERAS.items():
        print(f"method='{m}' uses detector {det.name}.connected={det.connected}")
    print(f"Selected detector '{det.name}' with method '{method}'.")

    det.roi1.kind = Kind.omitted  # reset (so we can ignore) it

    n_images = max(n_images, 1)
    image_mode = "Multiple" if n_images > 1 else "Single"

    _md = dict(
        file_name=file_name,
        use_hdf=use_hdf,
        acquire_time=acquire_time,
        acquire_period=acquire_period,
        image_mode=image_mode,
        n_images=n_images,
        method=method,
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
                file_template=AD_HDF5_FILE_TEMPLATE,
            )
        )
        yield from prep_hdf_plugin(det.hdf1, n_images, file_path, file_name)
        print(f"Staging setup {det.hdf1.stage_sigs=}")
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
