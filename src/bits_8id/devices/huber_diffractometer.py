"""
Define motors in Huber diffractometer
"""

from ophyd import EpicsMotor, Device, Component


class Huber_Diffractometer(Device):
  nu = Component(EpicsMotor, 'm4', name='nu')
  phi = Component(EpicsMotor, 'm9', name='phi')


huber = Huber_Diffractometer("8ideSoft:CR8-E1:", name="huber")