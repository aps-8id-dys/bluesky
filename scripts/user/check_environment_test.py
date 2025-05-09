#!/usr/bin/env python

"""
Tests to see if Bluesky can functions at APS Beamline
"""

from aps_8id_bs_instrument.tests.check_dm import check_dm
from aps_8id_bs_instrument.tests.check_subnet import warn_if_not_aps_controls_subnet

warn_if_not_aps_controls_subnet()
check_dm()
