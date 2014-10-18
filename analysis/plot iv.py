# -*- coding: utf-8 -*-
"""
Created on Mon Oct 06 17:13:49 2014

@author: David
"""

import pylab as pl
from MAR_functions import *
import numpy as np
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm

dataset="t_4k_0_25"
dataset2="t_0k"

pl.close("all")

u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,(0+1)/10.0), index_u=0, index_i=1, skip=0)
#full_data=np.zeros((len(u),999),)
full_data=[]
pl.hold(True)
transmissions = np.arange(0.002,1.0,0.002)
for j in range(len(transmissions)):
    u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,transmissions[j]), index_u=0, index_i=1, skip=0)
    print transmissions[j]
    full_data.extend(i)
    
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#full_data = [x for x in full_data]
full_data = np.array(full_data)
full_data = full_data.reshape((len(transmissions),-1))

#u,i,params = load_iv_data(r".\%s\0.9000"%(dataset), index_u=0, index_i=1, skip=0) 
#np.reshape()
#print full_data
X, Y = np.meshgrid(u, transmissions)
print len(X),len(Y),len(u),len(transmissions)
#cset = ax.contour(u,transmissions,full_data, cmap=cm.coolwarm) 
#pl.meshgrid(u,transmissions)
#surf = ax.plot_surface(full_data)
print len(full_data)
#full_data = X**2+Y**2
#surf = ax.plot_surface(X,Y, full_data, rstride=1, cstride=1, cmap=cm.coolwarm,
#        linewidth=0, antialiased=False)
pl.imshow(full_data)
#pl.contour(X,Y,full_data)


#u,i,params = load_iv_data(r".\%s\1.000"%(dataset), index_u=0, index_i=1)
#pl.plot(u,i,label="1.0")
#pl.legend()
#pl.grid()
#pl.colormaps()


#cset = ax.contour(X, Y, Z, cmap=cm.coolwarm)
#ax.clabel(cset, fontsize=9, inline=1)