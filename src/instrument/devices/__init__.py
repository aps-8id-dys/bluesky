"""
Custom Device Definitions & Instatiation
"""

# flake8: noqa

## Simulated detector/motor
from .simulated_1d_detector import sim_1d, sim_motor

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
from .damm import damm
from .flag_4 import fl4
from .hhl_mirrors import mr1, mr2
from .hhl_slits import wb_slit, mono_slit
from .idt_mono import idt_mono
from .meascomp_usb_ctr import mcs
from .tetramm_picoammeter import tetramm
from .qnw_device import qnw_env1, qnw_env2, qnw_env3
from .slit_4_base import sl4_base
from .slit_4 import sl4
from .slit_5 import sl5
from .slit_7 import sl7
from .slit_8 import sl8
from .slit_9 import sl9
from .granite import granite

## Beamline Area Detectors
from .ad_eiger_4M import eiger4M
from .ad_flag1 import flag1ad
from .ad_flag2 import flag2ad
from .ad_lambda_2M import lambda2M
from .ad_rigaku_3M import rigaku3M
from .ad_sim_4M import adsim4M
