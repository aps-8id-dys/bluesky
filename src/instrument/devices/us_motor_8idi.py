"""
Define motors on the upstream of 8idi sample stage
"""

from ophyd import EpicsMotor, Device, Component

class Cam_Stage(Device):
  x = Component(EpicsMotor, 'm13', name='nu')
  y = Component(EpicsMotor, 'm12', name='delta')

cam_stage_8idi = Cam_Stage("8ide:", name="huber")