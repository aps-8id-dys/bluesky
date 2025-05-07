"""
Granite X Enable Signal.
"""

import logging

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

class Valve_Enable(Device):
    """For 8-ID-E and I station"""
    enable = Component(EpicsSignal, "bo3:9.VAL")

# granite_8idi_valve = Valve_Enable("8idiSoft:CR8-I2:", name="granite_8idi_valve")

