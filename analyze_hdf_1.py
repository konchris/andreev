# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 21:02:03 2014

@author: David Weber
"""

import tables
import numpy as np
import os
import time
import datetime
import pylab as pl
import scipy.constants as const

g0 = const.elementary_charge**2*2.0/const.h
r0 = 1/g0
"""
class li_measurement(tables.IsDescription):
    timestamp   =   tables.Float64Col()
    x           =   tables.Float32Col()
    y           =   tables.Float32Col()

class temperature(tables.IsDescription):
    timestamp   =   tables.Float64Col()
    pot         =   tables.Float32Col()
    sample      =   tables.Float32Col()

class magnet(tables.IsDescription):
    timestamp   =   tables.Float64Col()
    field       =   tables.Float32Col()

class motor(tables.IsDescription):
    timestamp   =   tables.Float64Col()
    position    =   tables.Float32Col()
    velocity    =   tables.Float32Col()

class voltage(tables.IsDescription):
    timestamp   =   tables.Float64Col()
    voltage     =   tables.Float32Col()

class parameter(tables.IsDescription):
    timestamp   =   tables.Float64Col()
    name        =   tables.StringCol(25)
    value       =   tables.Float64Col()
    """
    
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


db = 0

filename = r"140623_iets_mar_09_auto"
base_path = os.path.join("Z:\dweber\data_p5",filename)
total_path = os.path.join(base_path,'db_%i.h5'%(db))
config_path = os.path.join(base_path,'config.txt')

close("all")

skip_loading = False
if 'old_filename' in locals():
    if filename == old_filename:
        if last_loading_successfull:
            skip_loading = True

old_filename = filename
_time = time.time()

if skip_loading:
    last_loading_successfull = True
else:
    last_loading_successfull = False
    print "Loading %s"%total_path
    
    
    h5file = tables.openFile(total_path, mode = "r")
    tab_v = h5file.root.voltages.ch_0
    tab_i = h5file.root.voltages.ch_1
    tab_li_0 = h5file.root.lockin.ch_0
    tab_li_1 = h5file.root.lockin.ch_1
    tab_li_3 = h5file.root.lockin.ch_3
    tab_li_4 = h5file.root.lockin.ch_4
    tab_motor = h5file.root.motor.data
    tab_magnet_0 = h5file.root.magnet.ch_0
    tab_magnet_1 = h5file.root.magnet.ch_1
    tab_temperature = h5file.root.temperature.data
    
    ################################
    # AGILENT ######################
    ################################
    
    _tab_v = tab_v[:]
    voltage_t,voltage_v = zip(*_tab_v)
    
    _tab_i = tab_i[:]
    current_t,current_v = zip(*_tab_i)
 
    v_raw = [voltage_t, voltage_v]
    i_raw = [current_t, current_v]
    print "Voltages after %is"%(time.time()-_time)
    _time = time.time()
    
    
    ################################
    # LOCKIN #######################
    ################################

    raw_ch_0_t,raw_ch_0_x,raw_ch_0_y = zip(*tab_li_0[:])  
    raw_ch_1_t,raw_ch_1_x,raw_ch_1_y = zip(*tab_li_1[:])
    raw_ch_3_t,raw_ch_3_x,raw_ch_3_y = zip(*tab_li_3[:])
    raw_ch_4_t,raw_ch_4_x,raw_ch_4_y = zip(*tab_li_4[:])
    print "Lockin after %is"%(time.time()-_time)
    _time = time.time()
    
    ################################
    # MOTOR ########################
    ################################

    motor_t,raw_position,raw_velocity = zip(*tab_motor[:])  
    print "Motor after %is"%(time.time()-_time)
    _time = time.time()
    
    ################################
    # TEMPERATURE ###################
    ################################

    temperature_t,raw_pot,raw_sample = zip(*tab_temperature[:])  
    print "Temperature after %is"%(time.time()-_time)
    _time = time.time()
    
    ################################
    # MAGNET #######################
    ################################

    if len(tab_magnet_0) > 0:
        magnet_0_t,raw_field_0 = zip(*tab_magnet_0[:])
    #else:
    #    magnet_0_t,raw_field_0 = [[],[]]
    if len(tab_magnet_1) > 0:
        magnet_1_t,raw_field_1 = zip(*tab_magnet_1[:])  
    #else:
    #    magnet_1_t,raw_field_1 = [[],[]]
    print "Magnet after %is"%(time.time()-_time)
    _time = time.time()
    
    last_loading_successfull = True



rref = 104000.0



x_list = np.arange(v_raw[0][0],v_raw[0][-1],0.1)

ch_0_x = interpolate(x_list, (raw_ch_0_t,raw_ch_0_x))
ch_0_y = interpolate(x_list, (raw_ch_0_t,raw_ch_0_y))
ch_1_x = interpolate(x_list, (raw_ch_1_t,raw_ch_1_x))
ch_1_y = interpolate(x_list, (raw_ch_1_t,raw_ch_1_y))
ch_3_x = interpolate(x_list, (raw_ch_3_t,raw_ch_3_x),rref)
ch_3_y = interpolate(x_list, (raw_ch_3_t,raw_ch_3_y),rref)
ch_4_x = interpolate(x_list, (raw_ch_4_t,raw_ch_4_x),rref)
ch_4_y = interpolate(x_list, (raw_ch_4_t,raw_ch_4_y),rref)
ch_0_r = np.sqrt(np.array(ch_0_x)**2 + np.array(ch_0_y)**2)
ch_1_r = np.sqrt(np.array(ch_1_x)**2 + np.array(ch_1_y)**2)
ch_3_r = np.sqrt(np.array(ch_3_x)**2 + np.array(ch_3_y)**2)
ch_4_r = np.sqrt(np.array(ch_4_x)**2 + np.array(ch_4_y)**2)
ch_0_theta = np.rad2deg(np.arctan(np.array(ch_0_x/ch_0_y)))
ch_1_theta = np.rad2deg(np.arctan(np.array(ch_1_x/ch_1_y)))
ch_3_theta = np.rad2deg(np.arctan(np.array(ch_3_x/ch_3_y)))
ch_4_theta = np.rad2deg(np.arctan(np.array(ch_4_x/ch_4_y)))

voltage = interpolate(x_list, v_raw)
current = interpolate(x_list, i_raw, rref)

cond = abs(current/voltage*r0)
di_dv = ch_3_r/ch_0_r*r0
d2i_dv2 = ch_4_r/ch_1_r*r0

print "Calc after %is"%(time.time()-_time)
_time = time.time()

pl.hold(True)
fig_overview = pl.figure(figsize=(18,12), dpi=72)
#fig.subplots_adjust(hspace = 0.35, wspace = 0.6)
pl_a = fig_overview.add_subplot(2,2,1)
pl_b = fig_overview.add_subplot(2,2,2)
pl_c = fig_overview.add_subplot(2,2,3)
pl_d = fig_overview.add_subplot(2,2,4)
pl_a.plot(v_raw[0][:],v_raw[1][:],'r')
pl_a.plot(i_raw[0][:],i_raw[1][:],'k')
pl_b.plot(x_list,cond,'k')

#pl.show()



###########################################################################
# SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP #
###########################################################################
split_up_ivs = True
try:  
    # splitting up the config file for sweeps, histograms, etc.
    print "Loading %s"%config_path
    config = open(config_path)
    config_rows = config.readlines()
    
    histograms = []
    ivs = []
    bcircle = []
    bsweep = []
    
    last_iv_start = 0
    last_iv_end = 0
    last_hist_open = 0
    last_hist_close = 0
    last_circle_start = 0
    last_circle_stop = 0
    last_bsweep_start = 0
    last_bsweep_stop = 0
    for line in config_rows:
        commands = line.split()
        if commands[0] == "IV_START":
            last_iv_start = float(commands[1])
        if commands[0] == "IV_STOP":
            last_iv_end = float(commands[1])
            ivs.append([last_iv_start, last_iv_end]) 
        
        if commands[0] == "HISTOGRAM_OPEN":
            last_hist_open = float(commands[1])
            histograms.append([last_hist_close, last_hist_open])
        if commands[0] == "HISTOGRAM_CLOSE":
            last_hist_close = float(commands[1])
            histograms.append([last_hist_open, last_hist_close])
        
        if commands[0] == "BCIRCLE_START":
            last_circle_start = float(commands[1])
        if commands[0] == "BCIRCLE_STOP":
            last_circle_stop = float(commands[1])
            bcircle.append([last_circle_start, last_circle_stop])
        
        if commands[0] == "BSWEEP_START":
            last_bsweep_start = float(commands[1])
        if commands[0] == "BSWEEP_STOP":
            last_bsweep_stop = float(commands[1])
            bcircle.append([last_bsweep_start, last_bsweep_stop])
        
    print "Found %i IVs, %i Traces, %i Circles, %i BSweeps"%(len(ivs),len(histograms),len(bcircle),len(bsweep))
 
except Exception,e:
    print e   

if split_up_ivs:
    iv_dir = os.path.join(base_path,"ivs")
    trace_dir = os.path.join(base_path,"traces")
    
    ensure_dir(iv_dir+"\\")
    ensure_dir(trace_dir+"\\")
    print "IV-DIR: %s"%(iv_dir)
    print "TRACE-DIR: %s"%(trace_dir)
    
    
    seperate_windows = True
    if not seperate_windows:
        fig = pl.figure(figsize=(21,12), dpi=72)
        fig.subplots_adjust(hspace = 0.3, wspace = 0.2)
        ax_sub_a = fig.add_subplot(2,2,1) # fig.gca()
        ax_didv = fig.add_subplot(2,2,2)
        ax_sub_b = ax_didv.twinx()  
        ax_sub_c = fig.add_subplot(2,2,3)
        ax_sub_d = fig.add_subplot(2,2,4)
    
    
    i = 1
    for iv_times in ivs:#[0:10]:
        if not seperate_windows:
            ax_sub_a.cla()
            ax_didv.cla()
            ax_sub_b.cla()
            ax_sub_c.cla()
            ax_sub_d.cla()
        i_begin =   find_min(x_list, iv_times[0])
        i_end =     find_min(x_list, iv_times[1])

        ax_x_factor = 1e3
        ax_y_factor = 1e6
        x_voltage = voltage[i_begin:i_end]*ax_x_factor
        slice_current = current[i_begin:i_end]*ax_y_factor
        
        abs_current = abs(slice_current)
        current_center_index = np.argmin(abs_current)
        
        if max(abs(x_voltage)) < 10.0:
            i += 1
            continue
        else:
            if seperate_windows:
                fig = pl.figure(figsize=(21,12), dpi=72)
                fig.subplots_adjust(hspace = 0.3, wspace = 0.2)
                ax_sub_a = fig.add_subplot(2,2,1) # fig.gca()
                ax_didv = fig.add_subplot(2,2,2)
                ax_sub_b = ax_didv.twinx()
                ax_sub_c = fig.add_subplot(2,2,3)
                ax_sub_d = fig.add_subplot(2,2,4)

        if max(abs(x_voltage)) > 10.0:
            ax_sub_a.plot(  x_voltage, slice_current, 'k-')
        else:
            pl.hold(True)
            ax_sub_a.plot(  abs(x_voltage[0:current_center_index]), abs(slice_current[0:current_center_index]), 'k-')
            ax_sub_a.plot(  abs(x_voltage[current_center_index:]), abs(slice_current[current_center_index:]), 'g--')
        ax_didv.plot(   x_voltage, di_dv[i_begin:i_end], 'k-', label="$dI/dV$")
        
        #pl.hold(True)
        #ax_sub_b.plot( x_voltage, ch_0_r[i_begin:i_end]/max(ch_0_r[i_begin:i_end]), 'g-', label="ch 0 r")
        #ax_sub_b.plot( x_voltage, ch_1_r[i_begin:i_end]/max(ch_1_r[i_begin:i_end]), 'r-', label="ch 1 r")
        #ax_sub_b.plot( x_voltage, ch_3_r[i_begin:i_end]/max(ch_3_r[i_begin:i_end]), 'y-', label="ch 3 r")
        #ax_sub_b.plot( x_voltage, ch_4_r[i_begin:i_end]/max(ch_4_r[i_begin:i_end]), 'b-', label="ch 4 r")
        #ax_sub_b.legend()
        
        pl.hold(True)       
        ax_sub_b.plot( x_voltage, ch_0_x[i_begin:i_end]/max(ch_0_x[i_begin:i_end]), 'g-', label="ch 0 x")
        ax_sub_b.plot( x_voltage, ch_1_x[i_begin:i_end]/max(ch_1_x[i_begin:i_end]), 'r-', label="ch 1 x")
        ax_sub_b.plot( x_voltage, ch_3_x[i_begin:i_end]/max(ch_3_x[i_begin:i_end]), 'y-', label="ch 3 x")
        ax_sub_b.plot( x_voltage, ch_4_x[i_begin:i_end]/max(ch_4_x[i_begin:i_end]), 'b-', label="ch 4 x")
        ax_sub_b.legend()

        #ax_sub_b.plot( x_voltage, d2i_dv2[i_begin:i_end]/di_dv[i_begin:i_end], 'b-')
        
        ax_sub_a.set_xlabel("Voltage (mV)")
        ax_sub_a.set_ylabel("Current (uA)")
        ax_sub_a.set_title("IV") 
        ax_sub_a.grid()
        
        ax_didv.set_xlabel("Voltage (mV)")
        ax_didv.set_ylabel("dI/dV ($G_0$)")
        ax_didv.set_title("LockIn")
        ax_didv.grid()
        
        ax_sub_b.set_ylabel("$d^2I/dV^2$ (norm.)")
        std = np.average(d2i_dv2[i_begin:i_end]/di_dv[i_begin:i_end])
        #ax_sub_b.set_ylim([0,min(5*std,max(d2i_dv2[i_begin:i_end]/di_dv[i_begin:i_end]))])
        
        
        diff_x = movingaverage(voltage[i_begin:i_end]*ax_x_factor,25)
        diff_y = movingaverage(di_dv[i_begin:i_end],5)
        d2idv2_num = np.diff(diff_x) / np.diff(diff_y)
        ax_sub_c.plot(voltage[i_begin:i_end-1]*ax_x_factor, d2idv2_num)
        ax_sub_c.grid()
        
        _xmin = min(voltage[i_begin:i_end]*ax_x_factor)
        _xmax = max(voltage[i_begin:i_end]*ax_x_factor)
        std = np.average(abs(d2idv2_num)*5)
        ax_sub_c.set_xlim([_xmin*0.9, _xmax*0.9])
        ax_sub_c.set_ylim([-std, +std])
        
        ax_sub_d.plot(x_voltage,ch_0_theta[i_begin:i_end], label="ch 0")
        ax_sub_d.plot(x_voltage,ch_1_theta[i_begin:i_end], label="ch 1")
        ax_sub_d.plot(x_voltage,ch_3_theta[i_begin:i_end], label="ch 3")
        ax_sub_d.plot(x_voltage,ch_4_theta[i_begin:i_end], label="ch 4")
        ax_sub_d.legend()
        
        #pl.rcParams['legend.loc'] = 'best'
        
        capture_time = datetime.datetime.fromtimestamp(int(iv_times[1])).strftime('%d.%m.%Y %H:%M:%S')
        fig.text(0.0, 0.0, "Measured: %s"%(capture_time), fontdict=None)

        fig.savefig(os.path.join(iv_dir,str(int(iv_times[1]))+".png"))
        print "%i/%i %s"%(i,len(ivs),capture_time) 
        pl.show()
        
        i += 1
    pl.close()
    """
    i = 1
    for hist_times in histograms:#[0:20]:
        
        i_begin =   find_min(x_list, hist_times[0])
        i_end =     find_min(x_list, hist_times[1])

        fig = pl.figure(figsize=(12,12), dpi=72)
        fig.subplots_adjust(hspace = 0.35, wspace = 0.6)
        ax_cond = fig.add_subplot(1,1,1) # fig.gca()
        #ax_didv = fig.add_subplot(2,1,2)
        #ax_sub_b = ax_didv.twinx()
        
        ##############################
        cond_lower_end = 0.1
        cond_higher_end = 10.0
        ##############################
        if cond[i_begin] > cond[i_end]: 
            # opening curve
            j = i_begin
            while j < i_end:
                if cond[j] < cond_higher_end:
                    break
                j += 1
            k = j
            while k < i_end:
                if cond[k] < cond_lower_end:
                    break
                k += 1
            ax_cond.plot(position[j-5:k+5]*(-1.0),cond[j-5:k+5], 'k-')
            ax_cond.set_title("Opening") 
        else:
            # closing curve
            j = i_begin
            while j < i_end:
                if cond[j] > cond_lower_end:
                    break
                j += 1
            k = j
            while k < i_end:
                if cond[k] > cond_higher_end:
                    break
                k += 1
            ax_cond.plot(position[j-5:k+5],cond[j-5:k+5], 'k-')
            ax_cond.set_title("Closing") 

        #ax_didv.plot(position[i_begin:i_end],di_dv[i_begin:i_end], 'r-')
        #ax_sub_b.plot(voltage[i_begin:i_end],d2i_dv2[i_begin:i_end], 'b-')
        
        ax_cond.set_xlabel("Pos (Turns)")
        ax_cond.set_ylabel("S ($G_0$)")
        ax_cond.grid()

        ax_cond.set_ylim([0,10])
        
        fig.savefig(os.path.join(trace_dir,str(int(hist_times[1]))+".png"))
        pl.close()
        trace_file = open(os.path.join(trace_dir,str(int(hist_times[1]))+".txt"),"w")
        save_data(trace_file, [position[i_begin:i_end],cond[i_begin:i_end]])
        
        print "%i/%i %i"%(i,len(histograms),int(hist_times[1]))
        i += 1
    
    i = 1
    for circle_times in bcircle:#[0:20]:
        
        i_begin =   find_min(x_list, circle_times[0])
        i_end =     find_min(x_list, circle_times[1])

        fig = pl.figure(figsize=(12,12), dpi=72)
        fig.subplots_adjust(hspace = 0.35, wspace = 0.6)
        ax_angle = fig.add_subplot(2,1,1) # fig.gca()
        ax_angle_2 = fig.add_subplot(2,1,2)
        #ax_sub_b = ax_didv.twinx()
        
        np.seterr(divide="print")
        angles = np.rad2deg(np.arctan(magnet_z[i_begin:i_end]/magnet_x[i_begin:i_end]))
        
        window_size=50
        window = np.ones(int(window_size))/float(window_size)
        smooth = np.convolve(cond, window, 'same')

        ax_angle.plot(angles,cond[i_begin:i_end], 'k-')
        ax_angle_2.plot(angles,smooth[i_begin:i_end], 'k-')
        
        ax_angle.set_xlabel("Degree")
        ax_angle.set_ylabel("S (A/V)")
        ax_angle.set_title("Circle") 
        ax_angle.grid()
        ax_angle.set_ylim([2,2.25])
        
        ax_angle_2.set_xlabel("Degree")
        ax_angle_2.set_ylabel("S (A/V)")
        ax_angle_2.set_title("Circle") 
        ax_angle_2.grid()
        ax_angle_2.set_ylim([2,2.25])
        
        #ax_didv.set_xlabel("Time (s)")
        #ax_didv.set_ylabel("dI/dV (A/V)")
        #ax_didv.set_title("LockIn") 
        #ax_didv.grid()

        #ax_sub_b.set_ylabel("d2I/dV2 (A/V2)")

        fig.savefig(os.path.join(magnet_dir,str(int(circle_times[1]))+"_circle.png"))
        pylab.close()
        
        print "%i/%i %i"%(i,len(bcircle),int(circle_times[1]))
        i += 1
        """


""" old
#ch_1_t = []
    #ch_1_x = []
    #ch_1_y = []
    #for i in range(len(tab_li_1)):
    #    ch_1_t.append(tab_li_1[i]['timestamp'])
    #    ch_1_x.append(tab_li_1[i]['x'])
    #    ch_1_y.append(tab_li_1[i]['y'])
        #ch_3_t = []
    #ch_3_x = []
    #ch_3_y = []
    #for i in range(len(tab_li_3)):
    #    ch_3_t.append(tab_li_3[i]['timestamp'])
    #    ch_3_x.append(tab_li_3[i]['x'])
    #    ch_3_y.append(tab_li_3[i]['y'])

    #ch_0_t = []
    #ch_0_x = []
    #ch_0_y = []
    #for i in range(len(tab_li_0)):
    #    ch_0_t.append(tab_li_0[i]['timestamp'])
    #    ch_0_x.append(tab_li_0[i]['x'])
    #    ch_0_y.append(tab_li_0[i]['y'])    
    #ch_4_t = []
    #ch_4_x = []
    #ch_4_y = []
    #for i in range(len(tab_li_4)):
    #    ch_4_t.append(tab_li_4[i]['timestamp'])
    #    ch_4_x.append(tab_li_4[i]['x'])
    #    ch_4_y.append(tab_li_4[i]['y'])
    #voltage_t = []
    #voltage_v = []
    #for i in _tab_v:
    #    voltage_t.append(i["timestamp"])
    #    voltage_v.append(i['voltage'])
    #for i in range(len(tab_v)):
    #    voltage_t.append(tab_v[i]['timestamp'])
    #     voltage_v.append(tab_v[i]['voltage'])
    #current_t = []
    #current_v = []
       #for i in _tab_i:
    #    current_t.append(i["timestamp"])
    #    current_v.append(i['voltage'])
    #for i in range(len(tab_i)):
    #    current_t.append(tab_i[i]['timestamp'])
    #    current_v.append(tab_i[i]['voltage'])
"""
