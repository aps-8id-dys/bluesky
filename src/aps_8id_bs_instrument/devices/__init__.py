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
	from aps_8id_bs_instrument.aerotech_stages import *
except Exception as excuse:
	print(f"Could not import Aerotech: {excuse}")

try:
	from aps_8id_bs_instrument.flight_tube import *
except Exception as excuse:
	print(f"Could not import Flight Tube: {excuse}")

# ----- ----- ----- ----- -----
# simulator depends on (Aerotech stage) sample.x
# TODO from .simulated_1d_detector import *
# ----- ----- ----- ----- -----
# imports that MUST come after the above devices
from aps_8id_bs_instrument.area_detectors import *
from aps_8id_bs_instrument.damm import *
from aps_8id_bs_instrument.data_management import *
from aps_8id_bs_instrument.flag_4 import *
from aps_8id_bs_instrument.hhl_mirrors import *
from aps_8id_bs_instrument.hhl_slits import *
from aps_8id_bs_instrument.idt_mono import *
from aps_8id_bs_instrument.meascomp_usb_ctr import *
from aps_8id_bs_instrument.qnw_device import *
from aps_8id_bs_instrument.slit_4 import *
