# -*- coding: utf-8 -*-
"""
Created on Sun Feb 02 14:09:19 2014
All rights reserved by David Weber
@author: David Weber
"""

from tables import *
import numpy
import os

class li_measurement(IsDescription):
    timestamp   =   Float64Col()
    x           =   Float32Col()
    y           =   Float32Col()

class temperature(IsDescription):
    timestamp   =   Float64Col()
    pot         =   Float32Col()
    sample      =   Float32Col()

class magnet(IsDescription):
    timestamp   =   Float64Col()
    field       =   Float32Col()

class motor(IsDescription):
    timestamp   =   Float64Col()
    position    =   Float32Col()
    velocity    =   Float32Col()

class voltage(IsDescription):
    timestamp   =   Float64Col()
    voltage     =   Float32Col()

class parameter(IsDescription):
    timestamp   =   Float64Col()
    name        =   StringCol(25)
    value       =   Float64Col()
    
class hdf5_saving:
    def __init__(self, filename=None):
        """Initialises new File with HDF5
        Filename: Absolute Path to File"""
        
        self.create_db(filename)
               
        
    def create_db(self, filename=None):
        """Filename: Absolute Path to File"""
        #d = str(_self.ui.editSetupDir.text())+str(_self.ui.editHeader.text())+"\\"    
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        # search a free filename
        i = 0
        while True:
            subname = "db_%i.h5"%(i)
            db_name = os.path.join(filename,subname)
            if not os.path.isfile(db_name):
                print "%s - Filename OK"%db_name
                break
            else:
                print "%s - File exists"%db_name
            i += 1
            
        self.h5file = openFile(db_name, mode = "w", title = "Measurement Data")

        group = self.h5file.createGroup("/", 'lockin', 'Zurich LockIn Data')
        
        table = self.h5file.createTable(group, 'ch_0', li_measurement, "Channel 0")
        table = self.h5file.createTable(group, 'ch_1', li_measurement, "Channel 1")
        table = self.h5file.createTable(group, 'ch_3', li_measurement, "Channel 3")
        table = self.h5file.createTable(group, 'ch_4', li_measurement, "Channel 4")
        
        group = self.h5file.createGroup("/", 'temperature', 'Temperature Data')
        table = self.h5file.createTable(group, 'data', temperature, "All Data")
        
        group = self.h5file.createGroup("/", 'magnet', 'Magnet Data')
        table = self.h5file.createTable(group, 'ch_0', magnet, "IPS Z")
        table = self.h5file.createTable(group, 'ch_1', magnet, "IPS X")
        
        group = self.h5file.createGroup("/", 'motor', 'Motor Data')
        table = self.h5file.createTable(group, 'data', motor, "All Data")
        
        group = self.h5file.createGroup("/", 'voltages', 'Voltage Data')
        table = self.h5file.createTable(group, 'ch_0', voltage, "Voltage")
        table = self.h5file.createTable(group, 'ch_1', voltage, "Current")
        
        group = self.h5file.createGroup("/", 'info', 'Add. Information')
        table = self.h5file.createTable(group, 'parameters', parameter, "Measurement Parameters")
        
        self.h5file.flush()
    
    def close(self):
        """Closes the File"""
        self.h5file.close()
    
    def save_temperature(self, timestamp=[], temp_pot=[], temp_sample=[]):
        table = self.h5file.root.temperature.data
        t_row = table.row
        for i in range(len(timestamp)):
            t_row["timestamp"] = timestamp[i]
            t_row["pot"] = temp_pot[i]
            t_row["sample"] = temp_sample[i]
            t_row.append()
        self.h5file.flush()
    
    def save_lockin(self, channel=0, timestamp=[], x=[], y=[]):
        """Takes a list of data for LockIn Channel.
        Channel: 0-5
        timestamp,x,y: List of Float"""
        
        # Find the right channel
        for table in self.h5file.walkNodes("/lockin/", "Table"):
            if table.name == "ch_%i"%(channel):
                break
            
        t_row = table.row
        for i in range(len(timestamp)):
            t_row["timestamp"] = timestamp[i]
            t_row["x"] = x[i]
            t_row["y"] = y[i]
            t_row.append()
        self.h5file.flush()
    
    def save_magnet(self, channel=0, timestamp=[], field=[]):
        """Takes a list of data for Magnet Fields.
        Channel: 0-1
        timestamp,field: List of Float"""
        
        # Find the right channel
        for table in self.h5file.walkNodes("/magnet/", "Table"):
            if table.name == "ch_%i"%(channel):
                break
            
        t_row = table.row
        for i in range(len(timestamp)):
            t_row["timestamp"] = timestamp[i]
            t_row["field"] = field[i]
            t_row.append()
        self.h5file.flush()
    
    def save_motor(self, timestamp=[], position=[], velocity=[]):
        table = self.h5file.root.motor.data            
        
        t_row = table.row
        for i in range(len(timestamp)):
            t_row["timestamp"] = timestamp[i]
            t_row["position"] = position[i]
            t_row["velocity"] = velocity[i]
            t_row.append()
        self.h5file.flush()
    
    def save_voltage(self, channel=0, timestamp=[], voltage=[]):
        """Takes a list of data for Magnet Fields.
        Channel: 0-1
        timestamp,voltage: List of Float"""
        
        # Find the right channel
        for table in self.h5file.walkNodes("/voltages/", "Table"):
            if table.name == "ch_%i"%(channel):
                break        
        
        t_row = table.row
        for i in range(len(timestamp)):
            t_row["timestamp"] = timestamp[i]
            t_row["voltage"] = voltage[i]
            t_row.append()
        self.h5file.flush()
    
    def save_parameter(self, timestamp=[], position=[], velocity=[]):
        table = self.h5file.root.motor.data            
        
        t_row = table.row
        for i in range(len(timestamp)):
            t_row["timestamp"] = timestamp[i]
            t_row["position"] = position[i]
            t_row["velocity"] = velocity[i]
            t_row.append()
        self.h5file.flush()

            
if __name__ == "__main__":        
    test = "C:\\Users\\David Weber\\Desktop\\andreev\\testhdf5\\"
    db = hdf5_saving(test)
    
    """table = h5file.root.temperature.data
    t_row = table.row
    t_row["timestamp"] = 1234.2
    t_row["pot"] = 32.2
    t_row["sample"] = 12.2
    t_row.append()"""
    
    db.save_lockin(1,[1,2,3],[0,4,3],[2,1,3])
    db.save_magnet(0,[1,2,3],[3,3.2,3.1])
    db.save_magnet(1,[1,2,3],[3,3.2,3.1])
    db.save_voltage(0,[10,2,03],[3,3.02,3.1])
    db.save_voltage(1,[1,20,3],[30,30.2,3.1])
    db.save_motor([1,2,3],[3,3.2,3.1],[4,5,6])
    
    db.close()



