"""
Configure for data collection using bluesky-queueserver.
"""

from __future__ import annotations

import inspect
import logging

import pyRestTable
from ophyd import Device, Signal

from aps_8id_bs_instrument import iconfig
from aps_8id_bs_instrument.callbacks import *
from aps_8id_bs_instrument.devices import *
from aps_8id_bs_instrument.plans import *
from aps_8id_bs_instrument.queueserver_framework import *
from aps_8id_bs_instrument.utils import *

# guides choice of module to import cat
iconfig["framework"] = "queueserver"

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)

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
