"""
QNW temperature controller
"""

__all__ = [
    "qnw_env1",
    "qnw_env2",
    "qnw_env3",
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
qnw_env1 = QnwDevice("8idiSoft:QNWenv_1:", readback_pv=None, name="qnw_env1")
qnw_env2 = QnwDevice("8idiSoft:QNWenv_2:", readback_pv=None, name="qnw_env2")
qnw_env3 = QnwDevice("8idiSoft:QNWenv_3:", readback_pv=None, name="qnw_env3")


# TODO:
# Add read-only temperatures to watch.  (What PVs?)
