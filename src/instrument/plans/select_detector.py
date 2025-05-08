
import bluesky.plan_stubs as bps

from ..devices.aerotech_stages import detector
from ..devices.registers_device import pv_registers


def select_detector(det: str):

    if det == "eiger":
        yield from bps.mv(pv_registers.workflow_name, 'xpcs8-boost-corr')
        yield from bps.mv(pv_registers.qmap_file, 'eiger4m_qmap_default.h5')

        det_x_position = pv_registers.eiger_det_x0.get()
        det_y_position = pv_registers.eiger_det_y0.get()
        db_x_coord = pv_registers.eiger_db_x0.get()
        db_y_coord = pv_registers.eiger_db_y0.get()

        yield from bps.mv(pv_registers.current_det_x0, det_x_position)
        yield from bps.mv(pv_registers.current_det_y0, det_y_position)
        yield from bps.mv(pv_registers.current_db_x0, db_x_coord)
        yield from bps.mv(pv_registers.current_db_y0, db_y_coord)
        yield from bps.mv(detector.x, det_x_position)
        yield from bps.mv(detector.y, det_y_position)

    elif det == "rigaku":
        yield from bps.mv(pv_registers.workflow_name, 'xpcs8-boost-corr')
        yield from bps.mv(pv_registers.qmap_file, 'rigaku3m_qmap_default.h5')

        det_x_position = pv_registers.rigaku_det_x0.get()
        det_y_position = pv_registers.rigaku_det_y0.get()
        db_x_coord = pv_registers.rigaku_db_x0.get()
        db_y_coord = pv_registers.rigaku_db_y0.get()

        yield from bps.mv(pv_registers.current_det_x0, det_x_position)
        yield from bps.mv(pv_registers.current_det_y0, det_y_position)
        yield from bps.mv(pv_registers.current_db_x0, db_x_coord)
        yield from bps.mv(pv_registers.current_db_y0, db_y_coord)

        yield from bps.mv(detector.x, det_x_position)
        yield from bps.mv(detector.y, det_y_position)

    else:
        print('Detector name must be eiger4M or rigaku3M')

