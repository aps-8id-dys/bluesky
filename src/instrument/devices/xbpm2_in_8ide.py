"""
XBPM2: X-ray beam position monitor in 8-ID-E for use in I station
"""

__all__ = """
    xbpm2
""".split()

import logging

from ophyd import Component
from ophyd import QuadEM
from ophyd.areadetector import ImagePlugin
from ophyd.areadetector import StatsPlugin

logger = logging.getLogger(__name__)
logger.info(__file__)


class MyImagePlugin(ImagePlugin):
    pool_max_buffers = None


class MyStatsPlugin(StatsPlugin):
    pool_max_buffers = None


class MyXBPM2(QuadEM):
    """Only change the AD plugins which don't have pool_max_buffers."""

    current1 = Component(MyStatsPlugin, "Current1:")
    current2 = Component(MyStatsPlugin, "Current2:")
    current3 = Component(MyStatsPlugin, "Current3:")
    current4 = Component(MyStatsPlugin, "Current4:")
    image = Component(MyImagePlugin, "image1:")
    sum_all = Component(MyStatsPlugin, "SumAll:")


xbpm2 = MyXBPM2("8idiSoft:T4U_BPM:", name="xbpm2")
