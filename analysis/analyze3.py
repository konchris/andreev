# -*- coding: utf-8 -*-
"""
Spyder Editor

Analyze MAR
"""

import numpy as np
from matplotlib import pylab
import matplotlib as mpl
import os
import scipy
from scipy.constants import e,h
from functions import find_min, ensure_dir, save_data
import time

rref = 104000.0
filename = r"140514_21-I-04_Meas_didv_7"
filename = r"140516_21-I-04_BzSweep_08"
server = True


max_cond = 0
max_res = 0

stepsize = 0.1  # seconds between samples



split_up_ivs = False
plot_overview = True
plot_ivs = False
plot_hist=False

g0 = 2.0*e*e/h
if server:
    filename = os.path.join("Z:\dweber\data_p5",filename)
else:
    filename = os.path.join("D:\Desktop\data_p5",filename)
#filename = os.path.dirname(__file__) #<-- absolute dir the script is in
#filename = "C:\\Users\\David Weber\\Desktop\\testdatensatz"
if plot_overview:
    file_li_0 = os.path.join(filename,"li0.txt")
    file_li_1 = os.path.join(filename,"li1.txt")
    file_li_3 = os.path.join(filename,"li3.txt")
    file_li_4 = os.path.join(filename,"li4.txt")
    file_ips = os.path.join(filename,"ips.txt")
    file_ips_2 = os.path.join(filename,"ips_2.txt")
    file_motor = os.path.join(filename,"motor.txt")
    file_temp = os.path.join(filename,"temp.txt")
    file_femto = os.path.join(filename,"femto.txt")
    file_config = os.path.join(filename,"config.txt")
    file_agilent_old = os.path.join(filename,"agilent_old.txt")
    file_agilent_new = os.path.join(filename,"agilent_new.txt")
    
    pylab.clf()
    pylab.close('all')
    fig = pylab.figure(figsize=(16,8), dpi=72)
    fig.subplots_adjust(hspace = 0.3, wspace = 0.55)
    
    ax_v = fig.add_subplot(2,3,1)
    ax_i = ax_v.twinx()
    
    ax_motor = fig.add_subplot(2,3,2, sharex=ax_v)
    ax_ips = fig.add_subplot(2,3,3, sharex=ax_v)
    
    ax_temp = fig.add_subplot(2,3,4, sharex=ax_v)
    ax_temp_2 = ax_temp.twinx()
    
    ax_cond = fig.add_subplot(2,3,5, sharex=ax_v)
    ax_res = fig.add_subplot(2,3,6, sharex=ax_v)
    
    ax_didv = fig.add_subplot(2,3,4, sharex=ax_v)
    ax_d2idv2 = ax_didv.twinx()
    
    ax_hist = fig.add_subplot(2,3,6)
    
    """
    try:
        print "IPS"
        ips = scipy.loadtxt(file_ips,unpack=True)
        ips_t = ips[0]
        ips_b = ips[1]
    except Exception,e:
        ips_t = []
        ips_b = []
        print e
    """    

    
    """    
    try:
        print "Temperature"
        temp = scipy.loadtxt(file_temp,unpack=True)
        temp_t = temp[0]
        temp_a = temp[1]
        temp_b = temp[2]
    except Exception,e:
        temp_t = []
        temp_a = []
        temp_b = []
        print e
    """    
 
    
    try:
        print "Agilents"
        ag_old = scipy.loadtxt(file_agilent_old,unpack=True)
        ag_old_t = ag_old[0]
        ag_old_v = ag_old[1]
        
        ag_new = scipy.loadtxt(file_agilent_new,unpack=True)
        ag_new_t = ag_new[0]
        ag_new_v = ag_new[1]
        
        timestamp = np.arange(min(ag_new_t),max(ag_new_t),stepsize)
        voltage = np.interp(timestamp, ag_new_t, ag_new_v)
        current = np.interp(timestamp, ag_old_t, ag_old_v)
        cond = current/voltage/rref*12900
    
        ax_v.set_title("Voltage")
        ax_v.plot(timestamp-timestamp[0],voltage,'r-')
        ax_v.set_ylabel("Voltage / a.u.")
        ax_i.plot(timestamp-timestamp[0],current,'k-')
        ax_i.set_ylabel("Current / a.u.")
        ax_v.set_xlabel("Time / s")
        ax_v.grid()
        ax_i.grid()
    
        ax_cond.set_title("Conductance")
        #ax_res.set_title("Resistance")   
        ax_cond.plot(timestamp-timestamp[0],cond,'r-')
        ax_cond.set_yscale('log')
        ax_cond.set_ylabel("Conductance / G_0")
        ax_cond.grid()
        ax_cond.set_xlabel("Time / s")
        
        
        ax_hist.set_title("Histogram") 
        #ax_hist.hist(cond, bins=np.logspace(-4, 1, 100))
        #ax_hist.set_xscale("log")
        ax_hist.hist(cond, bins=np.linspace(0, 5, 100))
        ax_hist.grid()
        #if plot_hist:
        #    ax_hist.hist(cond, bins=100, log=False, range=(0,5)) #  range=(0,10)
        #np.histogram(cond, )
        ax_hist.set_ylabel("Counts")
        ax_hist.set_xlabel("Conductance ($G_0$)")
                
    except Exception,e:
        print "Fehla"
        print e
        
    
    try:
        print "Lockin"
        start = time.time()
        li_0 = scipy.loadtxt(file_li_0,unpack=True)
        li_0_t = li_0[0]
        li_0_u = li_0[1]
        li_0_i = li_0[2]
        li_0_x = li_0[3]
        li_0_y = li_0[4]
        print "Ch 0"
        li_1 = scipy.loadtxt(file_li_1,unpack=True)
        li_1_t = li_1[0]
        li_1_x = li_1[1]
        li_1_y = li_1[2]
        print "Ch 1"
        li_3 = scipy.loadtxt(file_li_3,unpack=True)
        li_3_t = li_3[0]
        li_3_x = li_3[1]
        li_3_y = li_3[2]
        print "Ch 3"
        li_4 = scipy.loadtxt(file_li_4,unpack=True)
        li_4_t = li_4[0]
        li_4_x = li_4[1]
        li_4_y = li_4[2]
        print "Ch 4"
        start2 = time.time()
        print "%f"%(start2-start)
        
        li_0_x = np.interp(timestamp, li_0_t, li_0_x)
        li_0_y = np.interp(timestamp, li_0_t, li_0_y)
        li_1_x = np.interp(timestamp, li_1_t, li_1_x)
        li_1_y = np.interp(timestamp, li_1_t, li_1_y)
        li_3_x = np.interp(timestamp, li_3_t, li_3_x)
        li_3_y = np.interp(timestamp, li_3_t, li_3_y)
        li_4_x = np.interp(timestamp, li_4_t, li_4_x)
        li_4_y = np.interp(timestamp, li_4_t, li_4_y)
        
        start3 = time.time()
        print "%f"%(start3-start2)
        
        li_0_r = np.sqrt(np.square(li_0_x)+np.square(li_0_y))
        li_3_r = np.sqrt(np.square(li_3_x)+np.square(li_3_y))
        li_1_r = np.sqrt(np.square(li_1_x)+np.square(li_1_y))
        li_4_r = np.sqrt(np.square(li_4_x)+np.square(li_4_y))
        di_dv = li_3_r/li_0_r/rref*12906.4
        d2i_dv2 = li_4_r/li_1_r/rref*12906.4
        
        start4 = time.time()
        print "%f"%(start4-start3)
        
        ax_didv.plot(timestamp-timestamp[0],di_dv,'k-')
        ax_d2idv2.plot(timestamp-timestamp[0],d2i_dv2,'r-')
        
    except Exception,e:
        print e
    
    
    
    try:
        print "Motor"
        #ax_motor.set_title("Motor")
        motor = scipy.loadtxt(file_motor,unpack=True)
        motor_t = motor[0]
        motor_pos = motor[1]
        motor_vel = motor[2]
        motor_cur = motor[3]

        position = np.interp(timestamp, motor_t, motor_pos)
        #ax_motor.plot(motor_t-motor_t[0],motor_pos,'r-')
        #ax_motor.set_ylabel("Position / a.u.")
        #ax_motor.grid()
        #ax_motor_2.plot(motor_t-motor_t[0],motor_vel,'k-')
        #ax_motor.set_xlabel("Time / s")
        #ax_motor_2.set_ylabel("Velocity / RPM")
    except Exception,e:
        print e
        
    
    try:
        print "IPS"
        ips = scipy.loadtxt(file_ips,unpack=True)
        ips_t = ips[0]
        ips_b = ips[1]
        ips_2 = scipy.loadtxt(file_ips_2,unpack=True)
        ips_2_t = ips_2[0]
        ips_2_b = ips_2[1]
        
        magnet_z = np.interp(timestamp, ips_t, ips_b)
        magnet_x = np.interp(timestamp, ips_2_t, ips_2_b)
               
    except Exception,e:
        print e
    
    """
        
    ax_temp.set_title("Temperature")
    try:
        ax_temp.plot(temp_t-temp_t[0],temp_a,'r-')
        ax_temp.set_ylabel("T 1K / K")
        ax_temp.grid()
        ax_temp_2.plot(temp_t-temp_t[0],temp_b,'k-')
        ax_temp_2.set_ylabel("T Sample / K")
        ax_temp.set_xlabel("Time / s")
    except Exception,e:
        print e
    """    
    pylab.show()
    pylab.savefig(os.path.join(filename,"overview.png"))

print "FINISHED OVERVIEW"


if split_up_ivs:
    try:  
        # splitting up the config file for sweeps, histograms, etc.
        print "Config"
        config = open(file_config)
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
        
        i_begin =   find_min(timestamp, iv_times[0])
        i_end =     find_min(timestamp, iv_times[1])

        fig = pylab.figure(figsize=(12,12), dpi=72)
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
        
        i_begin =   find_min(timestamp, hist_times[0])
        i_end =     find_min(timestamp, hist_times[1])

        fig = pylab.figure(figsize=(12,12), dpi=72)
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
        pylab.close()
        trace_file = open(os.path.join(trace_dir,str(int(hist_times[1]))+".txt"),"w")
        save_data(trace_file, [position[i_begin:i_end],cond[i_begin:i_end]])
        
        print "%i/%i %i"%(i,len(histograms),int(hist_times[1]))
        i += 1
    
    i = 1
    for circle_times in bcircle:#[0:20]:
        
        i_begin =   find_min(timestamp, circle_times[0])
        i_end =     find_min(timestamp, circle_times[1])

        fig = pylab.figure(figsize=(12,12), dpi=72)
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
    

if plot_ivs:
    directory = filename
    
    plots_path = os.path.join(directory,"plots")
    if not os.path.exists(plots_path):
        os.makedirs(plots_path)
    ivs = {}
    for iv_file in os.listdir(directory):
        try:
            if iv_file.endswith(".txt") and iv_file.startswith("iv_"):
                ivs[iv_file] = scipy.loadtxt(os.path.join(directory,iv_file), unpack=True, skiprows=2)
                
                # timestamp 0, voltage 1, current 2, li_0_x 3, li_0_y 4, li_1_x 5, li_1_y 6, li_3_x 7, li_3_y 8, li_4_x 9, li_4_y 10
                #print data
                
                fig = pylab.figure(figsize=(12,6), dpi=72)
                fig.subplots_adjust(hspace = 0.3, wspace = 0.55)
                
                ax_iv = fig.add_subplot(2,1,1)
                ax_iv.plot(ivs[iv_file][1],ivs[iv_file][2])
                ax_iv.set_title("IV of "+iv_file)
                ax_iv.grid()
                ax_didv = fig.add_subplot(2,1,2)
                didv = np.sqrt(np.square(ivs[iv_file][7]) + np.square(ivs[iv_file][8])) / np.sqrt(np.square(ivs[iv_file][3]) + np.square(ivs[iv_file][4]))
                ax_didv.plot(ivs[iv_file][1],didv)
                ax_didv.set_title("dI/dV of "+iv_file)
                ax_didv.grid()
                print os.path.join(plots_path,iv_file+".png")
                
                pylab.savefig(os.path.join(plots_path,iv_file+".png"))
                pylab.show()
                #break
        except Exception,e:
            print e
            
#from collections import OrderedDict
if plot_ivs:
    selected = [
    "iv_1396008955.txt",
    "iv_1396009292.txt",
    ]
    selected_labels = [
        "1.5 K",
        "5 K",
        ]
    ivs
    
    
    fig_t = pylab.figure(figsize=(12,6), dpi=72)
    fig_t.subplots_adjust(hspace = 0.3, wspace = 0.55)
    ax_iv = fig_t.add_subplot(2,1,1)
    ax_iv.hold(True)
    
    for caption in selected:
        for k,v in ivs.iteritems():
            if k == caption:
                ax_iv.plot(ivs[k][1]*1000,ivs[k][2]/rref,label=selected_labels[selected.index(k)])
    ax_iv.set_title("IV")
    ax_iv.legend()
    ax_iv.set_xlabel("V (mV)")
    ax_iv.set_ylabel("I (A)")
    ax_iv.grid()
    
    ax_didv = fig_t.add_subplot(2,1,2)
    
    ax_didv.hold(True)
    
    for caption in selected:
        for k,v in ivs.iteritems():
            if k == caption:
                didv = np.sqrt(np.square(ivs[k][7]) + np.square(ivs[k][8])) / np.sqrt(np.square(ivs[k][3]) + np.square(ivs[k][4]))
                ax_didv.plot(ivs[k][1]*1000,didv/rref, label=selected_labels[selected.index(k)])
    ax_didv.set_xlabel("V (mV)")
    ax_didv.set_ylabel("dI/dV (a.u.)")
    ax_didv.legend()
    ax_didv.set_title("dI/dV")
    ax_didv.grid()
    
    #pylab.show()
    pylab.savefig(filename+"dIdV_selected.png")
    pylab.show()






