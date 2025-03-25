"""
Filters.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO


class Filter2Device(Device):
    """For 8-ID-E and I station"""

    atten_index = Component(EpicsSignal, "sortedIndex")
    attenuation_set = Component(EpicsSignal, "attenuation")
    attenuation_readback = Component(EpicsSignalRO, "attenuation_actual")
    transmission_set = Component(EpicsSignal, "transmission")
    transmission_readback = Component(EpicsSignal, "transmission_RBV")


filter_8ide = Filter2Device("8idPyFilter:FL2:", name="filter_8ide")
filter_8idi = Filter2Device("8idPyFilter:FL3:", name="filter_8idi")
