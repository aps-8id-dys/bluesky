"""
Slit Devices at 8-ID
"""

__all__ = """
    sl4
    sl5
    sl7
    sl8
    sl9
""".split()

import logging

from apstools.devices.positioner_soft_done import PVPositionerSoftDone
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt
from apstools.synApps.db_2slit import Optics2Slit1D
from apstools.synApps.db_2slit import Optics2Slit2D_HV
from ophyd import Component as cpt
from ophyd import EpicsSignal

logger = logging.getLogger(__name__)
logger.info(__file__)


class ID8Optics2Slit1D(Optics2Slit1D):

    def __init__(
        self,
        prefix: str,
        secondary_prefix: str,
        positive_motor: str,
        negative_motor: str,
        *args,
        **kwargs,
    ):

    xn = cpt(
        PVPositionerSoftDone,
        "xn",
        setpoint_pv=".VAL",
        readback_pv=".RBV",
        tolerance=8e-4,
    )
    xp = cpt(
        PVPositionerSoftDone,
        "xp",
        setpoint_pv=".VAL",
        readback_pv=".RBV",
        tolerance=8e-4,
    )
    size = cpt(
        PVPositionerSoftDone,
        "size",
        setpoint_pv=".VAL",
        readback_pv=".RBV",
        tolerance=8e-4,
    )
    center = cpt(
        PVPositionerSoftDone,
        "center",
        setpoint_pv=".VAL",
        readback_pv=".RBV",
        tolerance=8e-4,
    )
    sync = cpt(EpicsSignal, "doSync", put_complete=True, kind="omitted")

    p = FCpt(EpicsMotor, "{secondary_motor_prefix}:{positive_motor}", labels={"motors"})
    n = FCpt(EpicsMotor, "{secondary_motor_prefix}:{negative_motor}", labels={"motors"})



# class ID8Optics2Slit2D_HV(Optics2Slit2D_HV):
#     def __init__(
#         self,
#         prefix: str,
#         secondary_prefix: str,
#         h_positive_motor: str,
#         h_negative_motor: str,
#         v_positive_motor: str,
#         v_negative_motor: str,
#         *args,
#         **kwargs,
#     ):
#     print("help me I'm stuck \n\n\n\n")
#     h = FCpt(
#         ID8Optics2Slit1D,
#         prefix,
#         secondary_prefix="{secondary_prefix}",
#         positive_motor="{h_positive_motor}",
#         negative_motor="{h_negative_motor}"
#     )

class ID8Optics2Slit2D_HV(Optics2Slit2D_HV):
    def __init__(
        self,
        prefix: str,
        secondary_prefix: str,
        h_positive_motor: str,
        h_negative_motor: str,
        v_positive_motor: str,
        v_negative_motor: str,
        *args,
        **kwargs,
    ):
        super().__init__(prefix, *args, **kwargs)
        
        # Initialize class with provided motor arguments
        self.h_positive_motor = h_positive_motor
        self.h_negative_motor = h_negative_motor
        self.v_positive_motor = v_positive_motor
        self.v_negative_motor = v_negative_motor

    # Horizontal and vertical slits components, passing motor names dynamically
    h = FCpt(
        ID8Optics2Slit1D,
        "{prefix}",
        secondary_prefix="{secondary_prefix}",
        positive_motor="{h_positive_motor}",
        negative_motor="{h_negative_motor}"
    )
    
    v = FCpt(
        ID8Optics2Slit1D,
        "{prefix}",
        secondary_prefix="{secondary_prefix}",
        positive_motor="{v_positive_motor}",
        negative_motor="{v_negative_motor}"
    )



# sl4 = ID8Optics2Slit2D_HV("8iddSoft:Slit1", name="sl4")
sl5 = ID8Optics2Slit2D_HV(prefix = "8ideSoft:Slit1", secondary_prefix = "8idiSoft:CR8-E2", h_positive_motor = "m4", h_negative_motor = "m3", v_positive_motor = "m2", v_negative_motor = "m1", ,name="sl5")
# sl7 = ID8Optics2Slit2D_HV("8ideSoft:Slit2", name="sl7")
# sl8 = ID8Optics2Slit2D_HV("8idiSoft:Slit1", name="sl8")
sl9 = ID8Optics2Slit2D_HV(prefix = "8idiSoft:Slit2", secondary_prefix = "8ideSoft:CR8-I2", h_positive_motor = "m12", h_negative_motor = "m11", v_positive_motor = "m10", v_negative_motor = "m9", name="sl9")
