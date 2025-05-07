"""LabJack LJT705 in 8-ID-I."""

import logging

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

class FastShutter(Device):
    operation = Component(EpicsSignal, "State")
    logic = Component(EpicsSignal, "Lock")


# shutter_8ide = FastShutter("8ideSoft:fastshutter:", name="shutter_8ide")

