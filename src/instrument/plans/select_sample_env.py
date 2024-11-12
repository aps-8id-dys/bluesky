"""
Plan that allows for moving to pre-programmed positions seen as strings
"""

__all__ = """
    select_sample_env
""".split()

import bluesky.plan_stubs as bps

from ..devices import granite
from ..devices import sample


def select_sample_env(env: str):
    # choices = {
    #     "qnw": 933.0,
    #     "rheometer": 62,
    # }
    # target = choices.get(env)
    # if target is None:
    #     raise KeyError(f"Unkown environment {env=!r}")

    if env == "qnw":
        yield from bps.mv(granite.x, 923.0)
        yield from bps.mv(sample.x, 150)
    if env == "rheometer":
        yield from bps.mv(granite.x, 65)
        yield from bps.mv(sample.x, 0.5)
    elif env == "robot":
        yield from bps.mv(granite.x, 62)
        yield from bps.mv(sample.x, 298)
