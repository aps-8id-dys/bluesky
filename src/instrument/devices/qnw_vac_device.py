"""
QNW temperature controller
"""

__all__ = [
    "qnw_vac1",
    "qnw_vac2",
    "qnw_vac3",
]

import logging

from apstools.devices import PVPositionerSoftDoneWithStop
from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import Signal

logger = logging.getLogger(__name__)
logger.info(__file__)


class QnwDevice(PVPositionerSoftDoneWithStop):
    readback = Component(EpicsSignalRO, "SH_RBV", kind="hinted", auto_monitor=True)
    setpoint = Component(EpicsSignal, "TARG", kind="normal", put_complete=True)
    tolerance = Component(Signal, value=0.1, kind="config")
    ramprate = Component(EpicsSignal, "RAMP", kind="normal", put_complete=True)


# Use readback_pv=None since readback and setpoint were defined above.
# Works even though it looks ugglee.
qnw_vac1 = QnwDevice("8idiSoft:QNWvac_1:", readback_pv=None, name="qnw_vac1")
qnw_vac2 = QnwDevice("8idiSoft:QNWvac_2:", readback_pv=None, name="qnw_vac2")
qnw_vac3 = QnwDevice("8idiSoft:QNWvac_3:", readback_pv=None, name="qnw_vac3")
