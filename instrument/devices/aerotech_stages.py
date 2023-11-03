"""
Aerotech motorized stages.
"""

__all__ = """
    sample
    detector
    rheometer
""".split()

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


IOC = "8idiAerotech:"

# TODO: refactor from labels to ophyd_registry?


class AerotechSampleStage(Device):
    x = Component(EpicsMotor, "m1", labels=("sample", "motor"))
    y = Component(EpicsMotor, "m3", labels=("sample", "motor"))
    z = Component(EpicsMotor, "m2", labels=("sample", "motor"))


class AerotechDetectorStage(Device):
    x = Component(EpicsMotor, "m4", labels=("detector", "motor"))
    y = Component(EpicsMotor, "m5", labels=("detector", "motor"))
    # TBA: z
    # TBA: yaw (rotation about y)


class AerotechRheometerStage(Device):
    x = Component(EpicsMotor, "m8", labels=("rheometer", "motor"))
    y = Component(EpicsMotor, "m9", labels=("rheometer", "motor"))
    z = Component(EpicsMotor, "m7", labels=("rheometer", "motor"))
    # TODO: Are these motors assigned correctly?
    roll = Component(EpicsMotor, "m10", labels=("rheometer", "motor"))
    pitch = Component(EpicsMotor, "m11", labels=("rheometer", "motor"))
    yaw = Component(EpicsMotor, "m12", labels=("rheometer", "motor"))


sample = AerotechSampleStage(IOC, name="sample", labels=("sample", "stage"))
detector = AerotechDetectorStage(IOC, name="detector", labels=("detector", "stage"))
rheometer = AerotechRheometerStage(IOC, name="rheometer", labels=("rheometer", "stage"))
