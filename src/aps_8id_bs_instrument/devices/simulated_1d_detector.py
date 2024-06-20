"""
Simulated 1-D detector signal based on an EPICS motor position.

Test Examples::

    from apstools.plans import lineup

    RE(bp.scan([sim1d], sample.x, 0, 3, 21))
    RE(bp.rel_scan([sim1d], sample.x, 0, 3, 21))
    RE(lup([sim1d], sample.x, 0, 3, 21))
    RE(lineup([sim1d], sample.x, 0, 3, 21))
"""

__all__ = """
    sim1d
    motor
""".split()

import logging
import random

from ophyd.sim import SynGauss, motor

from . import sample  # noqa

logger = logging.getLogger(__name__)
logger.info(__file__)


MOTOR = motor
# MOTOR = sample.x
CENTER = 1.1 + 0.8 * random.random()
IMAX = 95_000 + 10_000 * random.random()
SIGMA = 0.01 + 0.1 * random.random()
NOISE = "poisson"

if MOTOR.connected:
    sim1d = SynGauss(
        "sim1d",
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
