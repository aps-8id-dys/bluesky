"""
EPICS PVs as Storage registers.
"""

from bluesky import plan_stubs as bps
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

    pos_sample1 = Component(EpicsSignal, "Reg191")
    pos_sample2 = Component(EpicsSignal, "Reg192")
    pos_sample3 = Component(EpicsSignal, "Reg193")
    pos_sample4 = Component(EpicsSignal, "Reg194")
    pos_sample5 = Component(EpicsSignal, "Reg195")
    pos_sample6 = Component(EpicsSignal, "Reg196")
    pos_sample7 = Component(EpicsSignal, "Reg197")
    pos_sample8 = Component(EpicsSignal, "Reg198")
    pos_sample9 = Component(EpicsSignal, "Reg199")

    def sample_position_register(self, qnw_index):
        """
        Return the indexed sample position register signal.

        Replaces: PyEpics calls involving f"8idi:Reg{int(190+qnw_index)}"
        """
        return getattr(self, f"pos_sample{qnw_index}")


pv_registers = EpicsPvStorageRegisters("8idi:", name="pv_registers")
