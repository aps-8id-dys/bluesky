
from ophyd import Device, Component, EpicsSignal

class SoftGlue(Device):
    trigger = Component(EpicsSignal, '8idi:softGlueA:MUX2-1_IN0_Signal', name='trigger')
    acq_time = Component(EpicsSignal, '8idi:SGControl1.C', name='acq_time')
    acq_time = Component(EpicsSignal, '8idi:SGControl1.A', name='acq_time')


softglue_8idi = SoftGlue('8idi:softGlueA:', name='my_detector')

