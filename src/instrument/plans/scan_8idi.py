from bluesky import plans as bp
from bluesky import plan_stubs as bps

from ..devices.aerotech_stages import sample
from ..devices.tetramm_picoammeter import tetramm1
from ..devices.filters import filter3
from .shutter_logic import blockbeam
from .shutter_logic import pre_align
from .shutter_logic import showbeam


def x_lup(
    rel_begin=-3,
    rel_end=3,
    num_pts=30,
    att_level=0,
):
    yield from pre_align()
    yield from bps.mv(filter3, att_level)

    yield from showbeam()
    yield from bp.rel_scan([tetramm1], sample.x, rel_begin, rel_end, num_pts)
    yield from blockbeam()


def y_lup(
    rel_begin=-3,
    rel_end=3,
    num_pts=30,
    att_level=0,
):
    yield from pre_align()
    yield from bps.mv(filter3, att_level)

    yield from showbeam()
    yield from bp.rel_scan([tetramm1], sample.y, rel_begin, rel_end, num_pts)
    yield from blockbeam()
