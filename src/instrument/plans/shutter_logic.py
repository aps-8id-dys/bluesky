import epics as pe
from bluesky import plan_stubs as bps

from ...xpcs.devices.labjack_support import labjack


def showbeam():
    yield from bps.mv(labjack.operation, 0)


def blockbeam():
    yield from bps.mv(labjack.operation, 1)


def shutteron():
    yield from bps.mv(labjack.logic, 0)


def shutteroff():
    yield from bps.mv(labjack.logic, 1)


def post_align():
    pe.caput("8idiSoft:FLIGHT:bo1:8", 1)
    yield from blockbeam()


def pre_align():
    pe.caput("8idiSoft:FLIGHT:bo1:8", 0)
    yield from shutteroff()
