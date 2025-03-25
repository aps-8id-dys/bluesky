"""
BD-5a Device in station 8-ID-D
"""

__all__ = """
    bd5a
""".split()


import logging

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.info(__file__)


class BD5A(Device):
    def __init__(
        self,
        prefix: str,
        h_base_motor: str,
        v_base_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._h_base_motor = h_base_motor
        self._v_base_motor = v_base_motor

        super().__init__(prefix, *args, **kwargs)

    # Real motors that directly control the slits
    h = FCpt(EpicsMotor, "{motor_prefix}:{_h_base_motor}", labels={"motors"})
    v = FCpt(EpicsMotor, "{motor_prefix}:{_v_base_motor}", labels={"motors"})


bd5a = BD5A(
    name="bd5a", prefix="8iddSoft:CR8-D1:US", h_base_motor="m9", v_base_motor="m10"
)
