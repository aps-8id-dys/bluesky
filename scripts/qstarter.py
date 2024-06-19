"""
Load devices and plans for bluesky queueserver.

How to start the queueserver process::

    DATABROKER_CATALOG=training
    STARTUP_DIR=$(pwd)

    start-re-manager \
        --startup-dir "${STARTUP_DIR}" \
        --update-existing-plans-devices ENVIRONMENT_OPEN \
        --zmq-publish-console ON \
        --databroker-config "${DATABROKER_CATALOG}"

"""

from __future__ import annotations

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).absolute().parent))

from aps_8id_bs_instrument.queueserver import *
from bluesky.plans import *

print_instrument_configuration()
print_devices_and_signals()
print_plans()
print_RE_metadata()
