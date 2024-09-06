"""
configure for data collection in a console session
"""

from apstools.utils import *  # noqa

from .callbacks import specwriter  # noqa
from .devices import *  # noqa
from .plans import *  # noqa

## ipython helpers
from .utils.session_logs import logger

logger.info(__file__)

logger.info("#### data collection tools loading is complete. ####")
