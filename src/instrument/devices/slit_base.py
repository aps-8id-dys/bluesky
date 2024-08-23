"""
Slit Base Devices at 8-ID
"""

__all__ = """
    sl4_base
    sl5_base
    sl7_base
    sl8_base
    sl9_base
""".split()


import logging

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt

logger = logging.getLogger(__name__)
logger.info(__file__)


class SlitBase(Device):
    def __init__(
        self,
        prefix: str,
        h_motor: str,
        v_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._h_motor = h_motor
        self._v_motor = v_motor

        super().__init__(prefix, *args, **kwargs)

    # Real motors that directly control the slits
    h = FCpt(EpicsMotor, "{motor_prefix}:{_h_motor}", labels={"motors"})
    v = FCpt(EpicsMotor, "{motor_prefix}:{_v_motor}", labels={"motors"})


sl4_base = SlitBase(
    name="SL 4 Base", prefix="8iddSoft:CR8-D1:US", h_motor="m15", v_motor="m16"
)
sl5_base = SlitBase(
    name="SL 5 Base", prefix="8ideSoft:CR8-E2:US", h_motor="m5", v_motor="m6"
)
sl7_base = SlitBase(
    name="SL 7 Base", prefix="8ideSoft:CR8-E2:US", h_motor="m15", v_motor="m16"
)
sl8_base = SlitBase(
    name="SL 8 Base", prefix="8idiSoft:CR8-I2:US", h_motor="m5", v_motor="m6"
)
sl9_base = SlitBase(
    name="SL 9 Base", prefix="8idiSoft:CR8-I2:US", h_motor="m15", v_motor="m16"
)
