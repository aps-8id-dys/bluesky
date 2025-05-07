"""
Slit Base Devices at 8-ID
"""

from ophyd import Device
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt


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
