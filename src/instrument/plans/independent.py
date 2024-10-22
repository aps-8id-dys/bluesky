"""
Independent plans.

.. autosummary::
    ~simple_acquire
"""

import pathlib

from apstools.devices import DM_WorkflowConnector
from apstools.utils import share_bluesky_metadata_with_dm
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp

from ..callbacks.nexus_data_file_writer import nxwriter
from ..devices.ad_eiger_4M import eiger4M
from ..initialize_bs_tools import cat

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


def kickoff_dm_workflow(experiment_name, file_name, qmap_file, run):
    """Start a DM workflow for this bluesky run."""
    workflow_name = "xpcs8-02-gladier-boost"
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    yield from bps.mv(dm_workflow.concise_reporting, True)
    yield from bps.mv(dm_workflow.reporting_period, 10)  # seconds between updates

    # DM argsDict content
    argsDict = dict(
        filePath=file_name,
        experimentName=experiment_name,
        qmap=qmap_file,
        # from the plan's API
        # smooth=wf_smooth,
        # gpuID=wf_gpuID,
        # beginFrame=wf_beginFrame,
        # endFrame=wf_endFrame,
        # strideFrame=wf_strideFrame,
        # avgFrame=wf_avgFrame,
        # type=wf_type,
        # dq=wf_dq,
        # verbose=wf_verbose,
        # saveG2=wf_saveG2,
        # overwrite=wf_overwrite,
        # analysisMachine=analysisMachine,
    )

    # TODO: How to turn off __all__ reporting about the workflow?
    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=False,
        timeout=999_999_999_999,  # TODO:
        **argsDict,
    )

    # upload bluesky run metadata to APS DM
    share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

    # TODO: print the workflow process id.


def full_acquisition():
    """These are the data acquisition steps for a user."""
    det = eiger4M
    yield from setup_detector(det, 0.1, 1000, "A001_001")

    uids = yield from simple_acquire(det)
    print(f"Bluesky run: {uids=}")
    run = cat[uids[0]]

    try:
        yield from nxwriter.wait_writer_plan_stub()
        yield from kickoff_dm_workflow(
            "my_dm_experiment",
            pathlib.Path(det.hdf1.full_file_name.get()).name,
            "my_qmap_file.h5",
            run,
        )
    except Exception as exc:
        print(f"Exception: {exc}")
