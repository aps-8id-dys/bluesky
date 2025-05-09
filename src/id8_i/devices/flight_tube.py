"""
SAXS Flight Tube
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor


class FlightTubeDetector(Device):
    z = Component(EpicsMotor, "m1")
    tth = Component(EpicsMotor, "m2")


class FlightTubeBeamStop(Device):
    ds_x = Component(EpicsMotor, "m5")
    ds_y = Component(EpicsMotor, "m6")
    us = Component(EpicsMotor, "m7")
