"""
EPICS area_detector ADSimDetector 4M
"""

__all__ = """
    adsim4M
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from .. import iconfig
from .ad_common import BLUESKY_FILES_ROOT
from .ad_common import IMAGE_DIR
from .ad_common import SimDetectorCam_V34
from .ad_common import XpcsAD_factory

DET_NAME = iconfig["AREA_DETECTOR"]["SIMDET_4M"]["NAME"]
PV_PREFIX = iconfig["AREA_DETECTOR"]["SIMDET_4M"]["PV_PREFIX"]

ADSIM4M_FILES_ROOT = BLUESKY_FILES_ROOT  # Same filesystem

# TODO: refactor these lines into the factory so users do not have to "get it right"
# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{ADSIM4M_FILES_ROOT / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_FILES_ROOT / IMAGE_DIR}/"

adsim4M = XpcsAD_factory(
    PV_PREFIX, DET_NAME, SimDetectorCam_V34, WRITE_PATH_TEMPLATE, READ_PATH_TEMPLATE,
    use_image=False
)
