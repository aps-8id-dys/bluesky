"""
configure for data collection in a console session
"""

import os

from apstools.utils import *  # noqa
from IPython import get_ipython

from . import iconfig
from .callbacks import *  # noqa
from .devices import *  # noqa
from .initialize import *  # noqa
from .plans import *  # noqa
from .utils.mpl import *  # noqa
from .utils.session_logs import logger

logger.info(__file__)

# conda environment name
_conda_prefix = os.environ.get("CONDA_PREFIX")
if _conda_prefix is not None:
    logger.info("CONDA_PREFIX = %s", _conda_prefix)
del _conda_prefix

# terse error dumps (Exception tracebacks)
_ip = get_ipython()
if _ip is not None:
    _xmode_level = iconfig.get("XMODE_DEBUG_LEVEL", "Minimal")
    _ip.run_line_magic("xmode", _xmode_level)
    logger.info("xmode exception level: '%s'", _xmode_level)
    del _ip


if iconfig.get("WRITE_SPEC_DATA_FILES", False):
    if specwriter is not None:
        RE.subscribe(specwriter.receiver)
        logger.info(f"writing to SPEC file: {specwriter.spec_filename}")
        logger.info("   >>>>   Using default SPEC file name   <<<<")
        logger.info("   file will be created when bluesky ends its next scan")
        logger.info("   to change SPEC file, use command:   newSpecFile('title')")


logger.info("#### Startup is complete. ####")
