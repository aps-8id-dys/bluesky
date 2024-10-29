

from aps_8id_bs_instrument.devices.labjack_support import labjack
from bluesky import plans as bp
from bluesky import plan_stubs as bps


def showbeam():
    yield from bps.mv(labjack.operation, 0)


def blockbeam():
    yield from bps.mv(labjack.operation, 1)


def shutteron():
    yield from bps.mv(labjack.logic, 0)


def shutteroff():
    yield from bps.mv(labjack.logic, 1)


def post_align():
    ### Placeholder for putting the pind in and out
    yield from blockbeam()
