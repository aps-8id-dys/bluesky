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
    from aps_8id_bs_instrument.devices.aerotech_stages import (
        AerotechDetectorStage,
        AerotechRheometerStage,
        AerotechSampleStage,
    )
except Exception as excuse:
    print(f"Could not import Aerotech: {excuse}")

try:
    from aps_8id_bs_instrument.devices.flight_tube import (
        FlightTubeBeamStop,
        FlightTubeDetector,
    )
except Exception as excuse:
    print(f"Could not import Flight Tube: {excuse}")

from aps_8id_bs_instrument import load_config
from aps_8id_bs_instrument.devices.ad_common import EigerDetectorCam_V34
from aps_8id_bs_instrument.devices.area_detectors import adsim4M, eiger4M
from aps_8id_bs_instrument.devices.damm import damm
from aps_8id_bs_instrument.devices.data_management import (
    DM_WorkflowConnector,
    dm_experiment,
)
from aps_8id_bs_instrument.devices.flag_4 import Flag4
from aps_8id_bs_instrument.devices.hhl_mirrors import HHL_Mirror1, HHL_Mirror2
from aps_8id_bs_instrument.devices.hhl_slits import HHLSlits
from aps_8id_bs_instrument.devices.idt_mono import IDTMono
from aps_8id_bs_instrument.devices.meascomp_usb_ctr import MeasCompCtr
from aps_8id_bs_instrument.devices.qnw_device import QnwDevice
from aps_8id_bs_instrument.devices.slit_4 import sl4
