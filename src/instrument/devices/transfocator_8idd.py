"""
RL1: Transfocator (compound refractive lens, CRL) in 8-ID-D

.. note:: POLAR instrument has some related functions (`transfocator.py`).
    https://github.com/APS-4ID-POLAR/polar_instrument/pull/7/files
"""

__all__ = """
    rl1
""".split()

import logging

from ophyd import Component
from ophyd import EpicsMotor
from ophyd import MotorBundle

logger = logging.getLogger(__name__)
logger.info(__file__)


class Transfocator(MotorBundle):
    y = Component(EpicsMotor, "m1")
    x = Component(EpicsMotor, "m2")
    yaw = Component(EpicsMotor, "m3")
    pitch = Component(EpicsMotor, "m4")

    lens1 = Component(EpicsMotor, "m5")
    lens2 = Component(EpicsMotor, "m6")
    lens3 = Component(EpicsMotor, "m7")
    lens4 = Component(EpicsMotor, "m8")
    lens5 = Component(EpicsMotor, "m9")
    lens6 = Component(EpicsMotor, "m10")
    lens7 = Component(EpicsMotor, "m11")
    lens8 = Component(EpicsMotor, "m12")
    lens9 = Component(EpicsMotor, "m13")
    lens10 = Component(EpicsMotor, "m14")


rl1 = Transfocator("8iddSoft:TRANS:", name="rl1")
