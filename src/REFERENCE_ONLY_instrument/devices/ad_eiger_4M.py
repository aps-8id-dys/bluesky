"""
EPICS area_detectors
"""

__all__ = """
    eiger4M
""".split()


import logging

from .ad_common import XpcsAreaDetectorFactory

logger = logging.getLogger(__name__)
logger.info(__file__)

eiger4M = XpcsAreaDetectorFactory("EIGER_4M", use_image=False)

# eiger4M.stats1.kind = "hinted"
# eiger4M.stats1.mean_value = "hinted"

if eiger4M is not None:
    # TODO: only on warmup?  Or in setup plan?
    # Just not on startup, blindly like this.
    eiger4M.cam.data_source.put("Stream")
    eiger4M.cam.stream_decompress.put("Disable")
