# -*- coding: utf-8 -*-
"""
Created on Sun May 18 21:05:38 2014

@author: David Weber
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
filename = r"140429_21-I-04_Histo_04"
server = True

femto_factor_u = 10.0
femto_factor_i = 10.0

max_cond = 0
max_res = 0

stepsize = 0.1  # seconds between samples



split_up_ivs = True
plot_overview = True
plot_ivs = False
hist=False

g0 = 2.0*e*e/h
if server:
    filename = os.path.join("Z:\dweber\data_p5",filename)
else:
    filename = os.path.join("D:\Desktop\data_p5",filename)



filename = r"Z:\\dweber\\data_p5\\140429_21-I-04_Histo_04\\traces\\"


def plot_2d_histogram(break_point=2.0):
    positions = []
    cond = []  
    
    files = os.listdir(filename)
    for f in files:
        if f[-4:] == ".txt":
            #print os.path.join(filename,f)
            trace_data = scipy.loadtxt(os.path.join(filename,f),unpack=True)
    
            p_temp = trace_data[0]
            c_temp = trace_data[1]
            
            if len(p_temp) < 20:
                continue

            index_point = -1
            if c_temp[0] > c_temp[-1]:
                for i in range(len(c_temp)):
                    if c_temp[i] > break_point:
                        index_point = i
            if c_temp[0] < c_temp[-1]:
                for i in range(len(c_temp)):
                    if c_temp[i] < break_point:
                        index_point = i
    
            if abs(c_temp[index_point]/break_point-1) > 0.1:
                continue
            
            print c_temp[index_point],p_temp[index_point]
            p_temp -= p_temp[index_point]
            
            positions.extend(p_temp)    
            cond.extend(c_temp)
    
    
    
    print len(positions),len(cond)
    
    xedges = np.arange(min(positions),0.2,0.01)
    yedges = np.arange(0,10,0.1)
    #print xedges,yedges
    H, xedges, yedges = np.histogram2d(positions, cond, bins=(xedges, yedges))
    #print H
    
    
    fig = pylab.figure(figsize=(16,8), dpi=144)
    ax = fig.gca()
    ax.set_title('2D')
    ax.grid()
    
    #X, Y = np.meshgrid(xedges, yedges)
    #ax.pcolormesh(X, Y, H)
    
    im = ax.imshow(H, interpolation='nearest', origin='low', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
    
    ax.set_aspect('auto') # equal
    ax.plot(positions,cond)
    #ax.set_ylim([0,10])
    pylab.show()


plot_2d_histogram()