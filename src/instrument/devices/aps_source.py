"""
APS only: connect with facility information
===========================================

.. autosummary::
    ~aps
"""

import logging

from apstools.devices import ApsMachineParametersDevice

logger = logging.getLogger(__name__)
logger.info(__file__)

aps = ApsMachineParametersDevice(name="aps")
"""
Information from the APS Storage Ring, including current.

.. seealso:: `apstools.devices.ApsMachineParametersDevice
   <https://bcda-aps.github.io/apstools/latest/api/_devices.html#apstools.devices.aps_machine.ApsMachineParametersDevice>`_
"""
