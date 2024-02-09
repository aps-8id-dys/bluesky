"""
EPICS area_detectors
"""

__all__ = """
    adsim4M
    eiger4M
    lambda2M
    rigaku3M
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from .ad_common import XpcsAreaDetectorFactory  # noqa

adsim4M = XpcsAreaDetectorFactory("ADSIM_4M", use_image=False)
# adsim16M = XpcsAreaDetectorFactory("ADSIM_16M", use_image=False)
eiger4M = XpcsAreaDetectorFactory("EIGER_4M", use_image=False)
# lambda2M = XpcsAreaDetectorFactory("LAMBDA_2M", use_image=False)
lambda2M = None  # TODO: re-enable?
# rigaku3M = XpcsAreaDetectorFactory("RIGAKU_3M", use_image=False)
rigaku3M = None  # TODO: IOC is still in development

if eiger4M is not None:
    # TODO: only on warmup?  Or in setup plan?
    # Just not on startup, blindly like this.
    eiger4M.cam.data_source.put("Stream")
    eiger4M.cam.stream_decompress.put("Disable")
