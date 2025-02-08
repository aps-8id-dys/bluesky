"""
Provides and instatiates information from the iconfig.yml file.

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
import os

import yaml

logger = logging.getLogger(__name__)

logger.info(__file__)
print(__file__)


def load_config_yaml():
    """Load iconfig.yml config files."""

    # Get the absolute path of the current file
    current_file_path = os.path.abspath(__file__)

    # Navigate two directories up
    two_dirs_up = os.path.dirname(os.path.dirname(current_file_path))

    # Define the target folder and file
    target_folder = "configs"
    target_file = "iconfig.yml"

    # Construct the full path to the target file
    target_file_path = os.path.join(two_dirs_up, target_folder, target_file)

    CONFIG_FILE = target_file_path

    if os.path.exists(CONFIG_FILE):
        iconfig = yaml.load(open(CONFIG_FILE, "r").read(), yaml.Loader)
    else:
        raise FileNotFoundError(
            f"Could not find instrument configuration file: {CONFIG_FILE}"
        )

    # Load configuration from TOML files
    return iconfig


iconfig = load_config_yaml()
