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
from .bd_5a import bd5a
from .damm import damm
from .fl import fl2, fl3
from .flag_4 import flag4
from .granite import granite
from .granite_enable import granite_8idi_valve
from .hhl_mirrors import mr1, mr2
from .hhl_slits import wb_slit, mono_slit
from .idt_mono import idt_mono
from .labjack_support import labjack
from .fast_shutter import shutter_8ide
from .meascomp_usb_ctr import mcs
from .qnw_device import qnw_env1, qnw_env2, qnw_env3
# from .qnw_vac_device import qnw_vac1, qnw_vac2, qnw_vac3
from .filters_8id import filter_8ide, filter_8idi
from .registers_device import pv_registers
from .slit_base import sl4_base, sl5_base, sl7_base, sl8_base, sl9_base
from .slit import sl4, sl5, sl7, sl8, sl9
from .individual_slits import sl5_motors, sl9_motors
from .softglue import softglue_8idi
from .tetramm_picoammeter import tetramm1, tetramm2, tetramm3, tetramm4
from .transfocator_8idd import rl1
from .transfocator_8ide import rl2
from .xbpm2_in_8ide import bd6a
from .xbpm2_in_8ide import xbpm2
from .win import win_e, win_i
from .func_gen import dpKeysight
from .huber_diffractometer import huber
from .rheometer_wait_signal import mcr_wait_signal
from .lakeshore import lakeshore1, lakeshore2
from .micellaneous_devices import cam_stage_8idi, mono_8id, flight_path_8idi


## Beamline Area Detectors
from .ad_eiger_4M import eiger4M
from .ad_flag1 import flag1ad
from .ad_flag2 import flag2ad
from .ad_flag3 import flag3ad
from .ad_flag4 import flag4ad
from .ad_lambda_2M import lambda2M
from .ad_rigaku_3M import rigaku3M
# from .ad_rigaku_3M import rigaku500k
from .ad_sim_4M import adsim4M

from .camera_stage_8idi import cam_x, cam_y
