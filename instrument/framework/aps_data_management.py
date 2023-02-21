"""
Configure environment variables for APS data management.
"""

__all__ = []

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)
from os import environ
from .. import iconfig

env_vars = iconfig.get("APS_DATA_MANAGEMENT")
if env_vars is not None:
    environ.update(env_vars)
del env_vars
