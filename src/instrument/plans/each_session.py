"""
Plans to be run for each session or experiment.

.. automodule::
    ~xpcs_setup_user
"""

import logging

try:
    from apstools.utils import dm_isDaqActive
except ImportError:
    # TODO hoist to apstools
    from ..utils.aps_data_management import dm_isDaqActive  # noqa
from apstools.utils import dm_start_daq
from apstools.utils import validate_experiment_dataDirectory
from bluesky import plan_stubs as bps

logger = logging.getLogger(__name__)
logger.info(__file__)

from ..devices.xpcs_support import xpcs_dm  # noqa: E402
from ..initialize_bs_tools import RE  # noqa: E402
from .ad_setup_plans import write_if_new  # noqa: E402


def xpcs_setup_user(dm_experiment_name: str, index: int = -1):
    """
    Configure bluesky session for this user and DM experiment.

    PARAMETERS

    dm_experiment_name *str*:
        Name of active APS Data Management experiment for this
        data acquisition.
    index *int*:
        Sequence number of XPCS data acquisition.

        .. hint:: Set ``index=-1`` to continue with current
           'xpcs_index' value.
    """
    validate_experiment_dataDirectory(dm_experiment_name)
    yield from bps.mv(xpcs_dm.experiment_name, dm_experiment_name)

    if index >= 0:
        yield from write_if_new(xpcs_dm.index, index)
    RE.md["xpcs_index"] = xpcs_dm.index.get()

    # Needed when data acquisition (Bluesky, EPICS, ...) writes to Voyager.
    # Full path to directory where new data will be written.
    # XPCS new data is written to APS Voyager storage (path
    # starting with ``/gdata/``).  Use "@voyager" in this case.
    # DM sees this and knows not copy from voyager to voyager.
    data_directory = "@voyager"

    # Check DM DAQ is running for this experiment, if not then start it.
    if not dm_isDaqActive(dm_experiment_name):
        # Need another DAQ if also writing to a different directory (off voyager).
        # A single DAQ can be used to cover any subdirectories.
        # Anything in them will be uploaded.
        msg = (
            f"Starting DM DAQ: experiment {dm_experiment_name!r}"
            f" in data directory {data_directory!r}."
        )
        logger.info(msg)
        print(msg)  # Was not showing up in the logs.
        dm_start_daq(dm_experiment_name, data_directory)
