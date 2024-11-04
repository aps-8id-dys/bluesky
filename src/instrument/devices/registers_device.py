"""
EPICS PVs as Storage registers.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class EpicsPvStorageRegisters(Device):
    """Various instrument constants and parameters are defined in PVs."""
    measurement_num = Component(EpicsSignal, "StrReg21", string=True)
    qnw_index = Component(EpicsSignal, "StrReg22", string=True)
    qmap_file = Component(EpicsSignal, "StrReg23", string=True)
    image_file_name = Component(EpicsSignal, "StrReg24", string=True)
    experiment_name = Component(EpicsSignal, "StrReg25", string=True)
    cycle_name = Component(EpicsSignal, "StrReg26", string=True)
    workflow_name = Component(EpicsSignal, "StrReg27", string=True)
    analysis_machine = Component(EpicsSignal, "StrReg29", string=True)
    # TODO StrReg28?
    # metadata_file = Component(EpicsSignal, "StrReg27", string=True)  # FIXME: same as workflow_name
    full_file_name = Component(EpicsSignal, "StrReg30", string=True)

    # TODO:
    # str_index = f"8idi:Reg{int(190+qnw_index)}"
    # pe.caput(str_index, pos_index)


pv_registers = EpicsPvStorageRegisters("8idi:", name="pv_registers")
