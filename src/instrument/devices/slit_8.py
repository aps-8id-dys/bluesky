"""
Slit 8 in station 8-ID-I
"""

__all__ = """
    sl8
""".split()

import logging

from ophyd import Device
from ophyd import EpicsMotor
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


sl8 = Slit6(
    name="sl8",
    prefix="8idiSoft:CR8-I2:US",
    v_neg_motor="m1",
    v_pos_motor="m2",
    h_neg_motor="m4",
    h_pos_motor="m3",
    h_base_motor="m5",
    v_base_motor="m6",
)
