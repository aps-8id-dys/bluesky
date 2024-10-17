"""
Slit Devices at 8-ID
"""

__all__ = """
    sl5
    sl9
""".split()

import logging

from apstools.devices.positioner_soft_done import PVPositionerSoftDone
from ophyd import EpicsMotor
from ophyd import FormattedComponent as FCpt
from ophyd import Component as Cpt
from apstools.synApps.db_2slit import Optics2Slit1D
from apstools.synApps.db_2slit import Optics2Slit2D_HV
from ophyd import Component as cpt
from ophyd import EpicsSignal

logger = logging.getLogger(__name__)
logger.info(__file__)


class ID8Optics2Slit1D(Optics2Slit1D):
    # Define formatted components at the class level using placeholders
    def __init__(
        self,
        prefix: str,
        secondary_prefix: str,
        positive_motor: str,
        negative_motor: str,
        *args,
        **kwargs,
    ):
        # Store motor names and secondary prefix as instance variables
        self.secondary_prefix = secondary_prefix
        print(self.secondary_prefix)
        self.positive_motor = positive_motor
        self.negative_motor = negative_motor

        # Call the parent constructor
        super().__init__(prefix, *args, **kwargs)

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
    p = FCpt(EpicsMotor, "{secondary_prefix}:{positive_motor}", labels={"motors"})
    n = FCpt(EpicsMotor, "{secondary_prefix}:{negative_motor}", labels={"motors"})


class ID8Optics2Slit2D_HV(Optics2Slit2D_HV):
    # Use FCpt to delay the initialization until after the instance is created
    h = FCpt(
        ID8Optics2Slit1D,
        "{prefix}H",  # H gets appended to the prefix
        secondary_prefix="{_secondary_prefix}",
        positive_motor="{_h_positive_motor}",
        negative_motor="{_h_negative_motor}",
    )

    v = FCpt(
        ID8Optics2Slit1D,
        "{prefix}V",  # V gets appended to the prefix
        secondary_prefix="{_secondary_prefix}",
        positive_motor="{_v_positive_motor}",
        negative_motor="{_v_negative_motor}",
    )

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
        # Store the motor names and secondary prefix as instance variables
        self._secondary_prefix = secondary_prefix
        self._h_positive_motor = h_positive_motor
        self._h_negative_motor = h_negative_motor
        self._v_positive_motor = v_positive_motor
        self._v_negative_motor = v_negative_motor
        
        # Print inside __init__
        print(f"outer: {self._secondary_prefix}\n\n\n\n\n")
        
        # Call the parent constructor
        super().__init__(prefix, *args, **kwargs)
        print("after init")

# Example of usage
sl5 = ID8Optics2Slit2D_HV(
    prefix="8ideSoft:Slit1",
    secondary_prefix="8idiSoft:CR8-E2",
    h_positive_motor="m4",
    h_negative_motor="m3",
    v_positive_motor="m2",
    v_negative_motor="m1",
    name="sl5",
)

sl9 = ID8Optics2Slit2D_HV(
    prefix="8idiSoft:Slit2",
    secondary_prefix="8ideSoft:CR8-I2:",
    h_positive_motor="m12",
    h_negative_motor="m11",
    v_positive_motor="m10",
    v_negative_motor="m9",
    name="sl9",
)
