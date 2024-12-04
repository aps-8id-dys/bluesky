"""
EPICS PVs as Storage registers.
"""

from bluesky import plan_stubs as bps
from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class EpicsPvStorageRegisters(Device):

    file_name = Component(EpicsSignal, "StrReg1", string=True)
    file_path = Component(EpicsSignal, "StrReg2", string=True)
    metadata_full_path = Component(EpicsSignal, "StrReg3", string=True)
    qmap_file = Component(EpicsSignal, "StrReg4", string=True)
    analysis_machine = Component(EpicsSignal, "StrReg5", string=True)
    workflow_name = Component(EpicsSignal, "StrReg6", string=True)
    experiment_name = Component(EpicsSignal, "StrReg7", string=True)
    cycle_name = Component(EpicsSignal, "StrReg8", string=True)
    sample_name = Component(EpicsSignal, "StrReg9", string=True)

    measurement_num = Component(EpicsSignal, "Reg1")
    qnw_index = Component(EpicsSignal, "Reg2")

    sample1_pos = Component(EpicsSignal, "Reg11")
    sample2_pos = Component(EpicsSignal, "Reg12")
    sample3_pos = Component(EpicsSignal, "Reg13")
    sample4_pos = Component(EpicsSignal, "Reg14")
    sample5_pos = Component(EpicsSignal, "Reg15")
    sample6_pos = Component(EpicsSignal, "Reg16")
    sample7_pos = Component(EpicsSignal, "Reg17")
    sample8_pos = Component(EpicsSignal, "Reg18")
    sample9_pos = Component(EpicsSignal, "Reg19")

    def sample_position_register(self, qnw_index):
        """
        Return the indexed sample position register signal.

        Replaces: PyEpics calls involving f"8idi:Reg{int(190+qnw_index)}"
        """
        if qnw_index <= 9:
            return getattr(self, f"sample{qnw_index}_pos")
        else:
            return getattr(self, f"sample9_pos")


pv_registers = EpicsPvStorageRegisters("8idiSoft:", name="pv_registers")