# -*- coding: utf-8 -*-
"""
Created on Sun Feb 02 14:09:19 2014

@author: David Weber
"""

from tables import *
import numpy

class li_measurement_1(IsDescription):
    timestamp   =   UInt64Col()
    aux0        =   Float32Col()
    aux1        =   Float32Col()
    x           =   Float32Col()
    y           =   Float32Col()

class li_measurement_2(IsDescription):
    timestamp   =   UInt64Col()
    x           =   Float32Col()
    y           =   Float32Col()

class temperature(IsDescription):
    timestamp   =   UInt64Col()
    pot         =   Float32Col()
    sample      =   Float32Col()
    

h5file = openFile("tutorial1.h5", mode = "w", title = "Test file")

group = h5file.createGroup("/", 'lockin', 'Zurich LockIn Data')

table = h5file.createTable(group, 'ch_0', li_measurement_1, "Channel 0")
table = h5file.createTable(group, 'ch_1', li_measurement_1, "Channel 1")
table = h5file.createTable(group, 'ch_3', li_measurement_1, "Channel 3")
table = h5file.createTable(group, 'ch_4', li_measurement_1, "Channel 4")

group = h5file.createGroup("/", 'temperature', 'Temperature Data')
table = h5file.createTable(group, 'data', li_measurement_1, "All Data")

temperature = table.row()