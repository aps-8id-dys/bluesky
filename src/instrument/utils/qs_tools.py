"""
Configure for data collection using bluesky-queueserver.
"""

import inspect
import os

import pyRestTable
from ophyd import Device
from ophyd import Signal

from .iconfig_loader import iconfig


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
    '''make kv table'''
    table = pyRestTable.Table()
    table.labels = "key value".split()
    for k, v in sorted(data.items()):
        if isinstance(v, dict):
            table.addRow((k, make_kv_table(v)))
        else:
            table.addRow((k, v))
    return table


def print_instrument_configuration():
    '''print instrument config on table
    move this to instrument utils'''
    if len(iconfig) > 0:
        table = make_kv_table(iconfig)
        print("")
        print("Instrument configuration (iconfig):")
        print(table)


def print_RE_metadata(RE):
    """
    Print a table (to the console) with the current RunEngine metadata.
    """
    if len(RE.md) > 0:
        table = make_kv_table(RE.md)
        print("")
        print("RunEngine metadata:")
        print(table)


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
