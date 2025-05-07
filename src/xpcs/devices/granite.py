"""
granite 1 DOF Motor
"""

import logging

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.bsdev(__file__)


class granite_device(Device):
    def __init__(
        self,
        prefix: str,
        x_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._x_neg_motor = x_motor

        super().__init__(prefix, *args, **kwargs)

    x = FCpt(EpicsMotor, "{motor_prefix}:{_x_neg_motor}", labels={"motors"})


# granite = granite_device(
#     name="granite",
#     prefix="8idiSoft:CR8-I2:US",
#     x_motor="m8",
# )
