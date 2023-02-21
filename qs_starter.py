"""
Load devices and plans for bluesky queueserver.
"""

import pathlib, sys

sys.path.append(
    str(pathlib.Path(__file__).absolute().parent)
)

from instrument import iconfig
from instrument.qserver import *


print_instrument_configuration()
print_devices_and_signals()
print_plans()
print_RE_metadata()
