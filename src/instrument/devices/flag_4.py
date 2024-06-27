"""
Flag 4 in station 8-ID-D
"""

__all__ = """
    fl4
""".split()


import logging

from ophyd import Device, EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.info(__file__)


class Flag4(Device):
    def __init__(
        self,
        prefix: str,
        flag_4_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._flag_4_motor = flag_4_motor

        super().__init__(prefix, *args, **kwargs)

    flag_4 = FCpt(EpicsMotor, "{motor_prefix}:{_flag_4_motor}", labels={"motors"})


fl4 = Flag4(
    name="fl4",
    prefix="8iddSoft:CR8-D1:US",
    flag_4_motor="m1",
)
