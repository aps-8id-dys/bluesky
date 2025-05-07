"""
Damm (dynamic aperture) in station 8-ID-D
"""

import logging

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


class XY_Motors(Device):
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


# damm = Damm(name="damm", prefix="8iddSoft:CR8-D1:US", x_motor="m2", y_motor="m3")
