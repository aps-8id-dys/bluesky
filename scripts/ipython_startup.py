import logging

import aps_8id_bs_instrument  # noqa: F401
import aps_8id_bs_instrument.initialize  # noqa: F401
import databroker  # noqa: F401
import matplotlib.pyplot as plt  # noqa: F401
from aps_8id_bs_instrument.collection import *
from bluesky import (
    RunEngine,  # noqa: F401
    suspenders,  # noqa: F401
)
from bluesky import plan_stubs as bps  # noqa: F401
from bluesky import plans as bp  # noqa: F401
from bluesky.callbacks.best_effort import BestEffortCallback  # noqa: F401

logging.basicConfig(level=logging.WARNING)

get_ipython().run_line_magic("xmode", "Minimal")


# # # Prepare the BlueSky instrument
config = aps_8id_bs_instrument.iconfig
t0 = time.monotonic()
# print(f"Initializing {config['beamline']['name']}…")
aps_8id_bs_instrument.initialize()
print(f"Finished initalization in {time.monotonic() - t0:.2f} seconds.")
