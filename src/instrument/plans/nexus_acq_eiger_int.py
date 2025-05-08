"""
Simple, modular Bluesky plans for users.
"""

from bluesky import plan_stubs as bps
from bluesky import plans as bp

from ..devices.ad_eiger_4M import eiger4M
from ..devices.registers_device import pv_registers
from .dm_util import dm_run_job
from .dm_util import dm_setup
from .nexus_utils import create_nexus_format_metadata
from .sample_info_unpack import gen_folder_prefix
from .sample_info_unpack import mesh_grid_move
from .shutter_logic import blockbeam
from .shutter_logic import post_align
from .shutter_logic import showbeam
from .shutter_logic import shutteroff


def setup_eiger_int_series(acq_time, num_frames, file_name):
    """Setup the Eiger4M cam module for internal acquisition (0) mode and populate the hdf plugin"""
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()

    file_path = f"/gdata/dm/8IDI/{cycle_name}/{exp_name}/data/{file_name}"

    acq_period = acq_time
    yield from bps.mv(eiger4M.cam.trigger_mode, "Internal Series")  # 0
    yield from bps.mv(eiger4M.cam.acquire_time, acq_time)
    yield from bps.mv(eiger4M.cam.acquire_period, acq_period)
    yield from bps.mv(eiger4M.hdf1.file_name, file_name)
    yield from bps.mv(eiger4M.hdf1.file_path, file_path)
    yield from bps.mv(eiger4M.cam.num_images, num_frames)
    yield from bps.mv(
        eiger4M.cam.num_triggers, 1
    )  # Need to put num_trigger to 1 for internal mode
    yield from bps.mv(eiger4M.hdf1.num_capture, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, file_path)
    yield from bps.mv(
        pv_registers.metadata_full_path, f"{file_path}/{file_name}_metadata.hdf"
    )


def eiger_acq_int_series(
    acq_time=1, num_frames=10, num_rep=3, wait_time=0, process=True, sample_move=False
):
    try:
        yield from post_align()
        yield from shutteroff()
        workflowProcApi, dmuser = dm_setup(process)
        folder_prefix = gen_folder_prefix()

        for ii in range(num_rep):
            yield from bps.sleep(wait_time)

            if sample_move:
                yield from mesh_grid_move()

            file_name = f"{folder_prefix}_f{num_frames:06d}_r{ii+1:05d}"
            yield from setup_eiger_int_series(acq_time, num_frames, file_name)

            yield from showbeam()
            yield from bps.sleep(0.1)
            yield from bp.count([eiger4M])
            yield from blockbeam()

            metadata_fname = pv_registers.metadata_full_path.get()
            create_nexus_format_metadata(metadata_fname, det=eiger4M)

            dm_run_job("eiger", process, workflowProcApi, dmuser, file_name)
    except Exception as e:
        print(f"Error occurred during measurement: {e}")
    finally:
        pass
