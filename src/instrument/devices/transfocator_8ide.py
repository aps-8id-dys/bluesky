"""
RL2: Transfocator (compound refractive lens, CRL) in 8-ID-E

.. note:: POLAR instrument has some related functions (`transfocator.py`).
    https://github.com/APS-4ID-POLAR/polar_instrument/pull/7/files
"""

__all__ = """
    rl2
""".split()

import logging

from ophyd import Component
from ophyd import EpicsMotor
from ophyd import MotorBundle

logger = logging.getLogger(__name__)
logger.info(__file__)


class Transfocator(MotorBundle):
    y = Component(EpicsMotor, "m25")
    x = Component(EpicsMotor, "m26")
    yaw = Component(EpicsMotor, "m27")
    pitch = Component(EpicsMotor, "m28")

    lens1 = Component(EpicsMotor, "m15")
    lens2 = Component(EpicsMotor, "m16")
    lens3 = Component(EpicsMotor, "m17")
    lens4 = Component(EpicsMotor, "m18")
    lens5 = Component(EpicsMotor, "m19")
    lens6 = Component(EpicsMotor, "m20")
    lens7 = Component(EpicsMotor, "m21")
    lens8 = Component(EpicsMotor, "m22")
    lens9 = Component(EpicsMotor, "m23")
    lens10 = Component(EpicsMotor, "m24")


rl2 = Transfocator("8iddSoft:TRANS:", name="rl2")
