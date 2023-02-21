"""
Configure environment variables for APS data management.
"""

__all__ = []

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)
from os import environ
from .. import iconfig

constants = iconfig.get("APS_DATA_MANAGEMENT")
if constants is not None:
    environ.update(constants)
    # for k, v in constants.items():
    #     print(f"{k=} {v=}")
del constants
