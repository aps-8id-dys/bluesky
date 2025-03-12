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
from ..devices.aerotech_stages import sample, rheometer
from ..devices.registers_device import pv_registers
from ..devices.qnw_device import qnw_env1, qnw_env2, qnw_env3
# from ..devices.qnw_vac_device import qnw_vac1, qnw_vac2, qnw_vac3

def select_sample(env: int):
    # yield from bps.mv(eiger4M.cam.acquire_time, 0.1)
    # yield from bps.mv(eiger4M.cam.acquire_period, 0.1)
    # yield from bps.mv(eiger4M.cam.num_images, 1)

    with open("/home/beams/8IDIUSER/bluesky/user_plans/sample_info.json", "r") as f:
        loaded_dict = json.load(f)

    sample_key = f"sample_{env}"
    x_cen = loaded_dict[sample_key]["x_cen"]
    y_cen = loaded_dict[sample_key]["y_cen"]

    print(f"Moving {sample_key} x to {x_cen} and y to {y_cen}")

    if env == 0:
        yield from bps.mv(rheometer.x, x_cen, rheometer.y, y_cen)
    elif env >=1 and env <=27:
        yield from bps.mv(sample.x, x_cen, sample.y, y_cen)
    else:
        pass

    yield from bps.mv(pv_registers.qnw_index, env)


def sort_qnw():
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
    temp_zone = loaded_dict[sample_key]["temp_zone"]
   
    # TODO: rewrite this IF block using getattr as in 'registers_device.py'
    # For air qnw 
    if temp_zone == 'qnw_env1':
        temp = qnw_env1.readback.get()
    elif temp_zone == 'qnw_env2':
        temp = qnw_env2.readback.get()
    else:
        temp = qnw_env3.readback.get()

    # For vacuum QNW
    # if (qnw_index == 1) or (qnw_index == 2) or (qnw_index == 3):
    #     temp = qnw_vac1.readback.get()
    # elif (qnw_index == 4) or (qnw_index == 5) or (qnw_index == 6):
    #     temp = qnw_vac2.readback.get()
    # else:
    #     temp = qnw_vac3.readback.get()

    header_name = f"{header}{meas_num:04d}"

    return (
        header_name,
        meas_num,
        qnw_index,
        temp,
        sample_name,
        x_cen,
        y_cen,
        x_radius,
        y_radius,
        x_pts,
        y_pts,
    )
