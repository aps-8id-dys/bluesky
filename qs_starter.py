"""
Load devices and plans for bluesky queueserver.
"""

import pathlib, sys

sys.path.append(
    str(pathlib.Path(__file__).absolute().parent)
)

from instrument import iconfig
from instrument.queueserver import *

# turn down the exception-reporting noise
_xmode_level = iconfig.get("XMODE_DEBUG_LEVEL")
if _xmode_level is not None:
    try:
        from IPython import get_ipython

        get_ipython().run_line_magic('xmode', _xmode_level)
        logger.info("xmode exception level: '%s'", _xmode_level)
    except Exception:
        pass  # fail silently
del _xmode_level

print_instrument_configuration()
print_devices_and_signals()
print_plans()
print_RE_metadata()
