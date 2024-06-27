"""
Slit 4 in station 8-ID-D
"""

__all__ = """
    sl4
""".split()

import logging

from ophyd import Device, EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.info(__file__)


class Slit6(Device):
    def __init__(
        self,
        prefix: str,
        v_neg_motor: str,
        v_pos_motor: str,
        h_neg_motor: str,
        h_pos_motor: str,
        h_base_motor: str,
        v_base_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._v_neg_motor = v_neg_motor
        self._v_pos_motor = v_pos_motor

        self._h_neg_motor = h_neg_motor
        self._h_pos_motor = h_pos_motor

        self._h_base_motor = h_base_motor
        self._v_base_motor = v_base_motor

        super().__init__(prefix, *args, **kwargs)

    v_neg = FCpt(EpicsMotor, "{motor_prefix}:{_v_neg_motor}", labels={"motors"})
    v_pos = FCpt(EpicsMotor, "{motor_prefix}:{_v_pos_motor}", labels={"motors"})
    h_neg = FCpt(EpicsMotor, "{motor_prefix}:{_h_neg_motor}", labels={"motors"})
    h_pos = FCpt(EpicsMotor, "{motor_prefix}:{_h_pos_motor}", labels={"motors"})
    h_base = FCpt(EpicsMotor, "{motor_prefix}:{_h_base_motor}", labels={"motors"})
    v_base = FCpt(EpicsMotor, "{motor_prefix}:{_v_base_motor}", labels={"motors"})


sl4 = Slit6(
    name="sl4",
    prefix="8iddSoft:CR8-D1:US",
    v_neg_motor="m11",
    v_pos_motor="m12",
    h_neg_motor="m13",
    h_pos_motor="m14",
    h_base_motor="m15",
    v_base_motor="m16",
)
