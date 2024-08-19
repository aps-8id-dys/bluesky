"""
define standard experiment metadata
"""

import getpass
import logging
import os
import pathlib
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

from ..utils.iconfig_loader import iconfig

logger = logging.getLogger(__name__)
logger.info(__file__)


HOSTNAME = socket.gethostname() or "localhost"
USERNAME = getpass.getuser() or "Bluesky user"
VERSIONS = dict(
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


def get_md_path():
    """Get metadata path on run_engine"""
    path = iconfig.get("RUNENGINE_MD_PATH")
    if path is None:
        path = pathlib.Path.home() / ".config" / "Bluesky_RunEngine_md"
    else:
        path = pathlib.Path(path)
    logger.info("RunEngine metadata saved in directory: %s", str(path))
    return str(path)


MD_PATH = get_md_path()


def metadata(RE, cat):
    """Write metadata on the Run Engine"""
    # Set up default metadata
    RE.md["databroker_catalog"] = cat.name
    RE.md["login_id"] = USERNAME + "@" + HOSTNAME
    RE.md.update(iconfig.get("RUNENGINE_METADATA", {}))
    RE.md["versions"] = VERSIONS
    RE.md["pid"] = os.getpid()
    RE.md["iconfig"] = iconfig

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix is not None:
        RE.md["conda_prefix"] = conda_prefix
    del conda_prefix

    return RE
