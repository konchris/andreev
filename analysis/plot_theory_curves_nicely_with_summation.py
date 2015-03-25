# -*- coding: utf-8 -*-
"""
Created on Mon Oct 06 17:13:49 2014

@author: David
"""

import pylab as pl
from MAR_functions import *
import numpy as np

dataset="t_4k_0_25"
dataset2="t_0k"

pl.close("all")

normalize = True


#u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,(j+1)/10.0), index_u=0, index_i=1, skip=0)
#full_data=np.zeros((len(u),999),)
transmissions = np.arange(0.1,1.1,0.1)
colors = ["black", "grey", "blue", "cyan", "green", "magenta", "red", "purple"]

colors = ["#%s%s%s"%(hex((x*22)%256)[2:-1] , hex((80+x*8)%256)[2:-1] , hex((80+x*4)%256)[2:-1]) for x in np.arange(16)+2]

color_count = 11
colors = ["#%s%s%s"%(hex((x*(256/color_count))%256)[2:-1] , "00","00") for x in np.arange(color_count)+1]

pl.figure(figsize=(8,6),dpi=72)

pl.hold(True)
for j in range(len(transmissions)):
    if normalize:
        u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,transmissions[j]), index_u=0, index_i=1, skip=0)
        i = i/transmissions[j]
        pl.text(3.2, i[int(2.0/u[-1]*len(u))]-0.2-j*0.01, "%1.1f"%(transmissions[j]))
    else:
        u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,transmissions[j]), index_u=0, index_i=1, skip=0)
        pl.text(3.2, i[int(3.2/u[-1]*len(u))]-0.2-j*0.01, "%1.1f"%(transmissions[j]))
    pl.plot(u,i,color=colors[j%len(colors)], linewidth="3")    
    #pl.plot(u,i,label="%1.1f"%(transmissions[j]),color=colors[j%len(colors)], linewidth="2")    
    


#u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,0.2), index_u=0, index_i=1, skip=0)
#u2,i2,params = load_iv_data(r".\%s\%1.4f"%(dataset,0.3), index_u=0, index_i=1, skip=0)
#i = i+i2
#pl.plot(u,i,"b--",label="0.2+0.3", linewidth="4")

u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,0.4), index_u=0, index_i=1, skip=0)
u2,i2,params = load_iv_data(r".\%s\%1.4f"%(dataset,0.6), index_u=0, index_i=1, skip=0)
i = (i+i2)/1.0
pl.plot(u,i,"g--",label="0.4+0.6", linewidth="4")

pl.title("Theoretical I-V Curves MAR", fontsize=20)

if normalize:
    pl.xlim((0,3))
else:
    pl.xlim((0,3.5))
pl.xticks([2.0/x for x in [0.666,1,2,3,4,5,6,7,8]],["3","2","1",r"$\frac{2}{3}$",r"$\frac{2}{4}$",r"$\frac{2}{5}$"])
pl.xlabel("Voltage ($\Delta$/e)",fontsize=20)
pl.gcf().subplots_adjust(left=0.08, bottom=0.15, right=0.99, top=0.95)


if normalize:
    pl.ylabel("Current (2e$\Delta$/G$\hbar$)",fontsize=20)
    pl.ylim((0,6))
else:
    pl.ylim((0,6))
    pl.ylabel("Current (2e$\Delta$/$\hbar$)",fontsize=20)
legend = pl.legend(loc="best", title="Transmission", fontsize="16", ncol=1, shadow=True, )
pl.setp(legend.get_title(),fontsize='16')
pl.grid()
pl.gca().tick_params(axis='both', which='major', labelsize=20)
pl.show()

pl.savefig(r"plot_theory_curves_nicely_with_summation.pdf")
pl.savefig(r"plot_theory_curves_nicely_with_summation.png")
pl.savefig(r"plot_theory_curves_nicely_with_summation.svg")