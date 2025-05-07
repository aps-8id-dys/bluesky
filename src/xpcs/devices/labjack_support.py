"""LabJack LJT705 in 8-ID-I."""

import logging

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

class LabJack(Device):
    operation = Component(EpicsSignal, "Bo0")
    logic = Component(EpicsSignal, "Bo1")


# labjack = LabJack("8idiSoft:LJT705:", name="labjack")
