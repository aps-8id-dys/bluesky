"""
Win Devices at 8 ID
"""

__all__ = """
    win_e
    win_i
""".split()


import logging

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.info(__file__)


class Win(Device):
    def __init__(
        self,
        prefix: str,
        x_motor: str,
        y_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._x_motor = x_motor
        self._y_motor = y_motor

        super().__init__(prefix, *args, **kwargs)

    # Real motors that directly control the slits
    x = FCpt(EpicsMotor, "{motor_prefix}:{_x_motor}", labels={"motors"})
    y = FCpt(EpicsMotor, "{motor_prefix}:{_y_motor}", labels={"motors"})


win_e = Win(name="win_e", prefix="8ide:US", x_motor="m13", y_motor="m12")
win_i = Win(name="win_i", prefix="8ide:US", x_motor="m23", y_motor="m24")
