"""
Simulate 1d rel_scan! demo for bluesky testing.

EXAMPLE::

    RE(demo_sim_1d())
"""

__all__ = """
    demo_sim_1d
""".split()

import logging

from bluesky import plans as bp

from ..devices import sim_1d
from ..devices import sim_motor

logger = logging.getLogger(__name__)
logger.info(__file__)


def demo_sim_1d():
    """Simple plan for testing purposes."""
    yield from bp.rel_scan([sim_1d], sim_motor, 0, 3, 21)
