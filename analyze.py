# -*- coding: utf-8 -*-
"""
Spyder Editor
All rights reserved by David Weber
Analyze MAR
"""

import numpy as np
from matplotlib import pylab
import matplotlib as mpl
import os
import scipy
from scipy.constants import *

# 
rref = 100000.0
filename = r"140326_hist_4"
server = True

femto_factor_u = 10.0
femto_factor_i = 10.0

max_cond = 0
max_res = 0

stepsize = 0.1


hist=True




g0 = 2.0*e*e/h
if server:
    filename = "Z:\dweber\data_p5\\" + filename + "\\"
else:
    filename = "D:\Desktop\data_p5\\" + filename + "\\"
print filename
file_li_0 = filename+"li0.txt"
file_li_1 = filename+"li1.txt"
file_li_3 = filename+"li3.txt"
file_li_4 = filename+"li4.txt"
file_ips = filename+"ips.txt"
file_motor = filename+"motor.txt"
file_temp = filename+"temp.txt"
file_femto = filename+"femto.txt"
file_config = filename+"config.txt"
file_agilent_old = filename+"agilent_old.txt"
file_agilent_new = filename+"agilent_new.txt"


pylab.clf()

pylab.close('all')
fig = pylab.figure(figsize=(16,8), dpi=72)
fig.subplots_adjust(hspace = 0.3, wspace = 0.55)

ax_v = fig.add_subplot(2,3,1)
ax_i = ax_v.twinx()

#ax_motor = fig.add_subplot(2,3,2, sharex=ax_v)
#ax_ips = fig.add_subplot(2,3,3, sharex=ax_v)

#ax_temp = fig.add_subplot(2,3,4, sharex=ax_v)
#ax_temp_2 = ax_temp.twinx()

ax_cond = fig.add_subplot(2,3,5, sharex=ax_v)
#ax_res = fig.add_subplot(2,3,6, sharex=ax_v)

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
    
try:
    print "Motor"
    motor = scipy.loadtxt(file_motor,unpack=True)
    motor_t = motor[0]
    motor_pos = motor[1]
    motor_vel = motor[2]
    motor_cur = motor[3]
except Exception,e:
    print e
    
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
    voltage = np.interp(timestamp,ag_new_t,ag_new_v)
    current = np.interp(timestamp,ag_old_t,ag_old_v)
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
    ax_cond.set_ylabel("Conductance / S")
    ax_cond.grid()
    ax_cond.set_xlabel("Time / s")
    
    ax_hist.hist(cond, bins=np.logspace(-4, 1, 50))
    ax_hist.set_xscale("log")
    ax_hist.grid()
    #ax_hist.hist(cond, bins=100, log=False, range=(0,5)) #  range=(0,10)
    #np.histogram(cond, )
    
except Exception,e:
    print e

print "yiffy"
try:
    print "Lockin"
    li_0 = scipy.loadtxt(file_li_0,unpack=True)
    li_0_t = li_0[0]
    li_0_u = li_0[1]
    li_0_i = li_0[2]
    li_0_x = li_0[3]
    li_0_y = li_0[4]
    li_1 = scipy.loadtxt(file_li_1,unpack=True)
    li_1_t = li_1[0]
    li_1_x = li_1[1]
    li_1_y = li_1[2]
    li_3 = scipy.loadtxt(file_li_3,unpack=True)
    li_3_t = li_3[0]
    li_3_x = li_3[1]
    li_3_y = li_3[2]
    li_4 = scipy.loadtxt(file_li_4,unpack=True)
    li_4_t = li_4[0]
    li_4_x = li_4[1]
    li_4_y = li_4[2]
    
    li_0_x = np.interp(timestamp, li_0_t, li_0_x)
    li_0_y = np.interp(timestamp, li_0_t, li_0_y)
    li_1_x = np.interp(timestamp, li_1_t, li_1_x)
    li_1_y = np.interp(timestamp, li_1_t, li_1_y)
    li_3_x = np.interp(timestamp, li_3_t, li_3_x)
    li_3_y = np.interp(timestamp, li_3_t, li_3_y)
    li_4_x = np.interp(timestamp, li_4_t, li_4_x)
    li_4_y = np.interp(timestamp, li_4_t, li_4_y)
    
    li_0_r = np.sqrt(np.square(li_0_x)+np.square(li_0_y))
    li_3_r = np.sqrt(np.square(li_3_x)+np.square(li_3_y))
    li_1_r = np.sqrt(np.square(li_1_x)+np.square(li_1_y))
    li_4_r = np.sqrt(np.square(li_4_x)+np.square(li_4_y))
    di_dv = li_3_r/li_0_r/rref
    d2i_dv2 = li_4_r/li_1_r/rref
    
    ax_didv.plot(timestamp-timestamp[0],di_dv,'k-')
    ax_d2idv2.plot(timestamp-timestamp[0],d2i_dv2,'r-')
    
except Exception,e:
    print e

"""
ax_cond.set_title("Conductance")
ax_res.set_title("Resistance")
try:    
    ax_cond.plot(li_t-li_t[0],1/li_res*12900.0,'r-')
    ax_cond.set_yscale('log')
    ax_cond.set_ylabel("Conductance / S")
    ax_cond.grid()
    ax_cond.set_xlabel("Time / s")
    
    ax_res.plot(li_t-li_t[0],li_res,'r-')
    ax_res.set_yscale('log')
    ax_res.set_ylabel("Resistance / Ohm")
    ax_res.grid()
    ax_res.set_xlabel("Time / s")
    if max_cond:
        ax_cond.set_ylim([0,max_cond])
    if max_res:
        ax_res.set_ylim([0,max_cond])

    #if (hist):
    #    ax_res.hist(li_res, bins=100, log=False, range=(0,5)) #  range=(0,10),
except Exception,e:
    print e

ax_motor.set_title("Motor")
try:
    ax_motor.plot(motor_t-motor_t[0],motor_pos,'r-')
    ax_motor.set_ylabel("Position / a.u.")
    ax_motor.grid()
    ax_motor_2.plot(motor_t-motor_t[0],motor_vel,'k-')
    ax_motor.set_xlabel("Time / s")
    ax_motor_2.set_ylabel("Velocity / RPM")
except Exception,e:
    print e

ax_ips.set_title("IPS")
try:    
    ax_ips.plot(ips_t-ips_t[0],ips_b*1000.0,'r-')
    ax_ips.set_ylabel("Field / mT")
    ax_ips.set_xlabel("Time / s")
except Exception,e:
    print e
    
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
pylab.savefig(filename+"overview.png")