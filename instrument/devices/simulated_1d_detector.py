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
""".split()

import logging
import random

logger = logging.getLogger(__name__)

logger.info(__file__)

from ophyd.sim import SynGauss
from . import sample

CENTER = 1.1 + 0.8*random.random()
IMAX = 95_000 + 10_000*random.random()
SIGMA = 0.01 + 0.1*random.random()

sim1d = SynGauss("sim1d", sample.x, sample.x.name, CENTER, IMAX, sigma=SIGMA, noise="poisson")
