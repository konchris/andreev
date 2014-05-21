# -*- coding: utf-8 -*-
"""
Created on Wed May 21 15:23:32 2014

@author: David Weber
"""
import numpy as np
_radius = 3
for angle in [0,90,180,270,360,450,630]:
    b_1 = np.cos(np.deg2rad(angle))*_radius
    b_2 = np.sin(np.deg2rad(angle))*_radius 
    print "angle: %i, z: %f, x: %f"%(angle,round(b_1),round(b_2))
    
"""
angle: 0, z: 3.000000, x: 0.000000
angle: 90, z: 0.000000, x: 3.000000
angle: 180, z: -3.000000, x: 0.000000
angle: 270, z: -0.000000, x: -3.000000
angle: 360, z: 3.000000, x: -0.000000
angle: 450, z: 0.000000, x: 3.000000
angle: 630, z: -0.000000, x: -3.000000
"""