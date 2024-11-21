"""
Filters.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class Filter2Device(Device):
    """For 8-ID-E and I station"""

    atten_index = Component(EpicsSignal, "sortedIndex")
    attenuation = Component(EpicsSignal, "attenuation")
    transmission = Component(EpicsSignal, "transmission")


filter_8ide = Filter2Device("8idPyFilter:FL2:", name="filter_8ide")
filter_8idi = Filter2Device("8idPyFilter:FL3:", name="filter_8idi")
