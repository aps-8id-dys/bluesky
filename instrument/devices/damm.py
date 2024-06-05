
"""
HHL Slits in station 8-ID-A
"""

__all__ = """
    damm
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

# from apstools.devices.hhl_slits import HHLSlits

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import FormattedComponent as FCpt
from ophyd import EpicsMotor


class Slit2(Device):

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
    pitch = FCpt(EpicsMotor, "{motor_prefix}:{_h_motor}", labels={"motors"})
    yaw = FCpt(EpicsMotor, "{motor_prefix}:{_v_motor}", labels={"motors"})

damm = Slit2(name="damm", prefix="8iddSoft:CR8-D1:US", h_motor="m2", v_motor="m3")