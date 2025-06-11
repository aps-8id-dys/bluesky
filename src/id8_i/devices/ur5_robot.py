"""Monochromator device configuration for 8ID beamline.

This module defines the monochromator device which provides read-only access to the
monochromator energy readback.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class UR5_Pipette(Device):
    """Device representing the monochromator.

    This device provides read-only access to the monochromator energy readback value.
    """

    step_1 = Component(EpicsSignal, "Run.PROC", name="step_1")
    step_2 = Component(EpicsSignal, "Run.DISP", name="step_2")
