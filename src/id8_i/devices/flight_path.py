from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor


class FlightPath(Device):
    length = Component(EpicsMotor, "m1", name="length")
