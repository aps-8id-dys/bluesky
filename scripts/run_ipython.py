#!/usr/bin/env python

import logging
import time

import aps_8id_bs_instrument  # noqa: F401
import databroker  # noqa: F401
import matplotlib.pyplot as plt  # noqa: F401
from bluesky import (
    RunEngine,  # noqa: F401
    suspenders,  # noqa: F401
)
from bluesky import plan_stubs as bps  # noqa: F401
from bluesky import plans as bp  # noqa: F401
from bluesky.callbacks.best_effort import BestEffortCallback  # noqa: F401
from bluesky.simulators import summarize_plan  # noqa: F401

logging.basicConfig(level=logging.WARNING)

# from IPython import get_ipython
# get_ipython().run_line_magic("xmode", "Minimal")
# from aps_8id_bs_instrument.collection import *

# Allow best effort callback to update properly
plt.ion()

# # Prepare the BlueSky instrument
config = aps_8id_bs_instrument.load_config()
t0 = time.monotonic()
# print(f"Initializing {config['beamline']['name']}…")

aps_8id_bs_instrument.load_instrument()
print(f"Finished initalization in {time.monotonic() - t0:.2f} seconds.")
RE = aps_8id_bs_instrument.run_engine()

# # Save references to some commonly used things in the global namespace
# registry = haven.registry
# ion_chambers = haven.registry.findall("ion_chambers")

# # Add metadata to the run engine
# RE.preprocessors.append(haven.preprocessors.inject_haven_md_wrapper)
