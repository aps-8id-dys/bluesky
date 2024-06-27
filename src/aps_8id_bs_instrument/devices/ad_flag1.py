"""
EPICS area_detectors
"""

__all__ = """
    flag1ad
""".split()


import logging

from .ad_common import XpcsAreaDetectorFactory

logger = logging.getLogger(__name__)
logger.info(__file__)

flag1ad = XpcsAreaDetectorFactory("FLAG1")  # all configured plugins enabled