"""
FL Devices
"""

__all__ = """
    fl2
    fl3
""".split()


import logging

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.info(__file__)


# Real motors that directly control the slits
fl2 = FCpt(EpicsMotor, "8ideSoft:CR8-E2:m7", labels={"motors"})
fl3 = FCpt(EpicsMotor, "8idiSoft:CR8-I2:m7", labels={"motors"})
