"""
Slit 7 in station 8-ID-E
"""

__all__ = """
    sl7
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
    xn = cpt(PVPositionerSoftDone, "", setpoint_pv="xn", readback_pv="xn.RBV")
    xp = cpt(PVPositionerSoftDone, "", setpoint_pv="xp", readback_pv="xp.RBV")
    size = cpt(PVPositionerSoftDone, "", setpoint_pv="size", readback_pv="size.RBV")
    center = cpt(
        PVPositionerSoftDone, "", setpoint_pv="center", readback_pv="center.RBV"
    )
    sync = cpt(
        EpicsSignal, "doSync", put_complete=True, kind="omitted"
    )  # TODO: What is the pv value for sync


class ID8Optics2Slit2D_HV(Optics2Slit2D_HV):
    h = cpt(ID8Optics2Slit1D, "H")
    v = cpt(ID8Optics2Slit1D, "V")


# Create the sl9 object
sl4 = ID8Optics2Slit2D_HV("8idESoft:Slit2", name="sl-7sl5.c")
