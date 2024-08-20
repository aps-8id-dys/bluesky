"""
EPICS area_detectors
"""

__all__ = """
    flag2ad
""".split()


import logging

from .ad_common import XpcsAreaDetectorFactory

logger = logging.getLogger(__name__)
logger.info(__file__)

flag2ad = XpcsAreaDetectorFactory(
    "FLAG2", use_process=False, use_roi=False, use_stats=False
)
