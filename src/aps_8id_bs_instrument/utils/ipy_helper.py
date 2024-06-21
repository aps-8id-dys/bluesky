"""ipython helper functions"""

from bluesky.magics import BlueskyMagics
from IPython import get_ipython

from .. import iconfig
from .session_logs import logger

logger.info(__file__)
_ip = get_ipython()

if _ip is not None:
    _xmode_level = iconfig.get("XMODE_DEBUG_LEVEL", "Minimal")
    _ip.register_magics(BlueskyMagics)
    _ip.run_line_magic("xmode", _xmode_level)
    logger.info("xmode exception level: '%s'", _xmode_level)
    del _ip
