# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 21:07:15 2013

@author: David Weber
"""

upper_limit = False
lower_limit = False

def motor_thread(motor, limit=30, reduction=3088):
    position = motor.get_pos()
    if position < 0:
        motor.stop()
        upper_limit = True
    if position < -reduction*2048*limit:
        motor.stop()
        lower_limit = True