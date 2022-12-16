"""
Start bluesky in IPython console session.
"""

# start a Bluesky data collection console session
from IPython import get_ipython
import pathlib
import sys

# find the "bluesky/" directory
BLUESKY_DIRECTORY = pathlib.Path.home() / "bluesky"
# put bluesky directory on the import path
sys.path.append(str(BLUESKY_DIRECTORY))

# terse error dumps (Exception tracebacks)
get_ipython().run_line_magic('xmode', 'Minimal')

from instrument.collection import *
