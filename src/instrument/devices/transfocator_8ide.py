"""
RL2: Transfocator (compound refractive lens, CRL) in 8-ID-E

.. note:: POLAR instrument has some related functions (`transfocator.py`).
    https://github.com/APS-4ID-POLAR/polar_instrument/pull/7/files
"""

__all__ = """
    rl2
""".split()

import logging

from ._8id_common import Transfocator

logger = logging.getLogger(__name__)
logger.info(__file__)


rl2 = Transfocator(
    "8iddSoft:TRANS:",
    name="rl2",
    pv_y="m25",
    pv_x="m26",
    pv_yaw="m27",
    pv_pitch="m28",
    pv_lens1="m15",
    pv_lens2="m16",
    pv_lens3="m17",
    pv_lens4="m18",
    pv_lens5="m19",
    pv_lens6="m20",
    pv_lens7="m21",
    pv_lens8="m22",
    pv_lens9="m23",
    pv_lens10="m24",
)
