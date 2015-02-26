# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 21:02:03 2014

@author: David Weber
"""

#import tables
import numpy as np
import os
import time
import datetime
import pylab as pl
import scipy.constants as const

from functions_evaluate import *
import MAR_functions

    
r_0 = const.h/const.e**2/2.0
g_0 = 2.0*const.e**2/const.h
################################
##### START ####################
################################

db = 0


filename = r"141216_Pb266_Tc"

base_path = os.path.join("Z:\dweber\data_p5",filename)              # server
base_path = os.path.join("C:\data_p5",filename)                     # local
base_path = r"C:\Users\David Weber\Desktop\09\140911_Pb216_MAR01"   # custom
total_path = [os.path.join(base_path,'db_%i.h5'%(db))]
config_path = os.path.join(base_path,'config.txt')


pl.close("all")

skip_loading = False
if 'old_filename' in locals():
    if filename == old_filename:
        if last_loading_successfull:
            skip_loading = True

old_filename = filename
_time = time.time()

if skip_loading:
    print "Skipping Loading"
    last_loading_successfull = True
else:
    last_loading_successfull = False
    print "Loading %s"%total_path

if not last_loading_successfull:
    data_packages = []
    for file_total in total_path:
        data_packages.append(HDF_DATA(file_total))
    last_loading_successfull = True
    

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
    
    
##########################################################
### Taking apart all measurements from bunch of data #####
##########################################################

if split_up_ivs:
    # create dir and paths
    iv_dir = os.path.join(base_path,"ivs")
    trace_dir = os.path.join(base_path,"traces")
    bsweep_dir = os.path.join(base_path,"bsweep")
    ensure_dir(iv_dir+"\\")
    ensure_dir(trace_dir+"\\")
    ensure_dir(bsweep_dir+"\\")
    print "IV-DIR: %s"%(iv_dir)
    print "TRACE-DIR: %s"%(trace_dir)
    print "BSWEEP-DIR: %s"%(bsweep_dir)
    
    # todo
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
    for iv_times in ivs[:]:
        if not seperate_windows:
            ax_sub_a.cla()
            ax_didv.cla()
            ax_sub_b.cla()
            ax_sub_c.cla()
            ax_sub_d.cla()
            
        i_begin = find_min(data_packages[0].x_list, iv_times[0])
        i_end = find_min(data_packages[0].x_list, iv_times[1])

        ax_x_factor = 1e3
        ax_y_factor = 1e6
        slice_voltage = data_packages[0].voltage[i_begin:i_end]*ax_x_factor
        slice_current = data_packages[0].current[i_begin:i_end]*ax_y_factor
        
        fig = pl.figure(figsize=(21,12), dpi=72)
        fig.subplots_adjust(hspace = 0.3, wspace = 0.2)
        ax_sub_a = fig.add_subplot(2,2,1) # fig.gca()
        ax_didv = fig.add_subplot(2,2,2)
        ax_sub_b = ax_didv.twinx()
        ax_sub_c = fig.add_subplot(2,2,3)
        ax_sub_d = fig.add_subplot(2,2,4)
        
        ####################   A (I/V)   ####################
        from matplotlib.patches import Rectangle
        extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)  #empty rectangle for legend
        
        current_center_index = np.argmin(abs(slice_current))
        
        du,di,shift,corr_u,corr_i,anti_sym = MAR_functions.find_iv_offset([slice_voltage, slice_current], verbal=True)
        
        ax_sub_a.hold(True)
        if max(abs(slice_voltage)) > 10.0: # IETS
            ax_sub_a.plot(  slice_voltage, slice_current, 'r-', label="Raw")
            ax_sub_a.plot(  slice_voltage, slice_current, 'k-', label="Offset Corrected")
        else: # if MAR
            pl.hold(True)
            branch_a,    = ax_sub_a.plot(  flip_data_positive(slice_voltage[0:current_center_index]), flip_data_positive(slice_current[0:current_center_index]), 'r--')
            branch_b,    = ax_sub_a.plot(  flip_data_positive(slice_voltage[current_center_index:]), flip_data_positive(slice_current[current_center_index:]), 'g--')
            offset_corr, = ax_sub_a.plot(  corr_u, corr_i, 'k-')
            anti_sym,    = ax_sub_a.plot(  corr_u, anti_sym, 'b--')
            
            ax_sub_a.legend([branch_a,branch_b,offset_corr,anti_sym,extra,extra],["A","B","Offset Corrected","Anti Sym","dU %f mV"%(du), "dI %f $\mu$A"%(di)],loc=2)
        
        
        # save raw agilent data interpolated on agilent_voltage
        t_raw,v_raw = data_packages[0].v_raw   
        
        j_begin = find_min(t_raw, iv_times[0])
        j_end = find_min(t_raw, iv_times[1])
        
        t_raw,v_raw = t_raw[j_begin:j_end],v_raw[j_begin:j_end]
        drop, i_raw = data_packages[0].i_raw 
        i_raw = np.interp(t_raw, drop, i_raw)
        np.savetxt(os.path.join(iv_dir,str(int(iv_times[1]))+".txt"), np.array([v_raw,i_raw]).transpose(), "%10.10f", "\t")
        
        
        
        
        ####################   B   ####################
        ax_didv.plot(   slice_voltage, data_packages[0].di_dv[i_begin:i_end], 'k-', label="$dI/dV$")
        pl.hold(True)       
        ax_sub_b.plot( slice_voltage, data_packages[0].ch_0_r[i_begin:i_end]/max(data_packages[0].ch_0_r[i_begin:i_end]), 'g-', label="ch 0 r")
        ax_sub_b.plot( slice_voltage, data_packages[0].ch_1_r[i_begin:i_end]/max(data_packages[0].ch_1_r[i_begin:i_end]), 'r-', label="ch 1 r")
        ax_sub_b.plot( slice_voltage, data_packages[0].ch_3_r[i_begin:i_end]/max(data_packages[0].ch_3_r[i_begin:i_end]), 'y-', label="ch 3 r")
        ax_sub_b.plot( slice_voltage, data_packages[0].ch_4_r[i_begin:i_end]/max(data_packages[0].ch_4_r[i_begin:i_end]), 'b-', label="ch 4 r")
        
        ax_sub_b.legend()

        #ax_sub_b.plot( slice_voltage, d2i_dv2[i_begin:i_end]/di_dv[i_begin:i_end], 'b-')
        
        ax_sub_a.set_xlabel("Voltage (mV)")
        ax_sub_a.set_ylabel("Current (uA)")
        ax_sub_a.set_title("IV") 
        ax_sub_a.grid()
        
        ax_didv.set_xlabel("Voltage (mV)")
        ax_didv.set_ylabel("dI/dV ($G_0$)")
        ax_didv.set_title("LockIn")
        ax_didv.grid()
        
        ax_sub_b.set_ylabel("Raw Value (a.u.)")
        
        std = np.average(data_packages[0].ch_3_r[i_begin:i_end]/data_packages[0].di_dv[i_begin:i_end])
        #ax_sub_b.set_ylim([0,min(5*std,max(d2i_dv2[i_begin:i_end]/di_dv[i_begin:i_end]))])
        
        
        ####################   C   ####################
        diff_x = movingaverage(data_packages[0].voltage[i_begin:i_end]*ax_x_factor,25)
        diff_y = movingaverage(data_packages[0].di_dv[i_begin:i_end],5)
        d2idv2_num = np.diff(diff_x) / np.diff(diff_y)
        ax_sub_c.plot(data_packages[0].voltage[i_begin:i_end-1]*ax_x_factor, d2idv2_num, label="num. diff")
        ax_sub_c.grid()
        
        
        
        _xmin = min(data_packages[0].voltage[i_begin:i_end]*ax_x_factor)
        _xmax = max(data_packages[0].voltage[i_begin:i_end]*ax_x_factor)
        std = np.average(abs(d2idv2_num)*5)
        ax_sub_c.set_xlim([_xmin*0.9, _xmax*0.9])
        ax_sub_c.set_ylim([-std, +std])
        
        ax_sub_c.set_title("Lockin Second")
        ax_sub_c.set_xlabel("Voltage (mV)")
        ax_sub_c.set_ylabel("$d^2I/dV^2$ (a.u.)")
        
        
        ####################   D   ####################
        ax_sub_d.plot(slice_voltage,data_packages[0].ch_0_theta[i_begin:i_end], label="ch 0")
        ax_sub_d.plot(slice_voltage,data_packages[0].ch_1_theta[i_begin:i_end], label="ch 1")
        ax_sub_d.plot(slice_voltage,data_packages[0].ch_3_theta[i_begin:i_end], label="ch 3")
        ax_sub_d.plot(slice_voltage,data_packages[0].ch_4_theta[i_begin:i_end], label="ch 4")
        ax_sub_d.legend()
        
        ax_sub_d.set_title("Lockin Phase")
        ax_sub_d.set_xlabel("Voltage (mV)")
        ax_sub_d.set_ylabel("Phase ($^\circ$)")
        
        #pl.rcParams['legend.loc'] = 'best'
        
        capture_time = datetime.datetime.fromtimestamp(int(iv_times[1])).strftime('%d.%m.%Y %H:%M:%S')
        fig.text(0.0, 0.0, "Measured: %s"%(capture_time), fontdict=None)

        fig.savefig(os.path.join(iv_dir,str(int(iv_times[1]))+".png"))
        print "%i/%i %s"%(i,len(ivs),capture_time) 
        plt.draw()
        plt.pause(0.001)
        
        i += 1
    pl.close()
    
    i = 1
    for hist_times in histograms[1:2]:
        
        i_begin =   find_min(data_packages[0].x_list, hist_times[0])
        i_end =     find_min(data_packages[0].x_list, hist_times[1])

        fig = pl.figure(figsize=(12,12), dpi=72)
        fig.subplots_adjust(hspace = 0.35, wspace = 0.6)
        ax_cond = fig.add_subplot(1,1,1) 
        #fig.gca()
        #ax_didv = fig.add_subplot(2,1,2)
        #ax_sub_b = ax_didv.twinx()
        
        opening_data = []
        closing_data = []
        
        ##############################
        cond_lower_end = 1e-4
        cond_higher_end = 1e1
        ##############################
        #print len(data_packages[0].position[i_begin:i_end]), data_packages[0].position[i_begin], data_packages[0].position[i_end]
        if data_packages[0].cond[i_begin] > data_packages[0].cond[i_end]: 
            # opening curve
            opening_data.extend(data_packages[0].cond[i_begin:i_end])
            j = i_begin
            while j < i_end:
                if data_packages[0].cond[j] < cond_higher_end:
                    break
                j += 1
            k = j
            while k < i_end:
                if data_packages[0].cond[k] < cond_lower_end:
                    break
                k += 1
            ax_cond.plot(data_packages[0].position[i_begin:i_end]*(-1.0),data_packages[0].cond[i_begin:i_end], 'k-')
            ax_cond.set_title("Opening") 
        else:
            # closing curve
            opening_data.extend(data_packages[0].cond[i_begin:i_end])
            j = i_begin
            while j < i_end:
                if data_packages[0].cond[j] > cond_lower_end:
                    break
                j += 1
            k = j
            while k < i_end:
                if data_packages[0].cond[k] > cond_higher_end:
                    break
                k += 1
            ax_cond.plot(data_packages[0].position[i_begin:i_end],data_packages[0].cond[i_begin:i_end], 'k-')
            
            ax_cond.set_title("Closing") 

        #ax_didv.plot(position[i_begin:i_end],di_dv[i_begin:i_end], 'r-')
        #ax_sub_b.plot(voltage[i_begin:i_end],d2i_dv2[i_begin:i_end], 'b-')
        
        ax_cond.set_xlabel("Pos (Turns)")
        ax_cond.set_ylabel("S ($G_0$)")
        ax_cond.set_yscale("log")
        ax_cond.grid()
        
        fig.savefig(os.path.join(trace_dir,str(int(hist_times[1]))+".png"))
        pl.close()
        #trace_file = open(os.path.join(trace_dir,str(int(hist_times[1]))+".txt"),"w")
        #save_data(trace_file, [position[i_begin:i_end],cond[i_begin:i_end]])
        
        print "%i/%i %i"%(i,len(histograms),int(hist_times[1]))
        i += 1
    
    i = 1
    for circle_times in bcircle[0:]:
        
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
        

if False:
    ov_plot = pl.figure(figsize=(8,6),dpi=120)
    ov_hist = ov_plot.add_subplot(1,1,1)
    
    if True:   # log
        ov_hist.hist(1.0/data_packages[0].r_raw/g_0, log=False, bins=np.logspace(-4,3, 250))  
        ov_hist.set_xscale("log")
    else:
        ov_hist.hist(1.0/data_packages[0].r_raw/g_0, log=False, bins=np.linspace(0.0,15, 45))
        ov_hist.set_xscale("linear")
    ov_hist.set_xlabel("G (G/$G_0$)")
    ov_hist.set_ylabel("Counts")
    ov_hist.set_title("Histogram (%i open+close)"%(len(histograms)))
    ov_plot.savefig(os.path.join(base_path,"histogramm.png"))
    
    #import numpy as np
    #from scipy.optimize import curve_fit
    
    #def gauss(x, a, b, c):
    #    return a * np.exp(-b * x**2) + c
    """
    y = func(xdata, 2.5, 1.3, 0.5)
    ydata = y + 0.2 * np.random.normal(size=len(xdata))
    
    popt, pcov = curve_fit(func, xdata, ydata)"""

if False:
    plot_t = pl.figure()
    plot_t_1 = plot_t.add_subplot(2,1,1)
    plot_t_2 = plot_t.add_subplot(2,1,2)
    von = 0
    bis = -1
    plot_t_1.plot(data_packages[0].t_sample[von:bis], data_packages[0].cond[von:bis])
    plot_t_1.set_ylabel("G (G/$G_0$)")
    plot_t_1.set_xlabel("T (K)")
    plot_t_2.plot(data_packages[0].cond)

    plot_t_2.set_ylabel("G (G/$G_0$)")
    plot_t_2.set_xlabel("t (s)")
    #plot_t_1.set_ylim([0,2000])
    #plot_t_2.set_ylim([0,2000])
    plot_t.savefig(os.path.join(base_path,"temperature.png"))


    

