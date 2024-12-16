import epics as pe
from bluesky import plans as bp

from ..devices.aerotech_stages import sample
from ..devices.tetramm_picoammeter import tetramm1
from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import rheometer
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
    pe.caput("8idPyFilter:FL3:sortedIndex", att_level)

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
    pe.caput("8idPyFilter:FL3:sortedIndex", att_level)

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
    pe.caput("8idPyFilter:FL3:sortedIndex", att_level)

    yield from showbeam()
    yield from bp.rel_scan([det], rheometer.x, rel_begin, rel_end, num_pts)
    yield from blockbeam()

