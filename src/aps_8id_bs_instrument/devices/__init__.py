"""
local, custom Device definitions
"""

# flake8: noqa

try:
    from .aerotech_stages import (
        AerotechDetectorStage,
        AerotechRheometerStage,
        AerotechSampleStage,
    )
except Exception as excuse:
    print(f"Could not import Aerotech: {excuse}")

try:
    from .flight_tube import (
        FlightTubeBeamStop,
        FlightTubeDetector,
    )
except Exception as excuse:
    print(f"Could not import Flight Tube: {excuse}")

# from .. import load_config
from .ad_common import EigerDetectorCam_V34
from .damm import damm
from .data_management import (
    DM_WorkflowConnector,
    dm_experiment,
)
from .flag_4 import fl4
from .hhl_mirrors import HHL_Mirror1, HHL_Mirror2
from .hhl_slits import wb_slit
from .idt_mono import IDTMono
from .meascomp_usb_ctr import MeasCompCtr
from .qnw_device import QnwDevice
from .slit_4 import sl4


from .ad_eiger_4M import eiger4M
from .ad_flag1 import flag1ad
from .ad_flag2 import flag2ad
from .ad_lambda_2M import lambda2M
from .ad_rigaku_3M import rigaku3M
from .ad_sim_4M import adsim4M
