from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignalRO


class Mono(Device):
    energy_readback = Component(EpicsSignalRO, "BraggERdbkAO", name="energy_readback")


mono_8id = Mono("8idaSoft:", name="mono_8id")
