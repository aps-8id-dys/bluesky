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


# rigaku3M = None  # TODO: IOC is still in development
rigaku3M = XpcsAreaDetectorFactory("RIGAKU_3M", use_hdf=False, use_image=False)

# # Remove any stage_sigs here
# rigaku3M.cam.stage_sigs.pop("wait_for_plugins", None)
# if hasattr(rigaku3M, "hdf1"):
#     rigaku3M.hdf1.stage_sigs.pop("parent.cam.wait_for_plugins", None)
