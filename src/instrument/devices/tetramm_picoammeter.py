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
from ophyd.areadetector import ImagePlugin
from ophyd.areadetector import StatsPlugin

logger = logging.getLogger(__name__)
logger.info(__file__)


class MyImagePlugin(ImagePlugin):
    pool_max_buffers = None


class MyStatsPlugin(StatsPlugin):
    pool_max_buffers = None


class MyTetrAMM(TetrAMM):
    """Only change the AD plugins which don't have pool_max_buffers."""

    current1 = Component(MyStatsPlugin, "Current1:")
    current2 = Component(MyStatsPlugin, "Current2:")
    current3 = Component(MyStatsPlugin, "Current3:")
    current4 = Component(MyStatsPlugin, "Current4:")
    image = Component(MyImagePlugin, "image1:")
    sum_all = Component(MyStatsPlugin, "SumAll:")


tetramm = MyTetrAMM("8idTetra:QUAD1:", name="tetramm")
tetramm.wait_for_connection()
