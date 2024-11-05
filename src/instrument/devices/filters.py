"""
Filters.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class Filter2Device(Device):
    """For 8-ID-E station.  (see scripts/user/filter_op.py)"""

    attenuation = Component(EpicsSignal, "attenuation", read_pv="attenuation_actual")

    # simple v. elegant - simple wins
    filter01_enable = Component(EpicsSignal, "filter01_Enable")
    filter02_enable = Component(EpicsSignal, "filter02_Enable")
    filter03_enable = Component(EpicsSignal, "filter03_Enable")
    filter04_enable = Component(EpicsSignal, "filter04_Enable")
    filter05_enable = Component(EpicsSignal, "filter05_Enable")
    filter06_enable = Component(EpicsSignal, "filter06_Enable")
    filter07_enable = Component(EpicsSignal, "filter07_Enable")
    filter08_enable = Component(EpicsSignal, "filter08_Enable")
    filter09_enable = Component(EpicsSignal, "filter09_Enable")
    filter10_enable = Component(EpicsSignal, "filter10_Enable")
    filter11_enable = Component(EpicsSignal, "filter11_Enable")
    filter12_enable = Component(EpicsSignal, "filter12_Enable")

    def filter_enable_signal(self, blade_num):
        """
        Return the indexed sample position register signal.

        Replaces: PyEpics calls involving FILTER_PV_PREFIX + f"filter{blade_num:02d}" + "_Enable"
        """
        return getattr(self, f"filter{blade_num:02d}_enable")


filter2 = Filter2Device("8idPyFilter:FL2:", name="filter2")

# TODO: Is FL3 similar to FL2?
filter3 = EpicsSignal("8idPyFilter:FL3:sortedIndex", name="filter3")
