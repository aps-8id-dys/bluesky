"""
Individual slits of JJ slit
"""

import logging

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.info(__file__)


class IndividualSlits(Device):
    """
    Individual Slits to move
    """

    def __init__(
        self,
        prefix: str,
        h_positive_motor: str,
        h_negative_motor: str,
        v_positive_motor: str,
        v_negative_motor: str,
        *args,
        **kwargs,
    ):
        """
        Initializing the prefix and correct suffix format
        """
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._h_positive_motor = h_positive_motor
        self._h_negative_motor = h_negative_motor
        self._v_positive_motor = v_positive_motor
        self._v_negative_motor = v_negative_motor

        super().__init__(prefix, *args, **kwargs)

    # Real motors that directly control the slits
    hp = FCpt(EpicsMotor, "{motor_prefix}:{_h_positive_motor}", labels={"motors"})
    hn = FCpt(EpicsMotor, "{motor_prefix}:{_h_negative_motor}", labels={"motors"})
    vp = FCpt(EpicsMotor, "{motor_prefix}:{_v_positive_motor}", labels={"motors"})
    vn = FCpt(EpicsMotor, "{motor_prefix}:{_v_negative_motor}", labels={"motors"})


i_sl9 = IndividualSlits(
    prefix="8idiSoft:CR8-I2:US",
    h_positive_motor="m12",
    h_negative_motor="m11",
    v_positive_motor="m10",
    v_negative_motor="m9",
    name="i_sl9",
)

i_sl5 = IndividualSlits(
    prefix="8ideSoft:CR8-E2:US",
    h_positive_motor="m4",
    h_negative_motor="m3",
    v_positive_motor="m2",
    v_negative_motor="m1",
    name="i_sl5",
)
