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
import epics as pe

from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import sample
from ..devices.qnw_vac_device import qnw_vac1
from ..devices.qnw_vac_device import qnw_vac2
from ..devices.qnw_vac_device import qnw_vac3


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

    pe.caput("8idi:StrReg22", str(env))


def sort_qnw():
    meas_num = int(pe.caget("8idi:StrReg21", as_string=True))
    qnw_index = int(pe.caget("8idi:StrReg22", as_string=True))
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

    if qnw_index <= 9:
        str_index = f"8idi:Reg{int(190+qnw_index)}"
    else:
        str_index = "8idi:Reg191"

    # For ambient QNW
    # if (qnw_index == 1) or (qnw_index == 2) or (qnw_index == 3):
    #     temp = qnw_env1.readback.get()
    # elif (qnw_index == 4) or (qnw_index == 5) or (qnw_index == 6):
    #     temp = qnw_env2.readback.get()
    # else:
    #     temp = qnw_env3.readback.get()

    # For vacuum QNW
    if (qnw_index == 1) or (qnw_index == 2) or (qnw_index == 3):
        temp = qnw_vac1.readback.get()
    elif (qnw_index == 4) or (qnw_index == 5) or (qnw_index == 6):
        temp = qnw_vac2.readback.get()
    else:
        temp = qnw_vac3.readback.get()

    header_name = f"{header}{meas_num:03d}"

    pe.caput("8idi:StrReg21", str(meas_num + 1))

    return (
        header_name,
        str_index,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    )
