"""
EPICS area_detectors
"""

__all__ = """
    adsim4M
    eiger4M
    lambda2M
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from .ad_common import XpcsAreaDetectorFactory  # noqa

adsim4M = XpcsAreaDetectorFactory("ADSIM_4M", use_image=False)
eiger4M = XpcsAreaDetectorFactory("EIGER_4M", use_image=False)
# lambda2M = XpcsAreaDetectorFactory("LAMBDA_2M", use_image=False)
lambda2M = None  # TODO: re-enable?

if eiger4M is not None:
    eiger4M.cam.data_source.put("Stream")
    eiger4M.cam.stream_decompress.put("Disable")
