"""
RL1: Transfocator (compound refractive lens, CRL) in 8-ID-D.
"""

__all__ = """
    rl1
""".split()

import logging

from ._8id_common import Transfocator

logger = logging.getLogger(__name__)
logger.info(__file__)


rl1 = Transfocator(
    "8iddSoft:TRANS:",
    name="rl1",
    pv_y="m1",
    pv_x="m2",
    pv_yaw="m3",
    pv_pitch="m4",
    pv_lens1="m5",
    pv_lens2="m6",
    pv_lens3="m7",
    pv_lens4="m8",
    pv_lens5="m9",
    pv_lens6="m10",
    pv_lens7="m11",
    pv_lens8="m12",
    pv_lens9="m13",
    pv_lens10="m14",
)
