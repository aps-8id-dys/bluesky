"""
EPICS area_detectors
"""

__all__ = """
    flag3ad
""".split()


import logging

from .ad_common import XpcsAreaDetectorFactory

logger = logging.getLogger(__name__)
logger.info(__file__)

try:
    flag3ad = XpcsAreaDetectorFactory(
        "FLAG3",
        use_process=False,  # Do not use the AD Processing plugin: PROC1
        use_roi=True,
        use_stats=True,
    )
    flag3ad.wait_for_connection()
except Exception as cause:
    logger.warning(f"Could not create flag3ad: {cause}")
    flag3ad = None
