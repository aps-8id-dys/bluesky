"""
EPICS area_detector common support
"""

__all__ = """
build_xpcs_area_detector
CamBase_V34
FileBase_V34
XpcsAD_CommonAreaDetectorDevice
XpcsAD_EpicsFileNameHDF5Plugin
XpcsAD_ImagePlugin
XpcsAD_PvaPlugin
XpcsAD_ROIPlugin
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

import time
from pathlib import PurePath

from apstools.devices import (
    AD_EpicsFileNameHDF5Plugin,
    AD_plugin_primed,
    AD_prime_plugin2,
)
from ophyd import ADComponent
from ophyd.areadetector import CamBase, DetectorBase, SingleTrigger
from ophyd.areadetector.plugins import (
    CodecPlugin_V34,
    FileBase,
    ImagePlugin_V34,
    PvaPlugin_V34,
    ROIPlugin_V34,
)
from ophyd.ophydobj import Kind
from ophyd.status import Status

from .. import iconfig

# LAMBDA2M_FILES_ROOT = PurePath("/extdisk/")
# BLUESKY_FILES_ROOT = PurePath("/home/8ididata/")
# # IMAGE_DIR = "%Y/%m/%d/"
# IMAGE_DIR = "2023-2/pvaccess_test"

# # MUST end with a `/`, pathlib will NOT provide it
# WRITE_PATH_TEMPLATE = f"{LAMBDA2M_FILES_ROOT / IMAGE_DIR}/"
# READ_PATH_TEMPLATE = f"{BLUESKY_FILES_ROOT / IMAGE_DIR}/"

# DET_NAME = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["NAME"]
# PV_PREFIX = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["PV_PREFIX"]


class CamBase_V34(CamBase):
    """
    Updates to CamBase since v22.

    PVs removed from AD now.
    """

    pool_max_buffers = None


class FileBase_V34(FileBase):
    """
    Updates to FileBase since v22.

    PVs removed from AD now.
    """

    file_number_sync = None
    file_number_write = None


class XpcsAD_EpicsFileNameHDF5Plugin(AD_EpicsFileNameHDF5Plugin):
    """Remove property attribute not found in AD IOCs now."""

    _asyn_pipeline_configuration_names = None

    @property
    def _plugin_enabled(self):
        return self.stage_sigs.get("enable") in (1, "Enable")

    def generate_datum(self, *args, **kwargs):
        if self._plugin_enabled:
            super().generate_datum(*args, **kwargs)

    def read(self):
        if self._plugin_enabled:
            readings = super().read()
        else:
            readings = {}
        return readings

    def stage(self):
        if self._plugin_enabled:
            staged_objects = super().stage()
        else:
            staged_objects = []
        return staged_objects

    def trigger(self):
        if self._plugin_enabled:
            trigger_status = super().trigger()
        else:
            trigger_status = Status(self)
            trigger_status.set_finished()
        return trigger_status


class XpcsAD_ImagePlugin(ImagePlugin_V34):
    """Remove property attribute found in AD IOCs now."""

    _asyn_pipeline_configuration_names = None


class XpcsAD_PvaPlugin(PvaPlugin_V34):
    """Remove property attribute found in AD IOCs now."""

    _asyn_pipeline_configuration_names = None


class XpcsAD_ROIPlugin(ROIPlugin_V34):
    """Remove property attribute found in AD IOCs now."""

    _asyn_pipeline_configuration_names = None


class XpcsAD_CommonAreaDetectorDevice(SingleTrigger, DetectorBase):
    """Common area detector Device class."""

    # Every subclass should define these component.
    # They are specific to the camera.
    #
    # cam = ADComponent(Lambda2MCam, "cam1:")
    # hdf1 = ADComponent(
    #     XpcsAD_EpicsFileNameHDF5Plugin,
    #     "HDF1:",
    #     write_path_template=WRITE_PATH_TEMPLATE,
    #     read_path_template=READ_PATH_TEMPLATE,
    #     kind="normal",
    # )

    # In the AD IOC, cam --> codec & image
    codec1 = ADComponent(CodecPlugin_V34, "Codec1:")  # needed by PVA and HDF
    image = ADComponent(XpcsAD_ImagePlugin, "image1:")

    # In the AD IOC, codec1 --> hdf1 & pva
    # If AD IOC sends codec1 to roi (& roi1?)
    pva = ADComponent(XpcsAD_PvaPlugin, "Pva1:")
    # roi1 = ADComponent(MyROIPlugin, "ROI1:")


def build_xpcs_area_detector(
    ad_class,  # subclass of XpcsCommonAreaDetectorDevice
    pv_prefix,  # EPICS PV prefix
    detector_name,  # for the ophyd device
    labels=["area_detector"],  # for the %wa command
    **kwargs,  # anything else the caller wants to add
):
    if not issubclass(ad_class, XpcsAD_CommonAreaDetectorDevice):
        # fmt:off
        raise TypeError(
            f"{ad_class} must be a subclass of"
            f" {XpcsAD_CommonAreaDetectorDevice.__class__.__name__}")
        # fmt:on

    t0 = time.time()
    try:
        # fmt: off
        connection_timeout = iconfig.get("PV_CONNECTION_TIMEOUT", 15)
        det = ad_class(
            pv_prefix, name=detector_name, labels=labels, **kwargs,
        )
        det.wait_for_connection(timeout=connection_timeout)
        # fmt: on

    except (KeyError, NameError, TimeoutError) as exinfo:
        # fmt: off
        logger.warning(
            "Error connecting with PV='%s in %.2fs, %s",
            pv_prefix, time.time() - t0, str(exinfo),
        )
        logger.warning("Setting %s to None.", detector_name)
        det = None
        # fmt: on

    else:
        # just in case these things are not defined in the class source code
        det.cam.stage_sigs["wait_for_plugins"] = "Yes"
        for nm in det.component_names:
            obj = getattr(det, nm)
            if "blocking_callbacks" in dir(obj):  # is it a plugin?
                obj.stage_sigs["blocking_callbacks"] = "No"

        plugin = det.hdf1  # for convenience below
        plugin.kind = Kind.config | Kind.normal  # Ensure plugin's read is called.
        plugin.stage_sigs.move_to_end("capture", last=True)

        if iconfig.get("ALLOW_AREA_DETECTOR_WARMUP", False):
            if det.connected:
                if not AD_plugin_primed(plugin):
                    AD_prime_plugin2(plugin)

    return det
