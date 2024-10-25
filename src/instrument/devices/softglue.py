
from ophyd import Component, Device, EpicsSignal

class SoftGlue(Device):
    
    # avoid the name 'trigger' since Device has a '.trigger()' method.
    sg_trigger = Component(EpicsSignal, "8idi:softGlueA:MUX2-1_IN0_Signal")
    acq_time = Component(EpicsSignal, "8idi:SGControl1.C")
    acq_period = Component(EpicsSignal, "8idi:SGControl1.A")

softglue_8idi = SoftGlue("", name="softglue_8idi")

