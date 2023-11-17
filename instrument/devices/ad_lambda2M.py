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

from ophyd import ADComponent, EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV

from .. import iconfig
from .ad_common import (
    CamBase_V34,
    XpcsAD_EpicsFileNameHDF5Plugin,
    XpcsAD_CommonAreaDetectorDevice,
    build_xpcs_area_detector,
)

LAMBDA2M_FILES_ROOT = PurePath("/extdisk/")
BLUESKY_FILES_ROOT = PurePath("/home/8ididata/")
# IMAGE_DIR = "%Y/%m/%d/"
IMAGE_DIR = "2023-2/pvaccess_test"

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{LAMBDA2M_FILES_ROOT / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_FILES_ROOT / IMAGE_DIR}/"

DET_NAME = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["NAME"]
PV_PREFIX = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["PV_PREFIX"]


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
    wait_for_plugins = ADComponent(
        EpicsSignal, "WaitForPlugins", string=True, kind="config"
    )

    energy_threshold = ADComponent(EpicsSignalWithRBV, "EnergyThreshold", kind="config")
    dual_mode = ADComponent(EpicsSignalWithRBV, "DualMode", string=True, kind="config")
    dual_threshold = ADComponent(EpicsSignalWithRBV, "DualThreshold", kind="config")

    EXT_TRIGGER = 0


class Lambda2MDetector(XpcsAD_CommonAreaDetectorDevice):
    """Custom Lambda2M detector."""

    cam = ADComponent(Lambda2MCam, "cam1:")

    hdf1 = ADComponent(
        XpcsAD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
        kind="normal",
    )


lambda2M = build_xpcs_area_detector(Lambda2MDetector, PV_PREFIX, DET_NAME)
