"""
Set granite block & sample position for collection with specific environments.

.. automodule::
    ~select_sample_env
"""

__all__ = """
    select_sample_env
""".split()

import bluesky.plan_stubs as bps

from ..devices import granite
from ..devices import sample


def select_sample_env(env: str):
    """
    Plan: Reposition for specific, named environments.
    """
    if env == "qnw":
        yield from bps.mv(granite.x, 933.0)
        yield from bps.mv(sample.x, 150)
    elif env == "rheometer":
        yield from bps.mv(granite.x, 62)
        yield from bps.mv(sample.x, 0.5)
    elif env == "robot":
        yield from bps.mv(granite.x, 62)
        yield from bps.mv(sample.x, 298)
    raise KeyError(f"Unkown environment {env=!r}")
