#!/usr/bin/env python

"""
configure the Bluesky framework
"""

from aps_8id_bs_instrument.tests.check_subnet import warn_if_not_aps_controls_subnet
from aps_8id_bs_instrument.utils.metadata import metadata

warn_if_not_aps_controls_subnet()
print(metadata())
