"""
start bluesky in IPython console session
"""

import pathlib
import sys

from IPython import get_ipython

# This is the Ipython profile

# start a Bluesky data collection console session

# find the "bluesky/" directory
BLUESKY_DIRECTORY = pathlib.Path.home() / "bluesky"
if not BLUESKY_DIRECTORY.exists():
    # <training repository directory>
    BLUESKY_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent.parent
    BLUESKY_DIRECTORY = BLUESKY_DIRECTORY / "bluesky"
if not BLUESKY_DIRECTORY.exists():
    raise FileNotFoundError(f"Cannot find bluesky directory: {BLUESKY_DIRECTORY}")
# put bluesky directory on the import path
sys.path.append(str(BLUESKY_DIRECTORY))

# terse error dumps (Exception tracebacks)
get_ipython().run_line_magic("xmode", "Minimal")

from aps_8id_bs_instrument.collection import *
