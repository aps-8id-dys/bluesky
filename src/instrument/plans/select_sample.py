"""
Plan that allows for moving to pre-programmed positions seen as strings
"""

__all__ = """
    select_sample
    open_shutter
    close_shutter
    shutter_on
    shutter_off
""".split()

import json

import bluesky.plan_stubs as bps

from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import sample
from ..devices.qnw_vac_device import qnw_vac1
from ..devices.qnw_vac_device import qnw_vac2
from ..devices.qnw_vac_device import qnw_vac3
from ..devices.registers_device import pv_registers


def select_sample(env: int):
    yield from bps.mv(eiger4M.cam.acquire_time, 0.1)
    yield from bps.mv(eiger4M.cam.acquire_period, 0.1)
    yield from bps.mv(eiger4M.cam.num_images, 1)

    with open("/home/beams/8IDIUSER/bluesky/user_plans/sample_info.json", "r") as f:
        loaded_dict = json.load(f)

    sample_key = f"sample_{env}"
    x_cen = loaded_dict[sample_key]["x_cen"]
    y_cen = loaded_dict[sample_key]["y_cen"]

    print(f"Moving {sample_key} x to {x_cen} and y to {y_cen}")
    yield from bps.mv(sample.x, x_cen)
    yield from bps.mv(sample.y, y_cen)

    yield from bps.mv(pv_registers.qnw_index, str(env))


def sort_qnw():
    """
    What exactly does this function accomplish?

    AFTER it defines the long list of parameters it will return, it increments
    measurement_num.
    """

    meas_num = int(pv_registers.measurement_num.get())
    qnw_index = int(pv_registers.qnw_index.get())
    sample_key = f"sample_{qnw_index}"

    with open("/home/beams/8IDIUSER/bluesky/user_plans/sample_info.json", "r") as f:
        loaded_dict = json.load(f)

    sample_name = loaded_dict[sample_key]["sample_name"]
    header = loaded_dict[sample_key]["header"]
    x_cen = loaded_dict[sample_key]["x_cen"]
    y_cen = loaded_dict[sample_key]["y_cen"]
    x_radius = loaded_dict[sample_key]["x_radius"]
    y_radius = loaded_dict[sample_key]["y_radius"]
    x_pts = loaded_dict[sample_key]["x_pts"]
    y_pts = loaded_dict[sample_key]["y_pts"]

    # TODO: PyEpics -> ophyd
    str_index = f"8idi:Reg{int(190+qnw_index)}"
    import epics as pe
    sam_pos = int(pe.caget(str_index))

    # For ambient QNW
    # if qnw_index in (1, 2, 3):
    #     temp = qnw_env1.readback.get()
    # elif qnw_index in (4, 5, 6):
    #     temp = qnw_env2.readback.get()
    # else:
    #     temp = qnw_env3.readback.get()

    # For vacuum QNW
    if qnw_index in (1, 2, 3):
        temp = qnw_vac1.readback.get()
    elif qnw_index in (4, 5, 6):
        temp = qnw_vac2.readback.get()
    else:
        temp = qnw_vac3.readback.get()

    header_name = f"{header}{meas_num:03d}"

    yield from bps.mv(pv_registers.measurement_num, str(meas_num+1))

    return (
        header_name,
        qnw_index,
        sam_pos,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    )
