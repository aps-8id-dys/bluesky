"""
Plans to be run for each session or experiment.

.. automodule::
    ~xpcs_setup_user
"""

import logging

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

    .. note:: Set ``index=-1`` to continue with current 'xpcs_index' value.
    """
    validate_experiment_dataDirectory(dm_experiment_name)
    yield from bps.mv(xpcs_dm.experiment_name, dm_experiment_name)

    if index >= 0:
        yield from write_if_new(xpcs_dm.index, index)
    RE.md["xpcs_index"] = xpcs_dm.index.get()
