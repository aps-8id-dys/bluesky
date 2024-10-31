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

import time
import json

import bluesky.plan_stubs as bps

from ..devices import eiger4M
from ..devices import pv_registers
from ..devices import sample
from ..devices import qnw_env1, qnw_env2, qnw_env3


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
   
    if qnw_index == 1 or 2 or 3:
        temp = qnw_env1.setpoint.get()
    if qnw_index == 4 or 5 or 6:
        temp = qnw_env2.setpoint.get()
    if qnw_index == 7 or 8 or 9:
        temp = qnw_env3.setpoint.get()
 
    header_name = f"{header}{meas_num:03d}"

    yield from bps.mv(pv_registers.measurement_num, str(meas_num+1))

    return header_name, temp, sample_name, x_cen, y_cen, x_radius, y_radius, x_pts, y_pts