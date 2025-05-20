"""
Tools that beamline might require tied with epics
"""

import logging

import ophyd
from ophyd import EpicsSignal

from .iconfig_loader import iconfig


def epics_scan_id_source(scan_id_epics, _md):
    """
    Callback function for RunEngine.  Returns *next* scan_id to be used.

    * Ignore metadata dictionary passed as argument.
    * Get current scan_id from PV.
    * Apply lower limit of zero.
    * Increment (so that scan_id numbering starts from 1).
    * Set PV with new value.
    * Return new value.

    Exception will be raised if PV is not connected when next
    ``bps.open_run()`` is called.
    """
    new_scan_id = max(scan_id_epics.get(), 0) + 1
    scan_id_epics.put(new_scan_id)
    return new_scan_id


def RUN_ENGINE_SCAN_ID_PV(_pv, RE):
    """
    Define a PV to use for the `scan_id`.
    """
    logger = logging.getLogger(__name__)
    logger.info("Using EPICS PV %s for scan_id", _pv)

    scan_id_epics = EpicsSignal(_pv, name="scan_id_epics")

    # Tell RunEngine to use the EPICS PV to provide the scan_id.
    RE.scan_id_source = epics_scan_id_source(scan_id_epics)
    scan_id_epics.wait_for_connection()
    RE.md["scan_id"] = scan_id_epics.get()


def set_control_layer(control_layer):
    """
    OPHYD_CONTROL_LAYER is an application of "lessons learned."
    The next line can be used to switch from PyEpics to caproto.
    Only used in a couple rare cases where PyEpics code was failing.
    It's defined here since it was difficult to find how to do this
    in the ophyd documentation.
    """
    logger = logging.getLogger(__name__)

    ophyd.set_cl(iconfig.get("OPHYD_CONTROL_LAYER", control_layer).lower())

    logger.info(f"using ophyd control layer: {ophyd.cl.name}")
