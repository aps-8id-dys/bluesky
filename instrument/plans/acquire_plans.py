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

AD_HDF5_FILE_TEMPLATE = "%s%s_%6.6d.h5"
DEFAULT_FRAME_RATE = 200  # fps  (expect occasional dropped frames at ~1_000 fps)
DEFAULT_DURATION = 10  # seconds
DEFAULT_ACQUIRE_TIME = 1.0 / DEFAULT_FRAME_RATE
DEFAULT_ACQUIRE_PERIOD = DEFAULT_ACQUIRE_TIME
DEFAULT_N_IMAGES = int(DEFAULT_DURATION * DEFAULT_FRAME_RATE)


def use_plugin(plugin, use=True):
    """
    Make the lambda2m HDF (or any other AD) plugin optional.
    """
    det = plugin.parent
    if use:
        plugin.enable_on_stage()
        if plugin.attr_name not in det.read_attrs:
            det.read_attrs.append(plugin.attr_name)
    else:
        plugin.disable_on_stage()
        if plugin.attr_name in det.read_attrs:
            det.read_attrs.remove(plugin.attr_name)
    yield from bps.null()


def repeated_acquire(
    acq_rep=3,
    file_name="Test",
    acquire_time=DEFAULT_ACQUIRE_TIME,
    acquire_period=DEFAULT_ACQUIRE_PERIOD,
    n_images=DEFAULT_N_IMAGES,
    file_path="/home/8ididata/2023-1/bluesky202301",
    use_hdf=False,
    md={},
):
    """Repeated Acquisition (using lambda2M)."""
    yield from use_plugin(lambda2M.hdf1, use_hdf)

    n_images = max(n_images, 1)
    image_mode = "Multiple" if n_images > 1 else "Single"

    _md = dict(
        file_name=file_name,
        use_hdf=use_hdf,
        acquire_time=acquire_time,
        acquire_period=acquire_period,
        image_mode=image_mode,
        n_images=n_images,
    )

    # fmt: off
    # configure the cam
    yield from bps.mv(
        lambda2M.cam.acquire_period, acquire_period,
        lambda2M.cam.acquire_time, acquire_time,
        lambda2M.cam.image_mode, image_mode,
        lambda2M.cam.num_images, n_images,
    )

    if use_hdf:
        # configure the HDF plugin, only if used
        md.update(
            dict(
                file_path=file_path,
                file_template=AD_HDF5_FILE_TEMPLATE,
            )
        )
        plugin = lambda2M.hdf1
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
            # plugin.enable, 1
            plugin.file_path, file_path,
            plugin.num_capture, n_images,  # save all frames received
        )
        yield from bps.mv(
            plugin.file_name, file_name,
        )
    # fmt: on

    print(f"Staging setup {lambda2M.stage_sigs=}")
    print(f"Staging setup {lambda2M.cam.stage_sigs=}")
    if use_hdf:
        print(f"Staging setup {lambda2M.hdf1.stage_sigs=}")

    _md.update(md)  # add the user-supplied metadata, if any
    print(f"run metadata: {_md}")

    for ii in range(acq_rep):
        print(f"Iteration {ii+1} of {acq_rep}...")
        yield from bp.count([lambda2M], md=_md)
