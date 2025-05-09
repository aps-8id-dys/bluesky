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
