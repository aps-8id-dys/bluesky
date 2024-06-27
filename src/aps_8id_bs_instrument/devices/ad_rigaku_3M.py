"""
EPICS area_detectors
"""

__all__ = """
    rigaku3M
""".split()


from .ad_common import XpcsAreaDetectorFactory  # noqa
import logging

logger = logging.getLogger(__name__)
logger.info(__file__)


rigaku3M = None  # TODO: IOC is still in development
