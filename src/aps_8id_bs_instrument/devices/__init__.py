"""
local, custom Device definitions
"""

# noqa
# fmt: off
# ----- ----- ----- ----- -----
# from ophyd.log import config_ophyd_logging
# config_ophyd_logging(level="DEBUG")
#     # 'ophyd' — the logger to which all ophyd log records propagate
#     # 'ophyd.objects' — logs records from all devices and signals (that is, OphydObject subclasses)
#     # 'ophyd.control_layer' — logs requests issued to the underlying control layer (e.g. pyepics, caproto)
#     # 'ophyd.event_dispatcher' — issues regular summaries of the backlog of updates from the control layer that are being processed on background threads
# ----- ----- ----- ----- -----

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

from .. import load_config
from .ad_common import EigerDetectorCam_V34
from .area_detectors import adsim4M, eiger4M
from .damm import damm
from .data_management import (
    DM_WorkflowConnector,
    dm_experiment,
)
from .flag_4 import Flag4
from .hhl_mirrors import HHL_Mirror1, HHL_Mirror2
from .hhl_slits import HHLSlits
from .idt_mono import IDTMono
from .meascomp_usb_ctr import MeasCompCtr
from .qnw_device import QnwDevice
from .slit_4 import sl4
