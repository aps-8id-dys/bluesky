"""
APS only: connect with facility information
"""

from __future__ import annotations

__all__ = [
    "aps",
]

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

import apstools.devices

aps = apstools.devices.ApsMachineParametersDevice(name="aps")
