"""
Provide information from the configuration.yml file.

Example YAML configuration file::

    # simple key:value pairs

    ADSIM_IOC_PREFIX: "bdpad:"
    GP_IOC_PREFIX: "bdp:"
    catalog: bdp2022
"""

from __future__ import annotations

__all__ = [
    "iconfig",
]
import logging
import pathlib

import yaml

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)

CONFIG_FILE = pathlib.Path(__file__).absolute().parent / "iconfig.yml"

if CONFIG_FILE.exists():
    iconfig = yaml.load(open(CONFIG_FILE, "r").read(), yaml.Loader)
else:
    raise FileNotFoundError(
        f"Could not find instrument configuration file: {CONFIG_FILE}"
    )
