"""
Independent plans.

.. autosummary::
    ~simple_acquire
"""

from bluesky import plans as bp
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp

from .ad_eiger_4M import eiger4M
from ..callbacks.nexus_data_file_writer import nxwriter
from ..initialize_bs_tools import oregistry

EMPTY_DICT = {}


def simple_acquire(det, md: dict = EMPTY_DICT):
    """Just run the acquisition, nothing else."""

    nxwriter.warn_on_missing_content = False
    # nxwriter.file_path = data_path
    # nxwriter.file_name = data_path / (file_name_base + ".hdf")

    md["metadatafile"] = nxwriter.file_name.name

    @bpp.subs_decorator(nxwriter.receiver)
    def acquire():
        yield from bp.count([det], md=md)

    yield from acquire()

    # Wait for NeXus metadata file content to flush to disk.
    # If next acquisition proceeds without waiting, the
    # metadata file will be spoiled.
    yield from nxwriter.wait_writer_plan_stub()


def setup_detector(det, acq_time, num_frames, file_name):
    """Setup the acquisition,"""
    yield from bps.mv(det.cam.acquisition_time, acq_time)
    yield from bps.mv(det.cam.number_of_frames, num_frames)
    yield from bps.mv(det.hdf1.file_name, file_name)

def full_acquisition():
    """These are the data acquisition steps for a user."""
    det = eiger4M
    yield from setup_detector(det, 0.1, 1000, "A001_001")
    yield from simple_acquire(det)
    yield from nxwriter.wait_writer_plan_stub()