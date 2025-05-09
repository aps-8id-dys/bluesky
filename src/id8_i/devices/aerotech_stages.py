"""
Aerotech motorized stages.

Plan these demonstrations:

Motivation: Move sample during measurement to avoid beam damage.

1. step scan Eiger4M v. sample.x
1. fly scan Eiger4M v. sample.x
  1. start motor moving
  2. start Eiger4M with one acquisition of n frames
  3. Eiger4M completes acquisition
  4. motor stops
1. fly scan Eiger4M v. sample.x and run DM workflow
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor


class AerotechSampleStage(Device):
    x = Component(EpicsMotor, "m1", labels=("sample", "motor"))
    y = Component(EpicsMotor, "m3", labels=("sample", "motor"))
    z = Component(EpicsMotor, "m2", labels=("sample", "motor"))
    # different IOC!! "8ide:"
    roll = Component(EpicsMotor, prefix="8ide:m15", labels=("sample", "motor"))
    pitch = Component(EpicsMotor, prefix="8ide:m14", labels=("sample", "motor"))
    yaw = Component(EpicsMotor, prefix="8ide:m16", labels=("sample", "motor"))


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


# try:
#     sample = AerotechSampleStage(IOC, name="sample", labels=("sample", "stage"))
#     detector = AerotechDetectorStage(IOC, name="detector", labels=("detector", "stage"))
#     rheometer = AerotechRheometerStage(
#         IOC, name="rheometer", labels=("rheometer", "stage")
#     )
# except Exception as exinfo:
#     logger.warning("Could not connect with Aerotech controller. %s", exinfo)
#     sample = None
#     detector = None
#     rheometer = None
