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
from apstools.utils import dm_setup
from bluesky import SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
from ophyd.signal import EpicsSignalBase
from ophydregistry import Registry

from .utils.catalog import load_catalog
from .utils.epics_tools import RUN_ENGINE_SCAN_ID_PV
from .utils.epics_tools import set_control_layer
from .utils.iconfig_loader import iconfig
from .utils.metadata import MD_PATH
from .utils.run_engine import run_engine

logger = logging.getLogger(__name__)
logger.info(__file__)

if iconfig["DM_SETUP_FILE"] is not None:
    dm_setup(iconfig["DM_SETUP_FILE"])

sd = SupplementalData()  # User will interact with the sd object, configure the RE for additional things to publish

bec = BestEffortCallback()  # Responsible for plots, only be instatiated once
if iconfig["BEC"]["BASELINE"] is False:
    bec.disable_baseline()  # User config
if iconfig["BEC"]["PLOTS"] is False:
    bec.disable_plots()  # User config

peaks = bec.peaks  # just an alias for less typing

# Connect with our mongodb database
catalog_name = iconfig.get("DATABROKER_CATALOG", "training")
try:
    # We don't actually run this part because it is unable to find a yaml corresponding to the catalog name. For this to execute the yaml has to be store in:
    # import databroker; print(databroker.catalog_search_path())
    # https://blueskyproject.io/databroker/reference/configuration.html?highlight=search%20path
    cat = load_catalog(catalog_name)
    logger.info("using databroker catalog '%s'", cat.name)
except KeyError:
    cat = databroker.temp().v2
    logger.info("using TEMPORARY databroker catalog '%s'", cat.name)

# Set up a RunEngine.
RE = run_engine(cat=cat, bec=bec, preprocessors=sd, md_path=MD_PATH)

set_control_layer("PyEpics")

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
    RUN_ENGINE_SCAN_ID_PV(_pv, RE)

logger.info("#### Bluesky tools are loaded is complete. ####")
