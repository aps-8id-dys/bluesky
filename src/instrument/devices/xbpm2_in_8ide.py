"""
XBPM2: X-ray beam position monitor in 8-ID-E for use in I station.

Device 'bd6a' positions the xbpm2 with h & v translations.
"""

__all__ = """
    bd6a
    xbpm2
""".split()

import logging

from ._8id_common import HV_Motors
from ._8id_common import SydorTP4U

logger = logging.getLogger(__name__)
logger.info(__file__)

bd6a = HV_Motors("8iddSoft:CR8-E2:", name="bd6a", pv_h="m9", pv_v="m10")
xbpm2 = SydorTP4U("8idiSoft:T4U_BPM:", name="xbpm2")
