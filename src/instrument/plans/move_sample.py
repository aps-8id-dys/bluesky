

from ..devices.aerotech_stages import sample, rheometer
from ..devices.registers_device import pv_registers
from bluesky import plan_stubs as bps

import numpy as np

def mesh_grid_move(
    sam_index,
    x_cen,
    x_radius, 
    x_pts,
    y_cen,
    y_radius,
    y_pts 
):
    sample_pos_register = pv_registers.sample_position_register(sam_index)
    sam_pos = int(sample_pos_register.get())
    
    samx_list = np.linspace(x_cen - x_radius, x_cen + x_radius, num=x_pts)
    samy_list = np.linspace(y_cen - y_radius, y_cen + y_radius, num=y_pts)

    pos_index = np.mod(sam_pos+1, x_pts * y_pts)
    x_pos = samx_list[np.mod(pos_index, x_pts)]
    y_pos = samy_list[int(np.floor(pos_index / y_pts))]

    if sam_index == 0:
        yield from bps.mv(rheometer.x, x_pos, rheometer.y, y_pos)
    elif sam_index >=1 and sam_index<=27:
        yield from bps.mv(sample.x, x_pos, sample.y, y_pos)
        print(x_pos, y_pos)
    else:
        pass

    yield from bps.mv(sample_pos_register, pos_index)
 



