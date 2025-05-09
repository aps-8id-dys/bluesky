"""
Simple, modular Bluesky plans for users.
"""

from apsbits.core.instrument_init import oregistry
from bluesky import plan_stubs as bps
from bluesky import plans as bp

from ..utils.dm_util import dm_run_job
from ..utils.dm_util import dm_setup
from .nexus_utils import create_nexus_format_metadata
from .sample_info_unpack import gen_folder_prefix
from .sample_info_unpack import mesh_grid_move
from .shutter_logic import blockbeam
from .shutter_logic import post_align
from .shutter_logic import showbeam
from .shutter_logic import shutteron

eiger4M = oregistry["eiger4M"]
softglue_8idi = oregistry["softglue_8idi"]
pv_registers = oregistry["pv_registers"]


def setup_eiger_ext_trig(acq_time, acq_period, num_frames, file_name):
    """Setup the Eiger4M cam module for internal acquisition (0) mode and populate the hdf plugin"""
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()

    file_path = f"/gdata/dm/8IDI/{cycle_name}/{exp_name}/data/{file_name}/"

    yield from bps.mv(eiger4M.cam.trigger_mode, "External Enable")  # 3
    yield from bps.mv(eiger4M.cam.acquire_time, acq_time)
    yield from bps.mv(eiger4M.cam.acquire_period, acq_period)
    yield from bps.mv(eiger4M.hdf1.file_name, file_name)
    yield from bps.mv(eiger4M.hdf1.file_path, file_path)
    # In External trigger mode, then num_images is not writable.
    # yield from bps.mv(eiger4M.cam.num_images, num_frames)
    yield from bps.mv(eiger4M.cam.num_triggers, num_frames)
    yield from bps.mv(eiger4M.hdf1.num_capture, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, file_path)
    yield from bps.mv(
        pv_registers.metadata_full_path, f"{file_path}/{file_name}_metadata.hdf"
    )


def setup_softglue_ext_trig(acq_time, acq_period, num_frames):
    """Setup external triggering"""
    yield from bps.mv(softglue_8idi.acq_time, acq_time)
    yield from bps.mv(softglue_8idi.acq_period, acq_period)
    # Generate n+1 triggers, in case softglue triggered before area detector.
    # Because we are also sending signal to softglue to stop the pulse train,
    # so add 10 more pulses to be on the safe side.
    yield from bps.mv(softglue_8idi.num_triggers, num_frames + 10)


def softglue_start_pulses():
    """Tell the FPGA to start generating pulses."""
    yield from bps.mv(softglue_8idi.start_pulses, "1!")


def softglue_stop_pulses():
    """Tell the FPGA to stop generating pulses."""
    yield from bps.mv(softglue_8idi.stop_pulses, "1!")


def eiger_acq_ext_trig(
    acq_time=1,
    acq_period=2,
    num_frames=10,
    num_rep=2,
    wait_time=0,
    sample_move=True,
    process=True,
):
    try:
        yield from setup_softglue_ext_trig(acq_time, acq_period, num_frames)
        yield from post_align()
        yield from shutteron()

        workflowProcApi, dmuser = dm_setup(process)
        folder_prefix = gen_folder_prefix()

        for ii in range(num_rep):
            yield from bps.sleep(wait_time)

            if sample_move:
                yield from mesh_grid_move()

            file_name = f"{folder_prefix}_f{num_frames:06d}_r{ii+1:05d}"
            yield from setup_eiger_ext_trig(acq_time, acq_period, num_frames, file_name)

            yield from showbeam()
            yield from bps.sleep(0.1)
            yield from softglue_start_pulses()
            yield from bp.count([eiger4M])
            yield from softglue_stop_pulses()
            yield from blockbeam()

            metadata_fname = pv_registers.metadata_full_path.get()
            create_nexus_format_metadata(metadata_fname, det=eiger4M)

            dm_run_job("eiger", process, workflowProcApi, dmuser, file_name)
    except Exception as e:
        print(f"Error occurred during measurement: {e}")
    finally:
        pass
