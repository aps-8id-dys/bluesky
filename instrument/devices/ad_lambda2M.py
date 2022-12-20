"""
EPICS area_detector Lambda 2M
"""

__all__ = """
    lambda2M
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

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

    firmware_version = ADComponent(EpicsSignalRO, "FirmwareVersion_RBV")
    operating_mode = ADComponent(EpicsSignalWithRBV, "OperatingMode")
    serial_number = ADComponent(EpicsSignalRO, "SerialNumber_RBV")
    temperature = ADComponent(EpicsSignalWithRBV, "Temperature")
    wait_for_plugins = ADComponent(EpicsSignal, 'WaitForPlugins', string=True)

    # Aren't these next components part of the HDF5 module?
    # file_path = ADComponent(EpicsSignal, 'FilePath', string=True)
    # create_directory = ADComponent(EpicsSignal, "CreateDirectory")

    EXT_TRIGGER = 0


class MyAD_EpicsFileNameHDF5Plugin(AD_EpicsFileNameHDF5Plugin):
    """Remove property attribute not found in Lambda2M."""
    _asyn_pipeline_configuration_names = None


class MyImagePlugin(ImagePlugin_V34):
    """Remove property attribute not found in Lambda2M."""
    _asyn_pipeline_configuration_names = None


class MyPvaPlugin(PvaPlugin_V34):
    """Remove property attribute not found in Lambda2M."""
    _asyn_pipeline_configuration_names = None


class Lambda2MDetector(SingleTrigger, DetectorBase):
    """Custom Lambda2MDetector."""

    cam = ADComponent(Lambda2MCam, "cam1:")
    hdf1 = ADComponent(
        MyAD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=str(LAMBDA2M_FILES_ROOT / IMAGE_DIR),
        read_path_template=str(BLUESKY_FILES_ROOT / IMAGE_DIR),
        kind='normal'
    )
    image = ADComponent(MyImagePlugin, "image1:")
    pva = ADComponent(MyPvaPlugin, "Pva1:")
    codec1 = ADComponent(CodecPlugin_V34, "Codec1:")


lambda2M = Lambda2MDetector("8idLambda2m:", name="lambda2M")

# Create two (local) convenience definitions which make
# it easier to copy/paste to other similar detectors.
det = lambda2M  # for convenience below
plugin = det.hdf1  # for convenience below

det.read_attrs.append(plugin.attr_name)  # Ensure plugin's read is called.

# just in case these are not defined in the class source code
det.cam.stage_sigs["wait_for_plugins"] = "Yes"
det.image.stage_sigs["blocking_callbacks"] = "No"
plugin.stage_sigs["blocking_callbacks"] = "No"
plugin.stage_sigs.move_to_end("capture", last=True)

det.wait_for_connection(timeout=iconfig.get("PV_CONNECTION_TIMEOUT", 15))

# Needed if IOC has just been started
# plugin.auto_increment.put("Yes")
# plugin.auto_save.put("Yes")
# plugin.create_directory.put(-5)

if iconfig.get("ALLOW_AREA_DETECTOR_WARMUP", False):
    if not AD_plugin_primed(plugin):
        AD_prime_plugin2(plugin)
