import epics as pe
from bluesky import plans as bp
from bluesky import plan_stubs as bps

from ..devices.aerotech_stages import sample
from ..devices.tetramm_picoammeter import tetramm1
from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import rheometer
from ..devices.filters_8id import filter_8idi
from .shutter_logic import blockbeam
from .shutter_logic import pre_align
from .shutter_logic import showbeam



def x_lup(
    rel_begin=-3,
    rel_end=3,
    num_pts=30,
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
    num_pts=30,
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
    att_level=7,
    det=tetramm1,
):
    yield from pre_align()
    yield from bps.mv(filter_8idi.attenuation_set, att_level)

    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, rel_begin, rel_end, num_pts)
    yield from blockbeam()


def rheo_set_x_lup(att_level=4, det=tetramm1):

    yield from pre_align()
    yield from bps.mv(filter_8idi.attenuation_set, att_level)

    yield from bps.mv(rheometer.x, -15.27)
    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, -0.5, 0.5, 100)
    yield from blockbeam()

    yield from bps.mv(rheometer.x, -4.19)
    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, -0.5, 0.5, 100)
    yield from blockbeam()

    yield from bps.mv(rheometer.x, -9.8)
    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, -8, 8, 160)
    yield from blockbeam()



