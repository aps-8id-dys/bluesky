"""
ensure BlueSky is available
"""

__all__ = []


import logging
import sys

from aps_8id_bs_instrument import iconfig

try:
    import bluesky
except ImportError as err:
    raise ImportError(
        "No module named `bluesky`\n"
        f"This python is from directory: {sys.prefix}\n"
        "\n"
        "You should exit now and find a Python with Bluesky."
    ) from err

import databroker

logger = logging.getLogger(__name__)
logger.info(__file__)


def check_python_version():
    req_version = tuple(iconfig.get("MINIMUM_PYTHON_VERSION", (3, 7)))
    cur_version = sys.version_info
    if cur_version < req_version:
        ver_str = ".".join((map(str, req_version)))
        raise RuntimeError(
            f"Requires Python {ver_str}+ with the Bluesky framework.\n"
            f"You have Python {sys.version} from {sys.prefix}\n"
            "\n"
            "You should exit now and start a Python"
            " with the Bluesky framework."
        )


def check_ophyd_version():
    req_version = tuple(iconfig.get("MINIMUM_BLUESKY_VERSION", (1, 8)))
    cur_version = tuple(map(int, bluesky.__version__.split(".")[:2]))
    if cur_version < req_version:
        ver_str = ".".join((map(str, req_version)))
        raise ValueError(
            f"Need bluesky version {ver_str} or higher"
            f", found version {bluesky.__version__}"
        )


def check_databroker_version():
    req_version = tuple(iconfig.get("MINIMUM_DATABROKER_VERSION", (1, 2)))
    cur_version = tuple(map(int, databroker.__version__.split(".")[:2]))
    if cur_version < req_version:
        ver_str = ".".join((map(str, req_version)))
        raise ValueError(
            f"Need databroker version {ver_str} or higher"
            f", found version {databroker.__version__}"
        )
