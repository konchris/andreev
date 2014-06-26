# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 21:02:03 2014

@author: David Weber
"""

import tables
import numpy as np
import os

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
    
    
def interpolate(x=[],data=[[],[]],scale_y=1.0):
    """interpolates using np.interp() with some extras"""
    xp = np.array(data[0])
    fp = np.array(data[1])/scale_y
    
    min_index = min(len(xp),len(fp))-1
    
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
filename = r"140618_iets_mar_03_auto"
total_path = os.path.join("Z:\dweber\data_p5",filename,'db_%i.h5'%(db))
config_path = os.path.join("Z:\dweber\data_p5",filename,'config.txt')

print "Loading %s"%total_path

h5file = tables.openFile(total_path, mode = "r")
tab_v = h5file.root.voltages.ch_0
tab_i = h5file.root.voltages.ch_1
tab_li_0 = h5file.root.lockin.ch_0
tab_li_1 = h5file.root.lockin.ch_1
tab_li_3 = h5file.root.lockin.ch_3
tab_li_4 = h5file.root.lockin.ch_4

v_raw = [[x['timestamp'] for x in tab_v.iterrows()], [x['voltage'] for x in tab_v.iterrows()]]
i_raw = [[x['timestamp'] for x in tab_i.iterrows()], [x['voltage'] for x in tab_i.iterrows()]]

ch_0_t = []
ch_0_x = []
ch_0_y = []
for i in range(len(tab_li_0)):
    ch_0_t.append(tab_li_0[i]['timestamp'])
    ch_0_x.append(tab_li_0[i]['x'])
    ch_0_y.append(tab_li_0[i]['y'])
#ch_1_x = [[x['timestamp'] for x in tab_li_1.iterrows()], [x['x'] for x in tab_li_1.iterrows()]]
#ch_1_y = [[x['timestamp'] for x in tab_li_1.iterrows()], [x['y'] for x in tab_li_1.iterrows()]]
ch_3_t = []
ch_3_x = []
ch_3_y = []
for i in range(len(tab_li_3)):
    ch_3_t.append(tab_li_3[i]['timestamp'])
    ch_3_x.append(tab_li_3[i]['x'])
    ch_3_y.append(tab_li_3[i]['y'])
#ch_4_x = [[x['timestamp'] for x in tab_li_4.iterrows()], [x['x'] for x in tab_li_4.iterrows()]]
#ch_4_y = [[x['timestamp'] for x in tab_li_4.iterrows()], [x['y'] for x in tab_li_4.iterrows()]]

ch_0_r = np.sqrt(np.array(ch_0_x)**2 + np.array(ch_0_y)**2)
ch_3_r = np.sqrt(np.array(ch_3_x)**2 + np.array(ch_3_y)**2)

x_list = np.arange(v_raw[0][0],v_raw[0][-1],0.1)
voltage = interpolate(x_list, v_raw)
current = interpolate(x_list, i_raw, 104000.0)

cond = current/voltage*12900.0
di_dv = ch_3_r/ch_0_r
d2i_dv2 = di_dv


import pylab as pl
pl.hold(True)
pl_a = pl.subplot(2,2,1)
pl_a.plot(v_raw[0][:],v_raw[1][:],'r')
pl.plot(i_raw[0][:],i_raw[1][:],'k')

pl.subplot(2,2,2)
pl.plot(x_list,cond,'k')
pl.show()



###########################################################################
# SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP SPLIT UP #
###########################################################################
split_up_ivs = False
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
        
    print "Found %i IVs, %i Traces, %i Circles, %i BSweeps"%(len(ivs),len(histograms),len(bcircle),len(bsweep))
 
except Exception,e:
    print e   

if split_up_ivs:
    iv_dir = os.path.join(filename,"ivs")
    trace_dir = os.path.join(filename,"traces")
    
    ensure_dir(iv_dir+"\\")
    ensure_dir(trace_dir+"\\")
    print iv_dir
    print trace_dir
    
    i = 1
    for iv_times in ivs[0:5]:
        
        i_begin =   find_min(x_list, iv_times[0])
        i_end =     find_min(x_list, iv_times[1])

        fig = pl.figure(figsize=(12,12), dpi=72)
        fig.subplots_adjust(hspace = 0.35, wspace = 0.6)
        ax_i = fig.add_subplot(2,1,1) # fig.gca()
        ax_didv = fig.add_subplot(2,1,2)
        ax_d2idv2 = ax_didv.twinx()
        
        ax_i.plot(voltage[i_begin:i_end],current[i_begin:i_end], 'k-')
        ax_didv.plot(voltage[i_begin:i_end],di_dv[i_begin:i_end], 'r-')
        ax_d2idv2.plot(voltage[i_begin:i_end],d2i_dv2[i_begin:i_end], 'b-')
        
        ax_i.set_xlabel("Voltage (V)")
        ax_i.set_ylabel("Current (A)")
        ax_i.set_title("IV") 
        ax_i.grid()
        
        ax_didv.set_xlabel("Voltage (V)")
        ax_didv.set_ylabel("dI/dV (A/V)")
        ax_didv.set_title("LockIn") 
        ax_didv.grid()

        ax_d2idv2.set_ylabel("d2I/dV2 (A/V2)")

        fig.savefig(os.path.join(iv_dir,str(int(iv_times[1]))+".png"))
        pylab.close()
        
        print "%i/%i %i"%(i,len(ivs),int(iv_times[1]))
        i += 1
    
    i = 1
    for hist_times in histograms:#[0:20]:
        
        i_begin =   find_min(x_list, hist_times[0])
        i_end =     find_min(x_list, hist_times[1])

        fig = pl.figure(figsize=(12,12), dpi=72)
        fig.subplots_adjust(hspace = 0.35, wspace = 0.6)
        ax_cond = fig.add_subplot(1,1,1) # fig.gca()
        #ax_didv = fig.add_subplot(2,1,2)
        #ax_d2idv2 = ax_didv.twinx()
        
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
        #ax_d2idv2.plot(voltage[i_begin:i_end],d2i_dv2[i_begin:i_end], 'b-')
        
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
        #ax_d2idv2 = ax_didv.twinx()
        
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

        #ax_d2idv2.set_ylabel("d2I/dV2 (A/V2)")

        fig.savefig(os.path.join(magnet_dir,str(int(circle_times[1]))+"_circle.png"))
        pylab.close()
        
        print "%i/%i %i"%(i,len(bcircle),int(circle_times[1]))
        i += 1





