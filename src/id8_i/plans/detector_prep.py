"""
Prepare an area detector for acquisition.

see: https://bcda-aps.github.io/apstools/examples/de_1_adsim_hdf5_custom_names.html
"""

from bluesky import plan_stubs as bps


def prepare_count(
    plugin,  # NOTE: NOT GENERAL, only the HDF5 writer plugin is expected
    file_name,
    acquire_time,
    acquire_period,
    n_images=1,
    auto_increment="Yes",
    auto_save="Yes",
    compression=None,
    create_directory=-5,
    file_path=None,
    file_template=None,
):
    """
    prepare count
    """
    ad_det = plugin.parent
    # compression should be "None" if CODEC1 plugin compresses the image
    compression = compression or "zlib"
    file_path = file_path or plugin.write_path_template  # WRITE_PATH_TEMPLATE
    file_template = file_template or "%s%s_%4.4d.h5"
    n_images = max(n_images, 1)
    image_mode = "Multiple" if n_images > 1 else "Single"

    yield from bps.mv(
        plugin.enable,
        1,
        plugin.create_directory,
        create_directory,
    )
    # MUST set create_directory BEFORE file_path

    yield from bps.mv(
        plugin.file_path,
        file_path,
        plugin.file_template,
        file_template,
    )

    # NOW, set the other components
    # fmt: off
    yield from bps.mv(
        ad_det.cam.num_images, n_images,
        ad_det.cam.acquire_time, acquire_time,
        ad_det.cam.acquire_period, acquire_period,
        ad_det.cam.image_mode, image_mode,
        plugin.auto_increment, auto_increment,
        plugin.auto_save, auto_save,
        plugin.file_name, file_name,
        plugin.num_capture, n_images,  # save all frames received
        plugin.compression, compression,
    )
    # fmt: on
