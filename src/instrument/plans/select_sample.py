"""
Plan that allows for moving to pre-programmed positions seen as strings
"""

__all__ = """
    select_sample_env
""".split()

import bluesky.plan_stubs as bps
import time
import epics as pe

from ..devices import sample, eiger4M


def select_sample(env: int):

    yield from bps.mv(sample.y, 21.2)
    yield from bps.mv(eiger4M.cam.acquire_time, 0.1)
    yield from bps.mv(eiger4M.cam.acquire_period, 0.1)
    yield from bps.mv(eiger4M.cam.num_images, 1)

    eiger4M.stats1.kind = "hinted"
    eiger4M.stats1.mean_value.kind = "hinted"

    if env == 1:
        yield from bps.mv(sample.x, 304)
    if env == 2:
        yield from bps.mv(sample.x, 271.2)
    if env == 3:
        yield from bps.mv(sample.x, 238.2)
    if env == 4:
        yield from bps.mv(sample.x, 190.1)
    if env == 5:
        yield from bps.mv(sample.x, 156.9)
    if env == 6:
        yield from bps.mv(sample.x, 124.0)
    if env == 7:
        yield from bps.mv(sample.x, 76)
    if env == 8:
        yield from bps.mv(sample.x, 43)
    if env == 9:
        yield from bps.mv(sample.x, 10)

def open_shutter(): pe.caput('8idiSoft:fastshutter:State', 0); time.sleep(0.5)

def close_shutter(): pe.caput('8idiSoft:fastshutter:State', 1)