
from aps_8id_bs_instrument.devices.aerotech_stages import sample
from aps_8id_bs_instrument.plans.shutter_logic import shutteron, shutteroff, showbeam, blockbeam, post_align, pre_align
from aps_8id_bs_instrument.devices.tetramm_picoammeter import tetramm1
from bluesky import plans as bp
import epics as pe

def x_lup(
        rel_begin = -3,
        rel_end = 3,
        num_pts = 30,
        att_level = 0,
        ):

    yield from pre_align()
    pe.caput('8idPyFilter:FL3:sortedIndex', att_level)
    
    yield from showbeam()
    yield from bp.rel_scan([tetramm1], sample.x, rel_begin, rel_end, num_pts)
    yield from blockbeam()


def y_lup(
        rel_begin = -3,
        rel_end = 3,
        num_pts = 30,
        att_level = 0,
        ):

    yield from pre_align()
    pe.caput('8idPyFilter:FL3:sortedIndex', att_level)
    
    yield from showbeam()
    yield from bp.rel_scan([tetramm1], sample.y, rel_begin, rel_end, num_pts)
    yield from blockbeam()