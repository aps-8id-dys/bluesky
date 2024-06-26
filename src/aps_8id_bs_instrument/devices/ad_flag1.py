"""
EPICS area_detectors
"""

__all__ = """
    flag1ad
""".split()


from .ad_common import XpcsAreaDetectorFactory  # noqa
import logging

logger = logging.getLogger(__name__)
logger.info(__file__)


flag1ad = XpcsAreaDetectorFactory("FLAG1")  # all configured plugins enabled
