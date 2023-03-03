"""
EPICS area_detector Lambda 2M
"""

__all__ = """
    lambda2M
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

import time

from pathlib import PurePath

from .. import iconfig
from apstools.devices import AD_EpicsFileNameHDF5Plugin
from apstools.devices import AD_plugin_primed
from apstools.devices import AD_prime_plugin2
from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.plugins import FileBase
from ophyd.areadetector.plugins import CodecPlugin_V34
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import PvaPlugin_V34
from ophyd.areadetector.plugins import ROIPlugin_V34
from ophyd.status import Status

LAMBDA2M_FILES_ROOT = PurePath("/extdisk/")
BLUESKY_FILES_ROOT = PurePath("/home/8ididata/")
# IMAGE_DIR = "%Y/%m/%d/"
IMAGE_DIR = "2023-1/bluesky202301"


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


class Lambda2MCam(CamBase_V34):
    """
    Support for the Lambda 2M cam controls.

    https://x-spectrum.de/products/lambda/
    """

    _html_docs = ["Lambda2MCam.html"]

    firmware_version = ADComponent(EpicsSignalRO, "FirmwareVersion_RBV", kind="omitted")
    operating_mode = ADComponent(EpicsSignalWithRBV, "OperatingMode", kind="config")
    serial_number = ADComponent(EpicsSignalRO, "SerialNumber_RBV", kind="omitted")
    temperature = ADComponent(EpicsSignalWithRBV, "Temperature", kind="config")
    wait_for_plugins = ADComponent(EpicsSignal, "WaitForPlugins", string=True, kind="config")

    energy_threshold = ADComponent(EpicsSignalWithRBV, "EnergyThreshold", kind="config")
    dual_mode = ADComponent(EpicsSignalWithRBV, "DualMode", string=True, kind="config")
    dual_threshold = ADComponent(EpicsSignalWithRBV, "DualThreshold", kind="config")

    EXT_TRIGGER = 0


class MyAD_EpicsFileNameHDF5Plugin(AD_EpicsFileNameHDF5Plugin):
    """Remove property attribute not found in Lambda2M."""

    _asyn_pipeline_configuration_names = None

    def stage(self):
        # ONLY stage if enabled
        if self.stage_sigs.get("enable") in (1, "Enable"):
            result = super().stage()
        else:
            result = []
        return result


class MyImagePlugin(ImagePlugin_V34):
    """Remove property attribute not found in Lambda2M."""

    _asyn_pipeline_configuration_names = None


class MyPvaPlugin(PvaPlugin_V34):
    """Remove property attribute not found in Lambda2M."""

    _asyn_pipeline_configuration_names = None


class MyROIPlugin(ROIPlugin_V34):
    """Remove property attribute not found in Lambda2M."""

    _asyn_pipeline_configuration_names = None


class Lambda2MDetector(SingleTrigger, DetectorBase):
    """Custom Lambda2MDetector."""

    cam = ADComponent(Lambda2MCam, "cam1:")

    # cam --> codec & image
    codec1 = ADComponent(CodecPlugin_V34, "Codec1:")
    image = ADComponent(MyImagePlugin, "image1:")

    # codec1 --> hdf1 & pva
    hdf1 = ADComponent(
        MyAD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=str(LAMBDA2M_FILES_ROOT / IMAGE_DIR),
        read_path_template=str(BLUESKY_FILES_ROOT / IMAGE_DIR),
        kind="normal",
    )
    pva = ADComponent(MyPvaPlugin, "Pva1:")
    roi1 = ADComponent(MyROIPlugin, "ROI1:")


class Lambda2MDetectorPVA(SingleTrigger, DetectorBase):
    """Custom Lambda2MDetector."""

    cam = ADComponent(Lambda2MCam, "cam1:")

    # cam --> codec & image
    codec1 = ADComponent(CodecPlugin_V34, "Codec1:")
    image = ADComponent(MyImagePlugin, "image1:")

    # codec1 --> pva
    pva = ADComponent(MyPvaPlugin, "Pva1:")
    roi1 = ADComponent(MyROIPlugin, "ROI1:")


DET_NAME = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["NAME"]
PV_PREFIX = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["PV_PREFIX"]

t0 = time.time()
try:
    # fmt: off
    lambda2M = Lambda2MDetector(
        PV_PREFIX, name=DET_NAME, labels=["area_detector"]
    )
    lambda2Mpva = Lambda2MDetectorPVA(
        PV_PREFIX, name="lambda2Mpva", labels=["area_detector"]
    )
    # fmt: on

    # Create two (local) convenience definitions which make
    # it easier to copy/paste to other similar detectors.
    det = lambda2M  # for convenience below
    plugin = det.hdf1  # for convenience below

    det.read_attrs.append(plugin.attr_name)  # Ensure plugin's read is called.

    # just in case these are not defined in the class source code
    det.cam.stage_sigs["wait_for_plugins"] = "Yes"
    for nm in det.component_names:
        obj = getattr(det, nm)
        if "blocking_callbacks" in dir(obj):  # is it a plugin?
            obj.stage_sigs["blocking_callbacks"] = "No"
    plugin.stage_sigs.move_to_end("capture", last=True)

    det.wait_for_connection(timeout=iconfig.get("PV_CONNECTION_TIMEOUT", 15))

    # Needed if IOC has just been started
    # plugin.auto_increment.put("Yes")
    # plugin.auto_save.put("Yes")
    # plugin.create_directory.put(-5)

    if iconfig.get("ALLOW_AREA_DETECTOR_WARMUP", False):
        if det.connected:
            if not AD_plugin_primed(plugin):
                AD_prime_plugin2(plugin)
except (KeyError, NameError, TimeoutError):
    lambda2M = None
    # fmt: off
    logger.warning(
        "Did not connect '%s' (prefix '%s') in %.2fs.  Setting to 'None'.",
        DET_NAME, PV_PREFIX, time.time() - t0,
    )
    # fmt: on
