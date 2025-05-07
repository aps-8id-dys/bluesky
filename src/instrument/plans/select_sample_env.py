"""
Plan that allows for moving to pre-programmed positions seen as strings
"""

__all__ = """
    select_sample_env
""".split()

import bluesky.plan_stubs as bps

from ..devices import granite, granite_8idi_valve
from ..devices import sample


def select_sample_env(env: str):
    choices = {
        "qnw": 923.0,
        "rheometer": 65,
        "robot": 62,
    }
    target = choices.get(env)
    if target is None:
        raise KeyError(f"Unkown environment {env=!r}")

    yield from bps.mv(granite_8idi_valve.enable, 1)
    yield from bps.sleep(2)

    if env == "qnw":
        yield from bps.mv(granite.x, choices['qnw'])
    if env == "rheometer":
        yield from bps.mv(granite.x, choices['rheometer'])
    elif env == "robot":
        yield from bps.mv(granite.x, choices['robot'])
        yield from bps.mv(sample.x, 298)

    yield from bps.mv(granite_8idi_valve.enable, 0)
    yield from bps.sleep(2)
