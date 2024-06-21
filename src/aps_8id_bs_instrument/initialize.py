"""
initialize the bluesky framework
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
from bluesky.utils import PersistentDict, ProgressBarManager
from ophyd.signal import EpicsSignalBase
from ophydregistry import Registry

from . import iconfig
from .run_engine import run_engine
from .utils.ipy_helper import *  # noqa
from .utils.metadata import MD_PATH

logger = logging.getLogger(__name__)
logger.info(__file__)

sd = SupplementalData()

bec = BestEffortCallback()
peaks = bec.peaks  # just as alias for less typing
bec.disable_baseline()

# Set up a RunEngine and use metadata backed PersistentDict
RE = run_engine(connect_databroker=True, use_bec=True, extra_md=sd)

RE.md = PersistentDict(MD_PATH)

# Connect with our mongodb database
catalog_name = iconfig.get("DATABROKER_CATALOG", "training")
try:
    cat = databroker.catalog[catalog_name]
    logger.info("using databroker catalog '%s'", cat.name)
except KeyError:
    cat = databroker.temp().v2
    logger.info("using TEMPORARY databroker catalog '%s'", cat.name)

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
RE.subscribe(cat.v1.insert)


if iconfig.get("USE_PROGRESS_BAR", False):
    # Add a progress bar.
    pbar_manager = ProgressBarManager()
    RE.waiting_hook = pbar_manager


# At the end of every run, verify that files were saved and
# print a confirmation message.
# from bluesky.callbacks.broker import verify_files_saved
# RE.subscribe(post_run(verify_files_saved), 'stop')

# Uncomment the following lines to turn on
# verbose messages for debugging.
# ophyd.logger.setLevel(logging.DEBUG)

ophyd.set_cl(iconfig.get("OPHYD_CONTROL_LAYER", "PyEpics").lower())
logger.info(f"using ophyd control layer: {ophyd.cl.name}")

# diagnostics
# RE.msg_hook = ts_msg_hook

# set default timeout for all EpicsSignal connections & communications
TIMEOUT = 60
if not EpicsSignalBase._EpicsSignalBase__any_instantiated:
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

# this is where run engine gets created
