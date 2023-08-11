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
from ophyd.ophydobj import Kind
from ophyd.status import Status

LAMBDA2M_FILES_ROOT = PurePath("/extdisk/")
BLUESKY_FILES_ROOT = PurePath("/home/8ididata/")
# IMAGE_DIR = "%Y/%m/%d/"
IMAGE_DIR = "2023-2/pvaccess_test"

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{LAMBDA2M_FILES_ROOT / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_FILES_ROOT / IMAGE_DIR}/"

DET_NAME = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["NAME"]
PV_PREFIX = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["PV_PREFIX"]


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
    """Custom Lambda2M detector."""

    cam = ADComponent(Lambda2MCam, "cam1:")

    # cam --> codec & image
    codec1 = ADComponent(CodecPlugin_V34, "Codec1:")
    image = ADComponent(MyImagePlugin, "image1:")

    # codec1 --> hdf1 & pva (& roi1?)
    hdf1 = ADComponent(
        MyAD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
        kind="normal",
    )
    pva = ADComponent(MyPvaPlugin, "Pva1:")
    roi1 = ADComponent(MyROIPlugin, "ROI1:")


t0 = time.time()
try:
    # fmt: off
    lambda2M = Lambda2MDetector(
        PV_PREFIX, name=DET_NAME, labels=["area_detector"]
    )
    connection_timeout = iconfig.get("PV_CONNECTION_TIMEOUT", 15)
    lambda2M.wait_for_connection(timeout=connection_timeout)
    # fmt: on

except (KeyError, NameError, TimeoutError) as exinfo:
    # fmt: off
    logger.warning(
        "Error connecting with PV='%s in %.2fs, %s",
        PV_PREFIX, time.time() - t0, str(exinfo),
    )
    logger.warning("Setting lambda2M to None.")
    lambda2M = None
    # fmt: on

else:
    # just in case these things are not defined in the class source code
    det = lambda2M
    det.cam.stage_sigs["wait_for_plugins"] = "Yes"
    for nm in det.component_names:
        obj = getattr(det, nm)
        if "blocking_callbacks" in dir(obj):  # is it a plugin?
            obj.stage_sigs["blocking_callbacks"] = "No"

    det = lambda2M  # for convenience below
    plugin = det.hdf1  # for convenience below
    plugin.kind = Kind.config | Kind.normal  # Ensure plugin's read is called.
    plugin.stage_sigs.move_to_end("capture", last=True)

    if iconfig.get("ALLOW_AREA_DETECTOR_WARMUP", False):
        if det.connected:
            if not AD_plugin_primed(plugin):
                AD_prime_plugin2(plugin)
