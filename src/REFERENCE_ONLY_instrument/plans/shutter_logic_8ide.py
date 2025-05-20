import epics as pe
from bluesky import plan_stubs as bps
from ..devices.fast_shutter import shutter_8ide


def showbeam():
    yield from bps.mv(shutter_8ide.operation, 0)


def blockbeam():
    yield from bps.mv(shutter_8ide.operation, 1)


def shutteron():
    yield from bps.mv(shutter_8ide.logic, 0)


def shutteroff():
    yield from bps.mv(shutter_8ide.logic, 1)


def post_align():
    yield from blockbeam()


def pre_align():
    yield from shutteroff()

