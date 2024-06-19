"""
IDT Mono in station 8-ID-A
"""

__all__ = """
    idt_mono
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)


from ophyd import Device, EpicsMotor
from ophyd import FormattedComponent as FCpt


class IDTMono(Device):
    def __init__(
        self,
        prefix: str,
        bragg_motor: str,
        xtal_gap_motor: str,
        flag_motor: str,
        coarse_pitch_motor: str,
        coarse_roll_motor: str,
        x_pitch_motor: str,
        y_pitch_motor: str,
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._bragg_motor = bragg_motor
        self._xtal_gap_motor = xtal_gap_motor
        self._flag_motor = flag_motor
        self._coarse_pitch_motor = coarse_pitch_motor
        self._coarse_roll_motor = coarse_roll_motor
        self._x_pitch_motor = x_pitch_motor
        self._y_pitch_motor = y_pitch_motor

        super().__init__(prefix, *args, **kwargs)

    bragg = FCpt(EpicsMotor, "{motor_prefix}:{_bragg_motor}", labels={"motors"})
    xtal_gap = FCpt(EpicsMotor, "{motor_prefix}:{_xtal_gap_motor}", labels={"motors"})
    flag = FCpt(EpicsMotor, "{motor_prefix}:{_flag_motor}", labels={"motors"})
    coarse_pitch = FCpt(
        EpicsMotor, "{motor_prefix}:{_coarse_pitch_motor}", labels={"motors"}
    )
    coarse_roll = FCpt(
        EpicsMotor, "{motor_prefix}:{_coarse_roll_motor}", labels={"motors"}
    )
    x_pitch = FCpt(EpicsMotor, "{motor_prefix}:{_x_pitch_motor}", labels={"motors"})
    y_pitch = FCpt(EpicsMotor, "{motor_prefix}:{_y_pitch_motor}", labels={"motors"})


idt_mono = IDTMono(
    name="idt_mono",
    prefix="8idaSoft:MONO:US",
    bragg_motor="m1",
    xtal_gap_motor="m2",
    flag_motor="m3",
    coarse_pitch_motor="m5",
    coarse_roll_motor="m6",
    x_pitch_motor="m7",
    y_pitch_motor="m8",
)
