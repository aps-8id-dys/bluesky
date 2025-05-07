"""
Filters.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO


class Filter2Device(Device):
    """For 8-ID-E and I station"""

    atten_index = Component(EpicsSignal, "sortedIndex")
    atten_index_readback = Component(EpicsSignal, "sortedIndex_RBV")
    attenuation_set = Component(EpicsSignal, "attenuation")
    attenuation_readback = Component(EpicsSignalRO, "attenuation_actual")
    transmission_set = Component(EpicsSignal, "transmission")
    transmission_readback = Component(EpicsSignal, "transmission_RBV")
