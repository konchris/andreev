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