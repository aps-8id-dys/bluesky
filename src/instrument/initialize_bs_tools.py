"""
Initialize bluesky tools
"""

__all__ = """
    RE  cat  sd  bec  peaks
    oregistry
    """.split()

import logging

# convenience imports
import databroker
import ophyd
from bluesky import SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
from ophyd.signal import EpicsSignalBase
from ophydregistry import Registry

from .utils.catalog import load_catalog
from .utils.iconfig_loader import iconfig
from .utils.metadata import MD_PATH
from .utils.run_engine import run_engine

# TODO: This is not inside init. Some aspects do not work with qserver.

logger = logging.getLogger(__name__)
logger.info(__file__)

sd = SupplementalData()  # User will interact with the sd object, configure the RE for additional things to publish

bec = BestEffortCallback()  # Responsible for plots, only be instatiated once
bec.disable_baseline()  # User config
# bec.disable_plots()  # User config

peaks = bec.peaks  # just an alias for less typing


# Connect with our mongodb database
catalog_name = iconfig.get("DATABROKER_CATALOG", "training")
try:
    cat = load_catalog(catalog_name)
    logger.info("using databroker catalog '%s'", cat.name)
except KeyError:
    cat = databroker.temp().v2
    logger.info("using TEMPORARY databroker catalog '%s'", cat.name)

# Set up a RunEngine.
RE = run_engine(cat=cat, bec=bec, preprocessors=sd, md_path=MD_PATH)

# OPHYD_CONTROL_LAYER is an application of "lessons learned."
# The next line can be used to switch from PyEpics to caproto.
# Only used in a couple rare cases where PyEpics code was failing.
# It's defined here since it was difficult to find how to do this
# in the ophyd documentation.
ophyd.set_cl(iconfig.get("OPHYD_CONTROL_LAYER", "PyEpics").lower())
logger.info(f"using ophyd control layer: {ophyd.cl.name}")

# Set default timeout for all EpicsSignal connections & communications.
TIMEOUT = 60  # default used next...
if not EpicsSignalBase._EpicsSignalBase__any_instantiated:
    # Only BEFORE any EpicsSignalBase (or subclass) are created!
    EpicsSignalBase.set_defaults(
        auto_monitor=True,
        timeout=iconfig.get("PV_READ_TIMEOUT", TIMEOUT),
        write_timeout=iconfig.get("PV_WRITE_TIMEOUT", TIMEOUT),
        connection_timeout=iconfig.get("PV_CONNECTION_TIMEOUT", TIMEOUT),
    )


# Create a registry of ophyd devices
oregistry = Registry(auto_register=True)


_pv = iconfig.get("RUN_ENGINE_SCAN_ID_PV")
if _pv is None:
    logger.info("Using RunEngine metadata for scan_id")
else:
    from ophyd import EpicsSignal

    logger.info("Using EPICS PV %s for scan_id", _pv)
    scan_id_epics = EpicsSignal(_pv, name="scan_id_epics")

    def epics_scan_id_source(_md):
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

    # tell RunEngine to use the EPICS PV to provide the scan_id.
    RE.scan_id_source = epics_scan_id_source
    scan_id_epics.wait_for_connection()
    RE.md["scan_id"] = scan_id_epics.get()


logger.info("#### Bluesky tools are loaded is complete. ####")
