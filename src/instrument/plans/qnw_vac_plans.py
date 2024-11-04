"""
Change temperature on a QNW controller from a bluesky plan.

    RE(set_qnw(1, 20))

To watch the EPICS PVs in a simple GUI:

    pvview \
        8idi:QNWenv_1:SH_RBV 8idi:QNWenv_1:TARG \
        8idi:QNWenv_2:SH_RBV 8idi:QNWenv_2:TARG \
        8idi:QNWenv_3:SH_RBV 8idi:QNWenv_3:TARG \
        &
"""

__all__ = [
    "set_qnw_vac",
]

import logging

from bluesky import plan_stubs as bps

from ..devices import qnw_vac1
from ..devices import qnw_vac2
from ..devices import qnw_vac3

logger = logging.getLogger(__name__)
logger.info(__file__)


# Reference these controllers in a list by an index number with 1 offset.
qnw_controllers = [qnw_vac1, qnw_vac2, qnw_vac3]


def set_qnw_vac(qnw_number: int, setpoint: float, wait: bool = True, ramprate: float = 0.3):
    """
    Change temperature on a QNW controller from a bluesky plan.
    """
    if qnw_number < 1 or qnw_number > len(qnw_controllers):
        raise ValueError(
            f"qnw_number must be between 1 .. {len(qnw_controllers)},"
            f" received {qnw_number}."
        )
    qnw = qnw_controllers[qnw_number - 1]
    if qnw.ramprate.get() != ramprate:
        yield from bps.mv(qnw.ramprate, ramprate)

    if wait:
        yield from bps.mv(qnw, setpoint)
    else:
        yield from bps.mv(qnw.setpoint, setpoint)
