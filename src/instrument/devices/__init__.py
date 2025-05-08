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
from ...id8_i.devices.xy_motors import damm
from ...id8_i.devices.fl import fl2, fl3
from ...id8_i.devices.flag_4 import flag4
from ...id8_i.devices.granite import granite
from ...id8_i.devices.granite_enable import granite_8idi_valve
from ...id8_i.devices.hhl_mirrors import mr1, mr2
from ...id8_i.devices.hhl_slits import wb_slit, mono_slit
from ...id8_i.devices.idt_mono import idt_mono
from ...id8_i.devices.labjack_support import labjack
from ...id8_i.devices.fast_shutter import shutter_8ide
from .meascomp_usb_ctr import mcs
from ...id8_i.devices.qnw_device import qnw_env1, qnw_env2, qnw_env3

# from .qnw_vac_device import qnw_vac1, qnw_vac2, qnw_vac3
from ...id8_i.devices.filters_8id import filter_8ide, filter_8idi
from ...id8_i.devices.registers_device import pv_registers
from ...id8_i.devices.slit_base import sl4_base, sl5_base, sl7_base, sl8_base, sl9_base
from ...id8_i.devices.slit import sl4, sl5, sl7, sl8, sl9
from ...id8_i.devices.individual_slits import sl5_motors, sl9_motors
from ...id8_i.devices.softglue import softglue_8idi
from .tetramm_picoammeter import tetramm1, tetramm2, tetramm3, tetramm4

# from .transfocator_8idd import rl1
# from .transfocator_8ide import rl2
# from .xbpm2_in_8ide import bd6a
# from .xbpm2_in_8ide import xbpm2
# from ...xpcs.devices.win import win_e, win_i
from ...id8_i.devices.func_gen import dpKeysight
from ...id8_i.devices.huber_diffractometer import huber
from .rheometer_wait_signal import mcr_wait_signal
from .lakeshore import lakeshore1, lakeshore2
from .micellaneous_devices import cam_stage_8idi, mono_8id, flight_path_8idi


## Beamline Area Detectors
from .ad_flag1 import flag1ad
from .ad_flag2 import flag2ad
from .ad_flag3 import flag3ad
from .ad_flag4 import flag4ad
from .ad_lambda_2M import lambda2M
from .ad_rigaku_3M import rigaku3M
from .ad_rigaku_3M import rigaku500k
from .ad_sim_4M import adsim4M
