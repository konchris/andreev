# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 10:28:28 2014

@author: David Weber
"""

import tables
import numpy as np
import os
import time
import datetime
import pylab as pl
import scipy.constants as const


def movingaverage(values, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(values, window, 'same')
    
def interpolate(x=[],data=[[],[]],scale_y=1.0):
    """interpolates using np.interp() with some extras"""
    xp = np.array(data[0])
    fp = np.array(data[1])/scale_y
    
    min_index = min(len(xp),len(fp))-1
    if len(xp) != len(fp):
        print "Interp: Indices dont match %i,%i"%(len(xp),len(fp))
    interp_array = np.interp(x,xp[0:min_index],fp[0:min_index])
    return interp_array

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)     

def find_min(L, value):
    iterations = 0
    maxindex = len(L) - 1
    if len(L) == 0 or L[0] >= value:
        return 0
    if L[-1] <= value:
        #log("Last value is larger than wanted value!")
        return maxindex

    index = 0
    while index <= maxindex:
        center = index + ((maxindex - index)/2)
        if L[center] <= value and L[center+1] > value:
            return center   
        elif L[center] > value:
            maxindex = center - 1
        else:
            index = center + 1
        iterations += 1
    return 0

g0 = const.elementary_charge**2*2.0/const.h
r0 = 1/g0


class HDF_DATA:
    """ Gives Access to a hdf5 data file"""
    
    def __init__(self, filename, rref=104000.0):
        """ Opens HDF5 file in andreev-format to import 
        and interpolate data lists. 
        
        filename:   absolute path to .db-file
        rref:       value of rref in ohms"""
        self.rref = rref
        
        _time = time.time()
            
        self.h5file = tables.openFile(filename, mode="r")
        tab_v = self.h5file.root.voltages.ch_0
        tab_i = self.h5file.root.voltages.ch_1
        tab_li_0 = self.h5file.root.lockin.ch_0
        tab_li_1 = self.h5file.root.lockin.ch_1
        tab_li_3 = self.h5file.root.lockin.ch_3
        tab_li_4 = self.h5file.root.lockin.ch_4
        tab_motor = self.h5file.root.motor.data
        tab_magnet_0 = self.h5file.root.magnet.ch_0
        tab_magnet_1 = self.h5file.root.magnet.ch_1
        tab_temperature = self.h5file.root.temperature.data
        
        ################################
        # AGILENTS #####################
        ################################
        
        _tab_v = tab_v[:]
        voltage_t,voltage_v = zip(*_tab_v)
        
        _tab_i = tab_i[:]
        current_t,current_v = zip(*_tab_i)
     
        self.v_raw = [voltage_t, voltage_v]
        self.i_raw = [current_t, current_v]
        print "Voltages after %is"%(time.time()-_time)
        _time = time.time()
        
        print "voltage:", len(voltage_t)
        print "current:", len(current_t)
        self.x_list = np.arange(self.v_raw[0][0],self.v_raw[0][-1],0.1)
        self.voltage = interpolate(self.x_list, self.v_raw)
        self.current = interpolate(self.x_list, self.i_raw, self.rref)
        self.r_raw = voltage_v/interpolate(voltage_t, [current_t, current_v], self.rref)
        
        
        ################################
        # LOCKIN #######################
        ################################
    
        raw_ch_0_t,raw_ch_0_x,raw_ch_0_y = zip(*tab_li_0[:])  
        raw_ch_1_t,raw_ch_1_x,raw_ch_1_y = zip(*tab_li_1[:])
        raw_ch_3_t,raw_ch_3_x,raw_ch_3_y = zip(*tab_li_3[:])
        raw_ch_4_t,raw_ch_4_x,raw_ch_4_y = zip(*tab_li_4[:])
        
        self.ch_0_x = interpolate(self.x_list, (raw_ch_0_t,raw_ch_0_x))
        self.ch_0_y = interpolate(self.x_list, (raw_ch_0_t,raw_ch_0_y))
        self.ch_1_x = interpolate(self.x_list, (raw_ch_1_t,raw_ch_1_x))
        self.ch_1_y = interpolate(self.x_list, (raw_ch_1_t,raw_ch_1_y))
        self.ch_3_x = interpolate(self.x_list, (raw_ch_3_t,raw_ch_3_x),rref)
        self.ch_3_y = interpolate(self.x_list, (raw_ch_3_t,raw_ch_3_y),rref)
        self.ch_4_x = interpolate(self.x_list, (raw_ch_4_t,raw_ch_4_x),rref)
        self.ch_4_y = interpolate(self.x_list, (raw_ch_4_t,raw_ch_4_y),rref)
        self.ch_0_r = np.sqrt(np.array(self.ch_0_x)**2 + np.array(self.ch_0_y)**2)
        self.ch_1_r = np.sqrt(np.array(self.ch_1_x)**2 + np.array(self.ch_1_y)**2)
        self.ch_3_r = np.sqrt(np.array(self.ch_3_x)**2 + np.array(self.ch_3_y)**2)
        self.ch_4_r = np.sqrt(np.array(self.ch_4_x)**2 + np.array(self.ch_4_y)**2)
        self.ch_0_theta = np.rad2deg(np.arctan(np.array(self.ch_0_x/self.ch_0_y)))
        self.ch_1_theta = np.rad2deg(np.arctan(np.array(self.ch_1_x/self.ch_1_y)))
        self.ch_3_theta = np.rad2deg(np.arctan(np.array(self.ch_3_x/self.ch_3_y)))
        self.ch_4_theta = np.rad2deg(np.arctan(np.array(self.ch_4_x/self.ch_4_y)))    
        
        print "Lockin after %is"%(time.time()-_time)
        _time = time.time()
        
        ################################
        # MOTOR ########################
        ################################
    
        raw_position,motor_t,raw_velocity = zip(*tab_motor[:])  
        self.position = interpolate(self.x_list, [motor_t, raw_position])   
        #print motor_t[0:100], raw_position[0:100], raw_velocity[0:100]
        self.velocity = interpolate(self.x_list, [motor_t, raw_velocity])   
        
        print "Motor after %is"%(time.time()-_time)
        _time = time.time()
        
        ################################
        # TEMPERATURE ###################
        ################################
    
        temperature_t,raw_pot,raw_sample = zip(*tab_temperature[:])  
        self.t_sample = interpolate(self.x_list, [temperature_t, raw_sample])
        self.t_pot = interpolate(self.x_list, [temperature_t, raw_pot])
        
        print "Temperature after %is"%(time.time()-_time)
        _time = time.time()
        
        ################################
        # MAGNET #######################
        ################################
    
        if len(tab_magnet_0) > 0:
            magnet_0_t,raw_field_0 = zip(*tab_magnet_0[:])
            self.field_0 = interpolate(self.x_list, [magnet_0_t, raw_field_0])
        else:
            self.field_0 =  np.array(self.x_list)*0
            
        if len(tab_magnet_1) > 0:
            magnet_1_t,raw_field_1 = zip(*tab_magnet_1[:])  
            self.field_1 = interpolate(self.x_list, [magnet_1_t, raw_field_1])
        else:
            self.field_1 =  np.array(self.x_list)*0
        print "Magnet after %is"%(time.time()-_time)
        _time = time.time()
        
        self.cond = abs(self.current/self.voltage*r0)
        self.di_dv = self.ch_3_r/self.ch_0_r*r0
        self.d2i_dv2 = self.ch_4_r/self.ch_1_r*r0
        
        print "Calc after %is"%(time.time()-_time)
        _time = time.time()
        
        """return {"x_list":self.x_list,                            # sampling
                "voltage":self.voltage, "current":self.current, "v_raw": self.v_raw, "i_raw":self.i_raw,      # 
                "position":self.position, "velocity":self.velocity, 
                "t_sample":self.t_sample, "t_pot":self.t_pot,
                "field_0": self.field_0, "field_1":self.field_1,
                "ch_0_x":self.ch_0_x, "ch_0_y":self.ch_0_y, "ch_0_r":self.ch_0_r, "ch_0_theta":self.ch_0_theta,
                "ch_1_x":self.ch_1_x, "ch_1_y":self.ch_1_y, "ch_1_r":self.ch_1_r, "ch_1_theta":self.ch_1_theta,
                "ch_3_x":self.ch_3_x, "ch_3_y":self.ch_3_y, "ch_3_r":self.ch_3_r, "ch_3_theta":self.ch_3_theta,
                "ch_4_x":self.ch_4_x, "ch_4_y":self.ch_4_y, "ch_4_r":self.ch_4_r, "ch_4_theta":self.ch_4_theta,
                "cond":self.cond, "di_dv":self.di_dv, "d2i_dv2":self.d2i_dv2}
                """