"""LabJack LJT705 in 8-ID-I."""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class LabJack(Device):
    operation = Component(EpicsSignal, "Bo0")
    logic = Component(EpicsSignal, "Bo1")

