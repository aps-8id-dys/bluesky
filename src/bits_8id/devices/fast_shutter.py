"""LabJack LJT705 in 8-ID-I."""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class FastShutter(Device):
    operation = Component(EpicsSignal, "State")
    logic = Component(EpicsSignal, "Lock")


shutter_8ide = FastShutter("8ideSoft:fastshutter:", name="shutter_8ide")

