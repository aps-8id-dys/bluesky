"""
Bluesky plans to setup various Area Detectors for acquisition.
"""

from __future__ import annotations

__all__ = """
    ad_acquire_setup
    eiger4M_acquire_setup
    setup_hdf5_plugin
    write_if_new
    DetectorStateError
    HDF5PluginError
""".split()

import logging
import pathlib

from apstools.devices import AD_EpicsFileNameHDF5Plugin
from bluesky import plan_stubs as bps
from ophyd import Kind

from aps_8id_bs_instrument.devices import eiger4M

logger = logging.getLogger(__name__)
logger.info(__file__)


def write_if_new(signal, value):
    """Write an ophyd signal if it has a new value."""
    if value is not None and signal.get() != value:
        yield from bps.mv(signal, value)


class DetectorStateError(RuntimeError):
    """For custom errors in this module."""


class HDF5PluginError(RuntimeError):
    """An error with configuration of the HDF5 plugin."""


def ad_acquire_setup(
    det,  # area detector object
    acquire_time: float = 0.01,
    acquire_period: float = 0.01,
    num_capture: int = 1,
    num_exposures: int = 1,
    num_images: int = 1_000,
    num_triggers: int = 1,
    path="",  # str or pathlib.Path
):
    """
    Prepare any area detector for the next acquisition(s).

    Each parameter should have a defined type and default value, for use in the
    bluesky queueserver.  These parameters should be copied to the user-facing
    plan that appears in the queueserver.
    """
    cam = det.cam
    hdf = det.hdf1

    # Make the settings.
    settings = {
        cam.acquire_time: acquire_time,
        cam.acquire_period: acquire_period,
        cam.num_exposures: num_exposures,
        cam.num_images: num_images,
    }
    for signal, value in settings.items():
        if signal.get() != value:  # write only if different
            yield from bps.abs_set(signal, value)

    # Python attributes (not ophyd Signals)
    # allow for a pathlib object
    hdf.write_path_template = hdf.read_path_template = f"{path}/"


def eiger4M_acquire_setup(
    det,  # area detector object
    # acquire_time: float = 0.01,
    # acquire_period: float = 0.01,
    # num_capture: int = 1,
    # num_exposures: int = 1,
    # num_images: int = 1_000,
    num_triggers: int = 1,
    # path="",  # str or pathlib.Path
):
    """
    Prepare the Eiger4M detector for the next acquisition(s).
    """
    det = eiger4M
    cam = det.cam

    yield from write_if_new(cam.num_triggers, num_triggers)

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


def setup_hdf5_plugin(
    hdf,  # Area Detector's HDF5 plugin
    write_path: (str, pathlib.Path),  # Directory (as seen from the EPICS IOC)
    file_name: str,
    template: str = "%s%s.h5",
    dir_depth: int = -5,
    file_number: (int, None) = None,  # next file number
    auto_increment: bool = True,
    lazy_open: bool = False,
    auto_save: bool = True,
    write_mode: str = "Stream",
    num_capture: int = 1,
    cam_wait_for_plugins: bool = True,
    read_path: str = None,
):
    """
    (plan) Configure the area detector HDF5 plugin for acquisition.

    Allow the user to control the file name, write_path, and other parameters.
    Any of the keyword parameters may have value of ``None`` which means
    this setup plan should not change the existing value.

    EXAMPLE::

        ioc_file_path = "/tmp/Italy"
        yield from setup_hdf5_plugin(
            ad.hdf1,
            ioc_file_path,
            "Harold",
            template="%s%s.h5",
            read_path="/mnt/iockad" + ioc_file_path,
            write_mode="Stream"
        )
        yield from bp.count([ad])

    """
    if (
        # fmt: off
        not isinstance(hdf, AD_EpicsFileNameHDF5Plugin)
        # Test how filenames are created.
        # ophyd standard practice is to use short UUID, each call to
        # hdf.make_filename() returns a different result.  With
        # AD_EpicsFileNameHDF5Plugin, the results will be the same each time.
        # The file_template is not used by hdf.make_filename().
        or hdf.make_filename() != hdf.make_filename()
        # fmt: on
    ):
        raise HDF5PluginError(
            "'hdf' object must be built with"
            " 'apstools.devices.AD_EpicsFileNameHDF5Plugin'."
            f"  Received {type(hdf)!r}."
        )

    if len(str(write_path)) == 0:
        raise HDF5PluginError("'path' parameter must not be empty.")

    if len(file_name) == 0:
        raise HDF5PluginError("'file_name' parameter must not be empty.")

    # fmt: off
    if (
        write_mode is not None
        and write_mode not in hdf.file_write_mode.enum_strs
    ):
        raise HDF5PluginError(
            f"File write mode {write_mode!r} not available."
            f"  Pick one of these: {hdf.file_write_mode.enum_strs!r}."
        )
    # fmt: on

    # MUST be set before the file_path.
    yield from write_if_new(hdf.create_directory, dir_depth)

    # write_path MUST end with "/"
    yield from write_if_new(hdf.file_path, f"{pathlib.Path(write_path)}/")
    # Check that path exists now (might have just been created).
    if hdf.file_path_exists.get() not in (1, "Yes"):
        raise HDF5PluginError(
            f"File path {write_path!r} does not exist."
            f"  PV ({hdf.file_path!r}) = {hdf.file_path.get()!r}."
        )
    hdf.write_path_template = hdf.file_path.get()
    if read_path is None:
        read_path = hdf.write_path_template
    hdf.read_path_template = f"{pathlib.Path(read_path)}/"

    yield from write_if_new(hdf.file_name, file_name)
    yield from write_if_new(hdf.file_number, file_number)
    yield from write_if_new(hdf.file_template, template)
    yield from write_if_new(hdf.file_write_mode, write_mode)
    yield from write_if_new(hdf.num_capture, num_capture)

    # These boolean settings have Yes or No values in EPICS.
    yn = {True: "Yes", False: "No"}
    yield from write_if_new(hdf.auto_increment, yn[auto_increment])
    yield from write_if_new(hdf.auto_save, yn[auto_save])
    yield from write_if_new(hdf.lazy_open, yn[lazy_open])

    hdf.stage_sigs["blocking_callbacks"] = "No"
    hdf.stage_sigs["file_write_mode"] = write_mode
    hdf.stage_sigs["parent.cam.wait_for_plugins"] = yn[cam_wait_for_plugins]
    hdf.stage_sigs["capture"] = 1
    if write_mode == "Single":
        hdf.stage_sigs.pop("capture")
    else:
        hdf.stage_sigs.move_to_end("capture", last=True)
    hdf.kind = Kind.normal | Kind.hinted
