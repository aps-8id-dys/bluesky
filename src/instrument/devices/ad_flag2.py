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
    "FLAG2", 
    use_process=False,  # Do not use the AD Processing plugin: PROC1
    use_roi=False,  # Do not use the AD Region-of-Interest plugin: ROI1
    use_stats=False,  # Do not use the AD Statistics plugin: Stats1
)
