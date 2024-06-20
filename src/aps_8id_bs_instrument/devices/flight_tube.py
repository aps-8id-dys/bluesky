"""
SAXS Flight Tube
"""

__all__ = """
    bs
    det
""".split()


import logging

from ophyd import Component, Device, EpicsMotor

logger = logging.getLogger(__name__)
logger.info(__file__)


class FlightTubeDetector(Device):
    z = Component(EpicsMotor, "m1")
    tth = Component(EpicsMotor, "m2")


class FlightTubeBeamStop(Device):
    ds_x = Component(EpicsMotor, "m5")
    ds_y = Component(EpicsMotor, "m6")
    us = Component(EpicsMotor, "m7")


det = FlightTubeDetector(
    "8idiFlight:", name="det"
)  # TODO: "Ensure variable name is as desired"
bs = FlightTubeBeamStop(
    "8idiFlight:", name="bs"
)  # TODO: "Ensure variable name is as desired"
