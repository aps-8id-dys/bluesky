"""
Configure for data collection using bluesky-queueserver.
"""


import inspect
import logging
import os

import bluesky
import ophyd
from ophyd import Device, Signal
import pyRestTable

from .. import iconfig
from ..callbacks import *
from ..devices import *
from ..plans import *
from ..utils.metadata import metadata
from ..initialize import RE, cat





# guides choice of module to import cat
iconfig["framework"] = "queueserver"

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)


metadata = metadata()

RE.subscribe(cat.v1.insert)

# Set up SupplementalData.
sd = bluesky.SupplementalData()
RE.preprocessors.append(sd)

ophyd.set_cl(iconfig.get("OPHYD_CONTROL_LAYER", "PyEpics").lower())
logger.info(f"using ophyd control layer: {ophyd.cl.name}")

# update OS environment variables for APS Data Management
def _chop(text):
    return text.strip().split()[-1].split("=")

# fmt: off
_ev = {
    _chop(line)[0]: _chop(line)[-1]
    for line in open(iconfig["DM_SETUP_FILE"]).readlines()
    if line.startswith("export ")
}
os.environ.update(_ev)


def make_kv_table(data):
    table = pyRestTable.Table()
    table.labels = "key value".split()
    for k, v in sorted(data.items()):
        if isinstance(v, dict):
            table.addRow((k, make_kv_table(v)))
        else:
            table.addRow((k, v))
    return table


def print_instrument_configuration():
    if len(iconfig) > 0:
        table = make_kv_table(iconfig)
        print("")
        print("Instrument configuration (iconfig):")
        print(table)


def print_RE_metadata():
    """
    Print a table (to the console) with the current RunEngine metadata.
    """
    if len(RE.md) > 0:
        table = make_kv_table(RE.md)
        print("")
        print("RunEngine metadata:")
        print(table)

if iconfig.get("WRITE_SPEC_DATA_FILES", False):
    if specwriter is not None:
        RE.subscribe(specwriter.receiver)
        logger.info(f"writing to SPEC file: {specwriter.spec_filename}")
        logger.info("   >>>>   Using default SPEC file name   <<<<")
        logger.info("   file will be created when bluesky ends its next scan")
        logger.info("   to change SPEC file, use command:   newSpecFile('title')")


def print_devices_and_signals():
    """
    Print the Devices and Signals in the current global namespace.
    """
    glo = globals().copy()

    table = pyRestTable.Table()
    table.labels = "device/object pvprefix/pvname connected?".split()
    for k, v in sorted(glo.items()):
        if isinstance(v, (Device, Signal)) and not k.startswith("_"):
            v.wait_for_connection()
            p = ""
            for aname in "pvname prefix".split():
                if hasattr(v, aname):
                    p = getattr(v, aname)
            table.addRow((v.name, p, v.connected))
    if len(table.rows) > 0:
        print("Table of Devices and signals:")
        print(table)


def print_plans():
    """
    Print the plans in the current global namespace.
    """
    glo = globals().copy()
    # fmt: off
    plans = [
        k
        for k, v in sorted(glo.items())
        if inspect.isgeneratorfunction(v)
    ]
    # fmt: on
    if len(plans) > 0:
        print("List of Plans:")
        for k in plans:
            print(f"* {k}{inspect.signature(glo[k])}")
        print("")


if iconfig.get("APS_IN_BASELINE", False):
    sd.baseline.append(aps)
