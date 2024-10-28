"""LabJack LJT705 in 8-ID-I."""

from ophyd import Component, Device, EpicsSignal


class LabJack(Device):
    operation = Component(EpicsSignal, "Bo0")
    logic = Component(EpicsSignal, "Bo1")


labjack = LabJack("8idiSoft:LJT705:", name="labjack")
