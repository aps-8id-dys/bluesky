"""
IDT Mono in station 8-ID-A
"""

__all__ = """
    idt_mono
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)


from ophyd import Device
from ophyd import FormattedComponent as FCpt
from ophyd import EpicsMotor


class IDTMono(Device):

    def __init__(
        self,
        prefix: str,
        bragg: str,
        xal_gap: str,
        flag: str,
        coarse_pitch: str,
        coarse_roll: str,
        
        *args,
        **kwargs,
    ):
        # Determine the prefix for the motors
        pieces = prefix.strip(":").split(":")
        self.motor_prefix = ":".join(pieces[:-1])

        self._bragg = bragg
        self.xal_gap = xal_gap
        self._flag = flag
        self._coarse_pitch = coarse_pitch

        super().__init__(prefix, *args, **kwargs)

    bragg = FCpt(EpicsMotor, "{motor_prefix}:{_bragg_motor}", labels={"motors"})
    xal_gap = FCpt(EpicsMotor, "{motor_prefix}:{_xal_gap}", labels={"motors"})
    flag = FCpt(EpicsMotor, "{motor_prefix}:{_flag}", labels={"motors"})
    coarse_pitch = FCpt(EpicsMotor, "{motor_prefix}:{_coarse_pitch}", labels={"motors"})

idt_mono = IDTMono(name="mono_slit", prefix="8idaSoft:MONO:US", bragg="m1", xal_gap="m2", flag="m3", coarse_pitch="m5")