"""
configure for data collection in a console session
"""

from __future__ import annotations

from aps_8id_bs_instrument.session_logs import logger

logger.info(__file__)

# conda environment name
import os

_conda_prefix = os.environ.get("CONDA_PREFIX")
if _conda_prefix is not None:
    logger.info("CONDA_PREFIX = %s", _conda_prefix)
del _conda_prefix

from IPython import get_ipython

from aps_8id_bs_instrument import iconfig

# terse error dumps (Exception tracebacks)
_ip = get_ipython()
if _ip is not None:
    _xmode_level = iconfig.get("XMODE_DEBUG_LEVEL", "Minimal")
    _ip.run_line_magic("xmode", _xmode_level)
    logger.info("xmode exception level: '%s'", _xmode_level)
    del _ip


logger.info("#### Bluesky Framework ####")
from aps_8id_bs_instrument.framework import *

logger.info("#### Devices ####")
from aps_8id_bs_instrument.devices import *

logger.info("#### Callbacks ####")
from aps_8id_bs_instrument.callbacks import *

logger.info("#### Plans ####")
from aps_8id_bs_instrument.plans import *

logger.info("#### Utilities ####")
from apstools.utils import *

from aps_8id_bs_instrument._iconfig import iconfig
from aps_8id_bs_instrument.utils import *

if iconfig.get("WRITE_SPEC_DATA_FILES", False):
    if specwriter is not None:
        RE.subscribe(specwriter.receiver)
        logger.info(f"writing to SPEC file: {specwriter.spec_filename}")
        logger.info("   >>>>   Using default SPEC file name   <<<<")
        logger.info("   file will be created when bluesky ends its next scan")
        logger.info("   to change SPEC file, use command:   newSpecFile('title')")

# last line: ensure we have the console's logger
from .session_logs import logger

logger.info("#### Startup is complete. ####")
