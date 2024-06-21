"""
configure for data collection in a console session
"""

import os

from apstools.utils import *  # noqa

from . import iconfig
from .callbacks.spec_data_file_writer import specwriter
from .devices import *  # noqa
from .initialize import RE
from .plans import *  # noqa
from .utils.ipy_helpers import *  # noqa
from .utils.mpl_helper import *  # noqa
from .utils.session_logs import logger

logger.info(__file__)

# conda environment name
_conda_prefix = os.environ.get("CONDA_PREFIX")
if _conda_prefix is not None:
    logger.info("CONDA_PREFIX = %s", _conda_prefix)
del _conda_prefix


if iconfig.get("WRITE_SPEC_DATA_FILES", False):
    if specwriter is not None:
        RE.subscribe(specwriter.receiver)
        logger.info(f"writing to SPEC file: {specwriter.spec_filename}")
        logger.info("   >>>>   Using default SPEC file name   <<<<")
        logger.info("   file will be created when bluesky ends its next scan")
        logger.info("   to change SPEC file, use command:   newSpecFile('title')")


logger.info("#### Startup is complete. ####")
