"""
EPICS area_detectors
"""

__all__ = """
    adsim4M
""".split()


import logging

from .ad_common import XpcsAreaDetectorFactory

logger = logging.getLogger(__name__)
logger.info(__file__)

adsim4M = XpcsAreaDetectorFactory("ADSIM_4M", use_image=False)
