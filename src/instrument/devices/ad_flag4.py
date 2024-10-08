"""
EPICS area_detectors
"""

__all__ = """
    flag4ad
""".split()


import logging

from .ad_common import XpcsAreaDetectorFactory

logger = logging.getLogger(__name__)
logger.info(__file__)

flag4ad = XpcsAreaDetectorFactory(
    "FLAG4",
    use_image=False,  # This raised an error
    use_process=False,  # Do not use the AD Processing plugin: PROC1
    use_roi=True,
    use_stats=True,
)
