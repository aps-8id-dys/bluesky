"""
Independent plans.

.. autosummary::
    ~simple_acquire
"""

from bluesky import plans as bp
from bluesky import preprocessors as bpp

from ..callbacks.nexus_data_file_writer import nxwriter

TITLE = "acquire_detector"  # keep this short, single-word
DESCRIPTION = "Modular plan for area detector acquisition."
DEFAULT_RUN_METADATA = {
    "title": TITLE,
    "description": DESCRIPTION,
    "cycle": "2024-3",
}


def simple_acquire(det, md: dict = DEFAULT_RUN_METADATA):
    """
    Run the data acquisition with the chosen detector.

    Only does the following:

    - Start the cam module to acquire.
    """

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
