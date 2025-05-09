"""
Custom Device Definitions & Instatiation
"""

# flake8: noqa

## Beamline specific devices (with rules)
try:
    from .aerotech_stages import sample, detector, rheometer
except Exception as excuse:
    print(f"Could not import Aerotech: {excuse}")

try:
    from .flight_tube import (
        det_motors,
        bs_motors,
    )
except Exception as excuse:
    print(f"Could not import Flight Tube: {excuse}")


## Beamline specific devices
from .meascomp_usb_ctr import mcs
