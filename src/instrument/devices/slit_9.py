"""
Slit 9 in station 8-ID-I
"""

__all__ = """
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


class CustomOptics2Slit1D(Optics2Slit1D):
    xn = cpt(PVPositionerSoftDone, "", setpoint_pv="xn", readback_pv="xn.RBV")
    xp = cpt(PVPositionerSoftDone, "", setpoint_pv="xp", readback_pv="xp.RBV")
    size = cpt(PVPositionerSoftDone, "", setpoint_pv="size", readback_pv="size.RBV")
    center = cpt(
        PVPositionerSoftDone, "", setpoint_pv="center", readback_pv="center.RBV"
    )
    sync = cpt(
        EpicsSignal, "doSync", put_complete=True, kind="omitted"
    )  # TODO: What is the pv value for sync


class CustomOptics2Slit2D_HV(Optics2Slit2D_HV):
    h = cpt(CustomOptics2Slit1D, "H")
    v = cpt(CustomOptics2Slit1D, "V")


# Create the sl9 object
sl9 = CustomOptics2Slit2D_HV("8idiSoft:Slit2", name="sl-9")
