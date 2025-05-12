"""
Define motors in Huber diffractometer
"""

from ophyd import EpicsMotor

cam_x = EpicsMotor('8ide:m13', name='cam_x')
cam_y = EpicsMotor('8idiSoft:CR8-I2:m15', name='cam_y')