"""
HHL Slits in station 8-ID-A
"""

from __future__ import annotations

__all__ = """
    wb_slit
    mono_slit
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

# from apstools.devices.hhl_slits import HHLSlits

from ophyd import Device, EpicsMotor
from ophyd import FormattedComponent as FCpt


class HHLSlits(Device):
    """
    High Heat Load SHHLSlitst.

    There are no independent parts to move, so each axis only has center and size.

    Based on the 25-ID-A whitebeam slits.

    The motor parameters listed below specify which motor records
    control which axis. The last piece of the PV prefix will be
    removed, and the motor number added on. For example, if the prefix
    is "255ida:slits:US:", and the pitch motor is "255ida:slits:m3",
    then *pitch_motor* should be "m3".

    Parameters
    ==========
    prefix:
      EPICS prefix required to communicate with HHL Slit IOC, ex: "25ida:slits:US:"
    pitch_motor:
      The motor record suffix controlling the real pitch motor, ex "m3"
    yaw_motor:
      The motor record suffix controlling the real yaw motor, ex "m4"
    horizontal_motor:
      The motor record suffix controlling the real horizontal motor, ex: "m1"
    diagonal_motor:
      The motor record suffix controlling the real diagonal motor, ex: "m2"
    """

    def __init__(
        self,
        prefix: str,
        pitch_motor: str,
        yaw_motor: str,
        horizontal_motor: str,
        diagonal_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._pitch_motor = pitch_motor
        self._yaw_motor = yaw_motor
        self._horizontal_motor = horizontal_motor
        self._diagonal_motor = diagonal_motor

        super().__init__(prefix, *args, **kwargs)

    # class SlitAxis(Device):
    #     size = Cpt(EpicsMotor, "Size", labels={"motors"})
    #     center = Cpt(EpicsMotor, "Center", labels={"motors"})

    # # Individual slit directions
    # h = Cpt(SlitAxis, "h")
    # v = Cpt(SlitAxis, "v")

    # Real motors that directly control the slits
    pitch = FCpt(EpicsMotor, "{motor_prefix}:{_pitch_motor}", labels={"motors"})
    yaw = FCpt(EpicsMotor, "{motor_prefix}:{_yaw_motor}", labels={"motors"})
    horizontal = FCpt(
        EpicsMotor, "{motor_prefix}:{_horizontal_motor}", labels={"motors"}
    )
    diagonal = FCpt(EpicsMotor, "{motor_prefix}:{_diagonal_motor}", labels={"motors"})


wb_slit = HHLSlits(
    name="wb_slit",
    prefix="8idaSoft:CR8-A1:US",
    pitch_motor="m3",
    yaw_motor="m4",
    horizontal_motor="m1",
    diagonal_motor="m2",
)
mono_slit = HHLSlits(
    name="mono_slit",
    prefix="8idaSoft:CR8-A1:US",
    pitch_motor="m11",
    yaw_motor="m12",
    horizontal_motor="m9",
    diagonal_motor="m10",
)
