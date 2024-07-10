import logging
import time

from aps_8id_bs_instrument import iconfig
from aps_8id_bs_instrument.utils.session_logs import logger

from bluesky.magics import BlueskyMagics
from IPython import get_ipython

logging.basicConfig(level=logging.WARNING)
logger.info(__file__)

def setup_ipython():
    _ip = get_ipython()
    if _ip is not None:
        _xmode_level = iconfig.get("XMODE_DEBUG_LEVEL", "Minimal")
        _ip.register_magics(BlueskyMagics)
        _ip.run_line_magic("xmode", _xmode_level)
        logger.info("xmode exception level: '%s'", _xmode_level)
        del _ip

# Start timer
t0 = time.monotonic()

from aps_8id_bs_instrument.initialize_bs_tools import (  # noqa: F401
    RE,
    bec,
    cat,
    oregistry,
    peaks,
    sd,
)
from aps_8id_bs_instrument.data_collection import *  # noqa

print(f"Finished initialization in {time.monotonic() - t0:.2f} seconds.")

# Setup IPython
setup_ipython()
