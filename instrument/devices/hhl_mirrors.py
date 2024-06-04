"""
High-heat load mirrors in station 8-ID-A.
"""

__all__ = """
    mr1
    mr2
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


class HHL_Mirror1(Device):

    x = Component(EpicsMotor, "FMBO:m4")
    y = Component(EpicsMotor, "FMBO:m2")
    coarse_pitch = Component(EpicsMotor, "FMBO:m6")
    fine_pitch = Component(EpicsMotor, "FMBO:Piezo:m1")
    flag = Component(EpicsMotor, "CR8-A1:m5")


class HHL_Mirror2(Device):

    x = Component(EpicsMotor, "FMBO:m3")
    y = Component(EpicsMotor, "FMBO:m1")
    coarse_pitch = Component(EpicsMotor, "FMBO:m5")
    fine_pitch = Component(EpicsMotor, "FMBO:Piezo:m2")
    flag = Component(EpicsMotor, "CR8-A1:m6")
    bender1 = Component(EpicsMotor, "FMBO:m7")
    bender2 = Component(EpicsMotor, "FMBO:m8")


mr1 = HHL_Mirror1("8idaSoft:", name="mr1")
mr2 = HHL_Mirror2("8idaSoft:", name="mr2")
