"""
Simulated 1-D detector signal based on an EPICS motor position.

Test Examples::

    from apstools.plans import lineup

    RE(bp.scan([sim_1d], sim_motor, 0, 3, 21))
    RE(bp.rel_scan([sim_1d], sim_motor, 0, 3, 21))
    RE(lup([sim_1d], sim_motor, 0, 3, 21))
    RE(lineup([sim_1d], sim_motor, 0, 3, 21))
"""

__all__ = """
    sim_1d
    sim_motor
""".split()

import logging
import random

from ophyd.sim import SynGauss
from ophyd.sim import motor as sim_motor

logger = logging.getLogger(__name__)
logger.info(__file__)

MOTOR = sim_motor
CENTER = 1.1 + 0.8 * random.random()
IMAX = 95_000 + 10_000 * random.random()
SIGMA = 0.01 + 0.1 * random.random()
NOISE = "poisson"

if MOTOR.connected:
    sim_1d = SynGauss(
        "sim_1d",
        MOTOR,
        MOTOR.name,
        CENTER,
        IMAX,
        sigma=SIGMA,
        noise=NOISE,
        labels=["simulator"],
    )
else:
    logger.warning("motor %s not connected, cannot create sim1d Device", MOTOR.name)
    sim1d = None
