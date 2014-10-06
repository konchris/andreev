import os
import scipy
import numpy as np
import pylab

from MARfit_David import mar    # data fitting
from MAR_functions import *

# set the fit parameter
_gap = 1370                 # uV
_punkte = 800               # sample points to interpolate
_vmin = 0.05                # fitting min partial of gap
_vmax = 3.3                 # max voltage of gap
_iterations = 5000          # iterations for fit
_max_channels = 4           # starting value of channels
additional_info = True     # print additional information in plot
show_plots = True          # show plots after fit (else direct save)



# load ivs
iv_dir = r"C:\Users\David Weber\Desktop\Pb216\\"
iv_files = load_iv_files(iv_dir)


for iv_file in iv_files[:]:
   
    u,i,params = load_iv_data(os.path.join(iv_dir,iv_file))  
    if u[0] > u[-1]:
        u,i = u[::-1],i[::-1]
        
    u_new = np.linspace(min(u),max(u),1000)
    i_new = np.interp(u_new, u, i)
    
    u,i = u_new,i_new
    du,di,shift,u,i = find_iv_offset_2([u,i], verbal=True)
    #u,i = u-du,i-di
    
    #u_min = np.argmin(abs(u))
    #u,i = u[u_min:],i[u_min:]
    
    #break
    
    if additional_info:    # DEBUG
        pylab.close("all")
        pylab.plot(u,i,"+")
        ax = pylab.gca()
        ax.set_xlim([-0.01,0.01])
        ax.grid()
        if show_plots:
            pylab.show()
    
    print "Max: %5.2f Delta" %(u[-1]/_gap*1e6)
    if u[-1]/_gap*1e6 < _vmax:
        print "Voltage Span is not large enough %f < %f"%(u[-1]/_gap*1e6,_vmax)

    
    # create linear fit for outside the gap
    outer_gap_index = next(x[0] for x in enumerate(u) if x[1] > 3*_gap/1e6)
    p = np.polyfit(u[outer_gap_index:], i[outer_gap_index:], 1)
    # create dataline with this linear fit
    i_linear = np.polyval(p,u[:])
    
    # cluster data
    mar1 = np.array([u,i])
    
    # do the actual fit
    c = mar.fit(messung=mar1, iter=_iterations, channels=_max_channels, gap=_gap, punkte=_punkte, Vmin=_vmin, Vmax=_vmax, ErrRef=1E-10, KickOff=0.002, Strength=0.2); c #was gap=180 # kickoff 2e-4 # strength=0.1
    # gather a curve with the results of the fit (displaying only)
    fit = mar.kanalf(c, _gap, _punkte, 0, _vmax)
    
    
    import pylab
    import brewer2mpl   # nice plots, has to be installed
    from matplotlib.patches import Rectangle
    
    pylab.close("all")
    
    set2 = brewer2mpl.get_map('Paired', 'qualitative', 8).mpl_colors
    extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)  #empty rectangle for legend
    i_factor = 1e6
    u_factor = 1e3/_gap*1e3 # /_gap*1e3 for gap units
    no_channel = 5e-2       # transmission indicating no real channel anymore
    pos_x,pos_y = 0.5,1.0
    
    
    pylab.axes()
    ax1 = pylab.gca()
    
    #ax3 = ax1.twiny()
    #ax3.set_xlabel("U ($\Delta$)")
    
    ax1.set_xlabel("U ($\Delta$)")
    ax1.set_ylabel("I ($\mu$A)")
    ax1.set_title("MAR")
    ax1.hold("False")
    pl_fit = ax1.plot(fit[0]*u_factor, fit[1]*i_factor, color = set2[1], linewidth=2,label="Fit %2.2f $G_0$"%(np.sum(c)))
    ax1.hold("True")
    pl_data = ax1.plot(mar1[0]*u_factor, mar1[1]*i_factor, color = set2[4], linewidth=2,label="Experimental Data")
    
    if additional_info:
        pl_data = ax1.plot(u*u_factor, i_linear*i_factor, color = set2[2], linewidth=1,label="Excess Current %2.2f $G_0$"%(p[0]*12906))
    
    ax1.set_xlim(xmin=0)
    ax1.set_ylim(ymin=0)
    ax1.set_xticks([1,2,3,4])
    #pylab.legend([pl_fit,pl_data,extra],("Fit","Data","Gap: %2.3fmeV"%(_gap/1000.0)),loc=2)
    ax1.legend(loc=2)    
    ax1.grid()
    if additional_info:
        ax1.text(max(u*u_factor)*0.1,max(i*i_factor)*0.8, "Gap: %2.3fmeV"%(_gap/1000.0),ha="left")
        ax1.text(max(u*u_factor)*0.1,max(i*i_factor)*0.75, "T: %2.1fK"%(float(params["temp2"])),ha="left")
    
    """for i in range(len(c)):
        if c[i] < no_channel:
            rest = np.sum(c[i:])
            pylab.text(pos_x,pos_y-i*0.05,"Dropped:\t%f $G_0$"%(rest))
            break
        pylab.text(pos_x,pos_y-i*0.05,"Channel %i:\t%f $G_0$"%(i+1,c[i]))"""
    
    ch = [x for x in c if x > no_channel]
    ch_rest = [x for x in c if x < no_channel]
    rest = np.sum(ch_rest)
    
    
    # PLOTTING THE CHANNELS
    pylab.axes([0.55, 0.15, 0.3, 0.3])
    ax2 = pylab.gca()
    pylab.bar(np.array(range(len(ch)))+1-0.4,ch, facecolor=set2[1], width=0.8)
    
    # CHANNEL TRANSMISSIONS
    ch_height_par = 3
    for j in range(len(ch)):
        pylab.text(j+1, ch[j]+ch[0]/ch_height_par, "%0.2f"%(ch[j]), color="#333333", ha="left", rotation="vertical")
    
    pylab.text(len(ch)+1, 1, "Rest: %0.3f"%(rest), color="#AAAAAA", ha="right", rotation="horizontal")
    pylab.ylabel("$T_i$")
    pylab.title("Channels")
    ax2.set_xticks(np.arange(1,len(ch)+0.5))
    ax2.set_xlim(0.5,len(ch)+1)
    ax2.set_yticks([0.25,0.5,0.75,1.0])
    ax2.set_ylim([0,1.2])
    
    spines_to_remove = ['top', 'right']
    for spine in spines_to_remove:
        ax2.spines[spine].set_visible(False)
    ax2.xaxis.set_ticks_position('none')
    ax2.yaxis.set_ticks_position('none')
    
    savename = os.path.split(iv_file)[1]
    pylab.savefig(os.path.join(iv_dir,savename)+".png")
    #pylab.savefig(os.path.join(iv_dir,savename)+".pdf")
    if show_plots:    
        pylab.show()


# statistics of fitting
#if not 'all_c' in locals():
#    all_c = []
#all_c.append(c)

if False:
    pylab.hold(True)
    pylab.plot([x[0] for x in all_c])
    pylab.plot([x[1] for x in all_c])
    pylab.plot([x[2] for x in all_c])