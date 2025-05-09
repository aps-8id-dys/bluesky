from apsbits.core.instrument_init import oregistry
from bluesky import plan_stubs as bps
from bluesky import plans as bp

from .shutter_logic import blockbeam
from .shutter_logic import pre_align
from .shutter_logic import showbeam

rheometer = oregistry["rheometer"]
sample = oregistry["sample"]
filter_8idi = oregistry["filter_8idi"]
tetramm1 = oregistry["tetramm1"]


def att(att_ratio=None):
    yield from bps.mv(filter_8idi.attenuation_set, att_ratio)
    yield from bps.sleep(2)
    yield from bps.mv(filter_8idi.attenuation_set, att_ratio)
    yield from bps.sleep(2)
    yield from bps.mv(filter_8idi.attenuation_set, att_ratio)
    yield from bps.sleep(2)


def x_lup(
    rel_begin=-3,
    rel_end=3,
    num_pts=60,
    att_level=7,
    det=tetramm1,
):
    yield from pre_align()
    yield from bps.mv(filter_8idi.attenuation_set, att_level)

    yield from showbeam()
    yield from bp.rel_scan([det], sample.x, rel_begin, rel_end, num_pts)
    yield from blockbeam()


def y_lup(
    rel_begin=-3,
    rel_end=3,
    num_pts=60,
    att_level=7,
    det=tetramm1,
):
    yield from pre_align()
    yield from bps.mv(filter_8idi.attenuation_set, att_level)

    yield from showbeam()
    yield from bp.rel_scan([det], sample.y, rel_begin, rel_end, num_pts)
    yield from blockbeam()


def rheo_x_lup(
    rel_begin=-3,
    rel_end=3,
    num_pts=30,
    att_level=10,
    det=tetramm1,
):
    yield from pre_align()
    yield from bps.mv(filter_8idi.attenuation_set, att_level)

    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, rel_begin, rel_end, num_pts)
    yield from blockbeam()


def rheo_y_lup(
    rel_begin=-3,
    rel_end=3,
    num_pts=30,
    att_level=10,
    det=tetramm1,
):
    yield from pre_align()
    yield from bps.mv(filter_8idi.attenuation_set, att_level)

    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.y, rel_begin, rel_end, num_pts)
    yield from blockbeam()


def rheo_set_x_lup(att_level=10, det=tetramm1):
    yield from pre_align()
    yield from bps.mv(filter_8idi.attenuation_set, att_level)

    yield from bps.mv(rheometer.x, -8.99)
    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, -0.5, 0.5, 100)
    yield from blockbeam()

    yield from bps.mv(rheometer.x, 2.12)
    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, -0.5, 0.5, 100)
    yield from blockbeam()

    yield from bps.mv(rheometer.x, -3.53)
    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, -8, 8, 160)
    yield from blockbeam()
