"""
XBPM2: X-ray beam position monitor in 8-ID-E for use in I station
"""

__all__ = """
    bd6a
    xbpm2
""".split()

import logging

from ophyd import Component
from ophyd import EpicsMotor
from ophyd import EpicsSignalRO
from ophyd import MotorBundle
from ophyd import QuadEM
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
from ophyd.quadem import QuadEMPort

logger = logging.getLogger(__name__)
logger.info(__file__)


class BD6AMotors(MotorBundle):
    """Base motors for XBPM2."""

    h = Component(EpicsMotor, "m9", labels={"motor"})
    v = Component(EpicsMotor, "m10")


class MyXBPM2(QuadEM):
    """Revisions to ophyd class."""

    conf = Component(QuadEMPort, port_name="T4U_BPM")

    # latest versions of the AD plugins
    current1 = Component(StatsPlugin_V34, "Current1:")
    current2 = Component(StatsPlugin_V34, "Current2:")
    current3 = Component(StatsPlugin_V34, "Current3:")
    current4 = Component(StatsPlugin_V34, "Current4:")
    image = Component(ImagePlugin_V34, "image1:")
    sum_all = Component(StatsPlugin_V34, "SumAll:")

    # better as text than numbers
    firmware = Component(EpicsSignalRO, "Firmware", string=True, kind="config")
    model = Component(EpicsSignalRO, "Model", string=True, kind="config")


xbpm2 = MyXBPM2("8idiSoft:T4U_BPM:", name="xbpm2")
bd6a = BD6AMotors("8ideSoft:CR8-E2:", name="bd6a")
