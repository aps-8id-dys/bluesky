"""LabJack LJT705 in 8-ID-I."""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class LabJack(Device):
    """A device class for controlling LabJack data acquisition devices.

    This class provides control over LabJack devices used for data acquisition
    and control in the beamline. It includes functionality for analog and
    digital I/O, counter inputs, and device configuration.
    """

    operation = Component(EpicsSignal, "Bo0")
    logic = Component(EpicsSignal, "Bo1")
