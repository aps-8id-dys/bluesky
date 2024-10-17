"""
XPCS plans use some ophyd Signals that are not EPICS PVs.

.. automodule::
    ~xpcs_dm
"""

import logging
import pathlib

from apstools.utils import dm_api_ds
from bluesky import plan_stubs as bps
from ophyd import Component
from ophyd import Device
from ophyd import Signal

logger = logging.getLogger(__name__)
logger.info(__file__)

from ..initialize_bs_tools import RE  # noqa: E402


class XPCS_Plan_Signals_Device(Device):
    """
    Signals and methods used in XPCS Data Acquisition Plans with DM workflows.

    .. rubric:: Signals
    .. automodule::
        ~experiment_name
        ~header
        ~index

    .. rubric:: Methods
    .. automodule::
        ~data_path
        ~filename_base
        ~increment_index
        ~reset_index

    .. rubric:: Properties
    .. automodule::
        ~header_index_str
    """

    experiment_name = Component(Signal, value="")
    """Name of the current APS Data Management experiment."""

    header = Component(Signal, value=RE.md.get("xpcs_header", "A001"))
    """Identify a set of related measurements, such as "B123"."""

    index = Component(Signal, value=RE.md.get("xpcs_index", 0))
    """Increments at the start of each data acquisition plan."""

    def data_path(self, title: str, nframes: int = 0):
        """Return _this_ DM experiment's data directory."""
        experiment = dm_api_ds().getExperimentByName(self.experiment_name.get())
        path = pathlib.Path(experiment["dataDirectory"])
        filepath = path / self.filename_base(title, nframes)
        # return f"{experiment['dataDirectory']}/{self.filename_base(title, nframes)}"
        return filepath

    def filename_base(self, title: str, nframes: int = 0):
        """Return the base part of the filename."""
        return f"{self.header_index_str}_{title}-{nframes:05d}"

    def full_filename(self, title: str, suffix: str = ".hdf", nframes: int = 0):
        """Return the full filename."""
        base = self.filename_base(title, nframes)
        path = self.data_path(title, nframes)
        return path / f"{base}{suffix}"

    @property
    def header_index_str(self):
        """Return a formatted string with the header and index."""
        return f"{self.header.get()}_{self.index.get():03d}"

    def increment_index(self):
        """stub: Increment the index for the next run."""
        yield from bps.mvr(self.index, 1)

    def reset_index(self, index: int = 0):
        """
        stub: (Re)set the 'index'.  Default=0.

        Data directory and file names are defined by the 'header' and
        the`index'.
        """
        yield from bps.mv(self.index, index)


xpcs_dm = XPCS_Plan_Signals_Device(name="xpcs_dm")  # TODO: pick a better name
"""Signals used in XPCS Data Acquisition Plans with DM workflows."""
