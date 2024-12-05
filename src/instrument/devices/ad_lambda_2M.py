"""
EPICS area_detectors
"""

__all__ = """
    lambda2M
""".split()


from .ad_common import XpcsAreaDetectorFactory  # noqa
import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

lambda2M = XpcsAreaDetectorFactory("LAMBDA_2M", use_image=False)
# lambda2M = None  # TODO: re-enable?
