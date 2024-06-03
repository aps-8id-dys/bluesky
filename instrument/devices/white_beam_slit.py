"""
White Beam Slit
"""

__all__ = """
    wbslit
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from apstools.devices.hhl_slits import HHLSlits

wbslit = HHLSlits(name="wbslit", prefix="8idaSoft:CR8-A1:US", pitch_motor="m3", yaw_motor="m4", horizontal_motor="m1", diagonal_motor="m2")
