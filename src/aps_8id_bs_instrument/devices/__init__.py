"""
local, custom Device definitions
"""

# flake8: noqa

try:
    from .aerotech_stages import sample, detector, rheometer
except Exception as excuse:
    print(f"Could not import Aerotech: {excuse}")

try:
    from .flight_tube import (
        det,
        bs,
    )
except Exception as excuse:
    print(f"Could not import Flight Tube: {excuse}")

from .ad_common import EigerDetectorCam_V34
from .data_management import (
    DM_WorkflowConnector,
    dm_experiment,
)

from .damm import damm
from .flag_4 import fl4
from .hhl_mirrors import mr1, mr2
from .hhl_slits import wb_slit
from .idt_mono import idt_mono
from .meascomp_usb_ctr import mcs
from .qnw_device import qnw_env1, qnw_env2, qnw_env3
from .slit_4 import sl4
from .ad_eiger_4M import eiger4M
from .ad_flag1 import flag1ad
from .ad_flag2 import flag2ad
from .ad_lambda_2M import lambda2M
from .ad_rigaku_3M import rigaku3M
from .ad_sim_4M import adsim4M
