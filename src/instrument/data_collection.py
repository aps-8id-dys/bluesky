"""
configure for data collection in a console session
"""

from apstools.utils import *  # noqa

from .utils.iconfig_loader import iconfig
from .callbacks.spec_data_file_writer import specwriter
from .initialize_bs_tools import RE
from .devices import *  # noqa
from .plans import *  # noqa
import hdf5plugin  # noqa

## ipython helpers
from .utils.mpl_helper import *  # noqa
from .utils.session_logs import logger

logger.info(__file__)

if iconfig.get("WRITE_SPEC_DATA_FILES", False):
    if specwriter is not None:
        RE.subscribe(specwriter.receiver)  # noqa
        logger.info(f"writing to SPEC file: {specwriter.spec_filename}")
        logger.info("   >>>>   Using default SPEC file name   <<<<")
        logger.info("   file will be created when bluesky ends its next scan")
        logger.info("   to change SPEC file, use command:   newSpecFile('title')")

logger.info("#### data collection tools are loaded is complete. ####")
