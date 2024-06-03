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
	from .aerotech_stages import *
except Exception as excuse:
	print(f"Could not import Aerotech: {excuse}")

try:
	from .flight_tube import *
except Exception as excuse:
	print(f"Could not import Flight Tube: {excuse}")

from .data_management import *
from .hhl_mirrors import *
from .meascomp_usb_ctr import *
from .qnw_device import *

# ----- ----- ----- ----- -----
# simulator depends on (Aerotech stage) sample.x
# TODO from .simulated_1d_detector import *

# ----- ----- ----- ----- -----
# imports that MUST come after the above devices
from .area_detectors import *

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
