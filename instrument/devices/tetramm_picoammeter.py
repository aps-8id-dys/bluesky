"""
Caen picoammeter - TetraAMM

GitHub apstools issue #878 has some useful documentation in the comments.

.. see:: https://github.com/BCDA-APS/apstools/issues/878
"""

__all__ = """
    tetramm
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd import TetrAMM

tetramm = TetrAMM("8idTetra:QUAD1:", name="tetramm")
tetramm.wait_for_connection()
