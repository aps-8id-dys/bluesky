"""
Plan stubs (from the SPEC macros) for the shutters.
"""

from bluesky import plan_stubs as bps

from ..devices.flight_tube import flight_tube_shutter
from ..devices.labjack_support import labjack


def showbeam():
    yield from bps.mv(labjack.operation, 0)


def blockbeam():
    yield from bps.mv(labjack.operation, 1)


def shutteron():
    yield from bps.mv(labjack.logic, 0)


def shutteroff():
    yield from bps.mv(labjack.logic, 1)


def post_align():
    yield from flight_tube_shutter.close()
    yield from blockbeam()


def pre_align():
    yield from flight_tube_shutter.open()
    yield from shutteroff()
