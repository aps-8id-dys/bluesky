"""
The BCDA SoftGlue FPGA generates pulses to trigger an area detector.

Example acquisition sequence::

    fpga = SoftGlue("", name="fpga")
    ...
    # configure fpga & area_detector
    ...
    yield from bps.mv(fpga.start_pulses, "1!")
    yield from bp.count([area_detector])
    yield from bps.mv(fpga.stop_pulses, "1!")

"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class SoftGlue(Device):
    """
    BCDA SoftGlue FPGA to provide external trigger signal for detectors.

    The value to write to start & stop is the same text: 1!
    """

    acq_period = Component(EpicsSignal, "8idi:SGControl1.A", kind="config")
    acq_time = Component(EpicsSignal, "8idi:SGControl1.C", kind="config")
    num_triggers = Component(EpicsSignal, "8idi:SGControl1.J", kind="config")
    stop_trigger = Component(
        EpicsSignal, "8idi:softGlueA:OR-1_IN2_Signal", kind="config"
    )

    start_pulses = Component(
        EpicsSignal,
        "8idi:softGlueA:MUX2-1_IN0_Signal",
        kind="omitted",
        string=True,
    )

    stop_pulses = Component(
        EpicsSignal,
        "8idi:softGlueA:OR-1_IN2_Signal",
        kind="omitted",
        string=True,
    )


softglue_8idi = SoftGlue("", name="softglue_8idi")
