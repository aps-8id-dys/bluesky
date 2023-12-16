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

from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV

from .. import iconfig
from .ad_common import BLUESKY_FILES_ROOT
from .ad_common import CamBase_V34
from .ad_common import IMAGE_DIR
from .ad_common import XpcsAD_factory

DET_NAME = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["NAME"]
PV_PREFIX = iconfig["AREA_DETECTOR"]["LAMBDA_2M"]["PV_PREFIX"]

LAMBDA2M_FILES_ROOT = PurePath("/extdisk/")

# TODO: refactor these lines into the factory so users do not have to "get it right"
# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{LAMBDA2M_FILES_ROOT / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_FILES_ROOT / IMAGE_DIR}/"


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


lambda2M = XpcsAD_factory(PV_PREFIX, DET_NAME, Lambda2MCam, WRITE_PATH_TEMPLATE, READ_PATH_TEMPLATE)
