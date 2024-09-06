"""
Caen picoammeter - TetraAMM

GitHub apstools issue #878 has some useful documentation in the comments.

.. see:: https://github.com/BCDA-APS/apstools/issues/878
"""

__all__ = """
    tetramm
""".split()

import logging

from ophyd import Component
from ophyd import TetrAMM
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
from ophyd.quadem import QuadEMPort

logger = logging.getLogger(__name__)
logger.info(__file__)


class MyTetrAMM(TetrAMM):
    """Caen picoammeter - TetraAMM."""

    conf = Component(QuadEMPort, port_name="QUAD1")

    current1 = Component(StatsPlugin_V34, "Current1:")
    current2 = Component(StatsPlugin_V34, "Current2:")
    current3 = Component(StatsPlugin_V34, "Current3:")
    current4 = Component(StatsPlugin_V34, "Current4:")
    image = Component(ImagePlugin_V34, "image1:")
    sum_all = Component(StatsPlugin_V34, "SumAll:")


try:
    tetramm = MyTetrAMM("8idTetra:QUAD1:", name="tetramm")
    tetramm.wait_for_connection()
except Exception as cause:
    logger.warning(f"Could not create tetramm: {cause}")
    tetramm = None
