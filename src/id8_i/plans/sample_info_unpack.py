"""
Plan that does sample select and reading of json dictionary that contains the sample info
"""

import json

import bluesky.plan_stubs as bps
import numpy as np
from apsbits.core.instrument_init import oregistry

sample = oregistry["sample"]
rheometer = oregistry["rheometer"]
filter_8idi = oregistry["filter_8idi"]
pv_registers = oregistry["pv_registers"]


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
    elif env >= 1 and env <= 27:
        yield from bps.mv(sample.x, x_cen, sample.y, y_cen)
    else:
        pass

    yield from bps.mv(pv_registers.qnw_index, env)


def sort_qnw():
    qnw_index = int(pv_registers.qnw_index.get())
    sample_key = f"sample_{qnw_index}"
    with open("/home/beams/8IDIUSER/bluesky/user_plans/sample_info.json", "r") as f:
        loaded_dict = json.load(f)

    sam_dict = {}
    sam_dict["qnw_index"] = int(pv_registers.qnw_index.get())
    sam_dict["meas_num"] = int(pv_registers.measurement_num.get())
    sam_dict["sample_name"] = loaded_dict[sample_key]["sample_name"]
    sam_dict["header"] = loaded_dict[sample_key]["header"]
    sam_dict["x_cen"] = float(loaded_dict[sample_key]["x_cen"])
    sam_dict["y_cen"] = float(loaded_dict[sample_key]["y_cen"])
    sam_dict["x_radius"] = float(loaded_dict[sample_key]["x_radius"])
    sam_dict["y_radius"] = float(loaded_dict[sample_key]["y_radius"])
    sam_dict["x_pts"] = int(loaded_dict[sample_key]["x_pts"])
    sam_dict["y_pts"] = int(loaded_dict[sample_key]["y_pts"])
    sam_dict["temp_zone"] = loaded_dict[sample_key]["temp_zone"]

    return sam_dict


def gen_folder_prefix():
    sam_dict = sort_qnw()
    pv_registers.measurement_num.put(int(sam_dict["meas_num"]) + 1)
    pv_registers.sample_name.put(sam_dict["sample_name"])
    sample_name = pv_registers.sample_name.get()

    att_level = int(filter_8idi.attenuation_readback.get())

    header_name = f'{sam_dict["header"]}{sam_dict["meas_num"]:04d}'
    folder_name = f"{header_name}_{sample_name}_a{att_level:04}"
    print(folder_name)

    return folder_name


def mesh_grid_move():
    sam_dict = sort_qnw()

    sample_pos_register = pv_registers.sample_position_register(sam_dict["qnw_index"])
    sam_pos = int(sample_pos_register.get())

    samx_list = np.linspace(
        sam_dict["x_cen"] - sam_dict["x_radius"],
        sam_dict["x_cen"] + sam_dict["x_radius"],
        num=sam_dict["x_pts"],
    )
    samy_list = np.linspace(
        sam_dict["y_cen"] - sam_dict["y_radius"],
        sam_dict["y_cen"] + sam_dict["y_radius"],
        num=sam_dict["y_pts"],
    )

    pos_index = np.mod(sam_pos + 1, sam_dict["x_pts"] * sam_dict["y_pts"])
    x_pos = samx_list[np.mod(pos_index, sam_dict["x_pts"])]
    y_pos = samy_list[int(np.floor(pos_index / sam_dict["x_pts"]))]

    if sam_dict["qnw_index"] == 0:
        yield from bps.mv(rheometer.x, x_pos, rheometer.y, y_pos)
    elif sam_dict["qnw_index"] >= 1 and sam_dict["qnw_index"] <= 27:
        yield from bps.mv(sample.x, x_pos, sample.y, y_pos)
    else:
        pass

    yield from bps.mv(sample_pos_register, pos_index)
