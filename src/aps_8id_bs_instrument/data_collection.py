"""
configure for data collection in a console session
"""

import os

from apstools.utils import *  # noqa

from .devices import *  # noqa
from .plans import *  # noqa

## ipython helpers
from .utils.mpl_helper import *  # noqa
from .utils.session_logs import logger

# from .initialize import *  # noqa

logger.info(__file__)



logger.info("#### data collection tools are loaded. ####")
