import os
import scipy
import numpy as np
import pylab

#from MARfit_David import mar    # data fitting
from MAR_functions import *

# set the fit parameter
_gap = 1380                 # uV
_punkte = 800               # sample points to interpolate
_vmin = 0.05                # fitting min partial of gap
_vmax = 3.3                 # max voltage of gap
_iterations = 50000          # iterations for fit
_max_channels = 4           # starting value of channels
additional_info = True     # print additional information in plot
show_plots = False          # show plots after fit (else direct save)
reduced_y = True



color0 = "#C8E5EF"
color1 = "#A0D3E6"
color2 = "#59B6DC"
color3 = "#009AD1"



# load ivs
#iv_dir = r"c"
iv_path = r"C:\Users\David Weber\Desktop\iv_1410434984_5_-15.txt"



savename = os.path.split(iv_path)[1]
   
if True:
    u,i,params = load_iv_data(iv_path)
else:
    u,i,params = load_iv_data(iv_path,index_u=0,index_i=1,skip=0)
    params={"temp2": 99.9}

#if u[0] > u[-1]:
#    u,i = u[::-1],i[::-1]
    
i = i/104000.0
u_new = np.linspace(min(u),max(u),1000)
i_new = np.interp(u_new, u, i)

u,i = u_new,i_new
du,di,shift,x,y,anti_sym = find_iv_offset([u,i], verbal=True, show_plot=show_plots, plot_path=iv_path+"_offset.png")
u,i = u+du,i+di

    
import pylab
import brewer2mpl   # nice plots, has to be installed
from matplotlib.patches import Rectangle

pylab.close("all")

set2 = brewer2mpl.get_map('Paired', 'qualitative', 8).mpl_colors
extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)  #empty rectangle for legend


pylab.axes()
ax1 = pylab.gca()

i_factor = 1e9
u_factor = 1.0/(_gap*1e-6) # /_gap*1e3 for gap units


ax1.set_xlabel("eV/$\Delta$")
ax1.set_ylabel("I (nA)")
ax1.set_title("Tunnel Spectrum")
ax1.hold("False")
ax1.grid()

#G0 = scipy.constants.e**2/scipy.constants.h
from scipy.constants import h,e
G0 = e**2/h

if reduced_y:
    # plot only some points
    #x,y = thin_out(mar1, 40)
    #pl_data, = ax1.plot(x*u_factor, y/(G*G0*_gap*1e-6), marker="+", mew=1.3, ms=10, color=set2[4], linewidth=0,label="Experimental Data")
    # plot all points        
    pl_data, = ax1.plot(u*u_factor, i*i_factor, color = color3, linewidth=2)
    #ax1.hold("True")
    #pl_fit, = ax1.plot(fit[0]*u_factor, fit[1]/(G*G0*_gap*1e-6), color = set2[1], linewidth=2)
    
    ax1.set_xlim(xmin=-3, xmax=3)
    #ax1.set_ylim(ymin=0,ymax=10)
    #ax1.set_xticks([1,2,3,4])


    

pylab.savefig(iv_path+".png")
pylab.savefig(iv_path+".pdf")
pylab.savefig(iv_path+".svg")
if show_plots:    
    pylab.show()

