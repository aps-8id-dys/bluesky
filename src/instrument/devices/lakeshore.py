"""
Lakeshore 336 (temperature readout only)
"""

from ophyd import Device, Component, EpicsSignalRO

class Lakeshore(Device):
    readback_ch1 = Component(EpicsSignalRO, "IN1")
    readback_ch2 = Component(EpicsSignalRO, "IN2")
    readback_ch3 = Component(EpicsSignalRO, "IN3")
    readback_ch4 = Component(EpicsSignalRO, "IN4")

lakeshore1 = Lakeshore("8ideSoft:LS336:1:", name="lakeshore1")
lakeshore2 = Lakeshore("8ideSoft:LS336:2:", name="lakeshore2")

