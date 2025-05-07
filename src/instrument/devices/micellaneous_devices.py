from ophyd import EpicsMotor, EpicsSignal, EpicsSignalRO, Device, Component


class Cam_Stage(Device):
  x = Component(EpicsMotor, 'm13', name='cam_x')
  y = Component(EpicsMotor, 'm12', name='cam_y')
cam_stage_8idi = Cam_Stage("8ide:", name="cam_stage_8idi")

class Mono(Device):
  energy_readback = Component(EpicsSignalRO, 'BraggERdbkAO', name='energy_readback')
mono_8id = Mono("8idaSoft:", name="mono_8id")

class Flight_Path(Device):
  length = Component(EpicsMotor, 'm1', name='length')
flight_path_8idi = Flight_Path("8idiSoft:FLIGHT:", name="flight_path_8idi")

