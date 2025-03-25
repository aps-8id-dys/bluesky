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
from apstools.synApps.db_2slit import Optics2Slit1D
from apstools.synApps.db_2slit import Optics2Slit2D_HV
from ophyd import Component as cpt
from ophyd import EpicsSignal

logger = logging.getLogger(__name__)
logger.info(__file__)


class ID8Optics2Slit1D(Optics2Slit1D):
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
        tolerance=2e-3,
    )
    center = cpt(
        PVPositionerSoftDone,
        "center",
        setpoint_pv=".VAL",
        readback_pv=".RBV",
        tolerance=8e-4,
    )
    sync = cpt(EpicsSignal, "doSync", put_complete=True, kind="omitted")


class ID8Optics2Slit2D_HV(Optics2Slit2D_HV):
    h = cpt(ID8Optics2Slit1D, "H")
    v = cpt(ID8Optics2Slit1D, "V")


sl4 = ID8Optics2Slit2D_HV("8iddSoft:Slit1", name="sl4")
sl5 = ID8Optics2Slit2D_HV("8ideSoft:Slit1", name="sl5")
sl7 = ID8Optics2Slit2D_HV("8ideSoft:Slit2", name="sl7")
sl8 = ID8Optics2Slit2D_HV("8idiSoft:Slit1", name="sl8")
sl9 = ID8Optics2Slit2D_HV("8idiSoft:Slit2", name="sl9")
