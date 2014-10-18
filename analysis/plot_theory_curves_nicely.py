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


#u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,(j+1)/10.0), index_u=0, index_i=1, skip=0)
#full_data=np.zeros((len(u),999),)
transmissions = np.arange(0.1,1.1,0.1)
colors = ["black", "grey", "blue", "cyan", "green", "magenta", "red", "purple"]

colors = ["#%s%s%s"%(hex((x*22)%256)[2:-1] , hex((80+x*8)%256)[2:-1] , hex((80+x*4)%256)[2:-1]) for x in arange(16)+2]

color_count = 11
colors = ["#%s%s%s"%(hex((x*(256/color_count))%256)[2:-1] , "00","00") for x in arange(color_count)+1]


pl.hold(True)
for j in range(len(transmissions)):
    u,i,params = load_iv_data(r".\%s\%1.4f"%(dataset,transmissions[j]), index_u=0, index_i=1, skip=0)
    pl.plot(u,i,label="%1.1f"%(transmissions[j]),color=colors[j%len(colors)], linewidth="2")


pl.title("Theoretical I-V Curves MAR")

pl.xlim((0,3.5))
pl.xticks([2.0/x for x in [1,2,3,4,5,6,7,8]],["2","1",r"$\frac{2}{3}$",r"$\frac{1}{2}$",r"$\frac{2}{5}$"])
pl.xlabel("Voltage ($\Delta$)")

pl.ylim((0,6))
pl.ylabel("Current (I$\Delta$/2e)")
pl.legend(loc="best", title="Transmission", fontsize="12", ncol=2, shadow=True)
pl.grid()
pl.show()

pl.savefig(r"plot_theory_curves_nicely.pdf")
pl.savefig(r"plot_theory_curves_nicely.png")
pl.savefig(r"plot_theory_curves_nicely.svg")