"""
SAXS Flight Tube
"""

__all__ = """
    bs_motors
    det_motors
""".split()


import logging

from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor

logger = logging.getLogger(__name__)
logger.info(__file__)


class FlightTubeDetector(Device):
    z = Component(EpicsMotor, "m1")
    tth = Component(EpicsMotor, "m2")


class FlightTubeBeamStop(Device):
    ds_x = Component(EpicsMotor, "m5")
    ds_y = Component(EpicsMotor, "m6")
    us = Component(EpicsMotor, "m7")


det_motors = FlightTubeDetector("8idiSoft:FLIGHT:", name="det_motors")
bs_motors = FlightTubeBeamStop("8idiSoft:FLIGHT:", name="bs_motors")
