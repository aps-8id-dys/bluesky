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
from __future__ import annotations

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

# ----- ----- ----- ----- -----
# See the .unused_examples folder
# Copy/move to this folder and edit to use.
# from .aps_source import *
# from .aps_undulator import *

# from .area_detector import *
# from .calculation_records import *
# from .fourc_diffractometer import *
# from .ioc_stats import *
# from .kohzu_monochromator import *
# from .motors import *
# from .noisy_detector import *
# from .scaler import *
# from .shutter_simulator import *
# from .simulated_fourc import *
# from .simulated_kappa import *
# from .slits import *
# from .sixc_diffractometer import *
# from .temperature_signal import *
