"""
Define motors in Huber diffractometer
"""

from ophyd import EpicsMotor, Device, Component


class Huber_Diffractometer(Device):
  nu = Component(EpicsMotor, 'm4', name='nu')
  delta = Component(EpicsMotor, 'm5', name='delta')
  mu = Component(EpicsMotor, 'm6', name='mu')
  eta = Component(EpicsMotor, 'm7', name='eta')
  chi = Component(EpicsMotor, 'm8', name='chi')
  phi = Component(EpicsMotor, 'm9', name='phi')
  sample_y = Component(EpicsMotor, 'm10', name='sample_y')
  sample_z = Component(EpicsMotor, 'm11', name='sample_z')
  sample_x = Component(EpicsMotor, 'm15', name='sample_x')


huber = Huber_Diffractometer("8ideSoft:CR8-E1:", name="huber")