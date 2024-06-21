"""
define standard experiment metadata
"""

__all__ = ["metadata"]

import getpass
import logging
import os
import socket

import apstools
import bluesky
import databroker
import epics
import h5py
import intake
import matplotlib
import numpy
import ophyd
import pyRestTable
import spec2nexus

from aps_8id_bs_instrument import iconfig
from aps_8id_bs_instrument.initialize import RE, cat

logger = logging.getLogger(__name__)
logger.info(__file__)


def metadata():
    HOSTNAME = socket.gethostname() or "localhost"
    USERNAME = getpass.getuser() or "Bluesky user"

    # useful diagnostic to record with all data
    versions = dict(
        apstools=apstools.__version__,
        bluesky=bluesky.__version__,
        databroker=databroker.__version__,
        epics=epics.__version__,
        h5py=h5py.__version__,
        intake=intake.__version__,
        matplotlib=matplotlib.__version__,
        numpy=numpy.__version__,
        ophyd=ophyd.__version__,
        pyRestTable=pyRestTable.__version__,
        spec2nexus=spec2nexus.__version__,
    )

    # Set up default metadata
    RE.md["databroker_catalog"] = cat.name
    RE.md["login_id"] = USERNAME + "@" + HOSTNAME
    RE.md.update(iconfig.get("RUNENGINE_METADATA", {}))
    RE.md["versions"] = versions
    RE.md["pid"] = os.getpid()
    RE.md["iconfig"] = iconfig

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix is not None:
        RE.md["conda_prefix"] = conda_prefix
    del conda_prefix

    return versions, RE.md
