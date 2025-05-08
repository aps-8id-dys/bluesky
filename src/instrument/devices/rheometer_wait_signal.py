"""
Softglue counter. Increments when the MCR rheometer finishes current program.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignalRO


class Rheometer_Wait(Device):
    pulse_count = Component(EpicsSignalRO, "UpCntr-1_COUNTS")


mcr_wait_signal = Rheometer_Wait("8idMZ4:SG:", name="mcr_wait_signal")
