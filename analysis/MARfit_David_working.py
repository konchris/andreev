﻿import os
import scipy
import numpy as np


class MAR:
    """Fitroutine für Multiple Andreev Refektionen"""
    
    def __init__(self,filename='.\\'):
        """lädt die MAR-Theoriekurven in den Einheiten 2*e*Delta/h gegen
        Delta."""
        #files=glob.glob(filename)
        files = []
        for _file in os.listdir(filename):
            #if _file.endswith(".dat"):
            if True:
                files.append(_file)
        files.sort()
        #print files
        
        if len(files)==0: raise Exception("Keine Dateien mit MAR-Daten gefunden.")
        
        #Ts=[f.split('\\')[-1].split('.')[0] for f in files]
        Ts=[float(f.split('\\')[-1]) for f in files]
        Ts=[0.]+Ts#[float(i)/1e4 for i in Ts]
        #Tfs=[xy.open(f, x=1, y=2) for f in files]
        #print Ts
        Tfs = []
        for f in files:
            _data = scipy.loadtxt(os.path.join(filename,f),unpack=True)
            Tfs.append(_data)
        for i in Tfs:
            #print i
            i=(i[0][:600],i[1][:600])
            #i[1]=
        Tf0=Tfs[0].copy()*0
        Tfs=[Tf0]+Tfs
        #print len(Ts), len(Tfs)
        self.Ts=Ts; self.Tfs=Tfs

    def kanalf(self,T,gap=1100,punkte=400,Vmin=0.,Vmax=5.5):
        """Theorie-IV-Kurve für eine Liste von Kanälen T
        oder eine einzelne Transmission T.
        gap: die zur Umrechnung verwendete Bandlücke in µeV
        punkte: Anzahl Punkte der Kurven (interpoliert)
        Vmin: untere Grenze fürs Fitten in Einheiten der Bandlücke
        Vmax: obere Grenze fürs Fitten in Einheiten der Bandlücke

        Rückgabewert: xy-Funktion"""
        Tx=np.arange(Vmin,Vmax,(Vmax-Vmin)/float(punkte),dtype='d')
        Tx*=(gap*1E-6)
        self.Tx=Tx
        Ty=[]
        for f in self.Tfs:
            newf=f.copy()
            newf[0]*=(gap*1E-6) #Delta
            newf[1]*=(gap*1E-6)*7.74809220561E-5 #2*e*Delta/h
            new_y = np.interp(Tx, newf[0], newf[1]) # was newf[1] = 
            #newf.equidistantx(x=Tx)
            Ty+=[new_y] # was newf[1]
        self.Tx=Tx; self.Ty=Ty
        self.len=len(self.Tx)
        if type(T) is float or type(T) is int: T=[float(T)]
        #return xy.xyFunction(Tx, self.kanal(T))
        return (Tx, self.kanal(T))

    def kanal(self,T):
        """Theorie-IV-Kurve für eine Liste von Kanälen T.
        Rückgabewert: nur y-Array"""
        mar=np.zeros(self.len)
        
        for Ti in T:
            #print Ti
            i=1
            while Ti>self.Ts[i]: i+=1
            p=float(Ti-self.Ts[i-1])/(self.Ts[i]-self.Ts[i-1])
            mar+=self.Ty[i-1]*(1-p)
            mar+=self.Ty[i]*p
        return mar

    def fit(self, messung, iter=10, chanels=8, gap=180, punkte=400, Vmin=.15, Vmax=5.5 , ErrRef=1.0E-10, KickOff=0.0001, Strength=0.01, verbose=True, ReturnError=False):
        """messung: Messkurve vom Typ xy (nur monotone x-Werte)
        chanels: Maximalzahl von Kanälen oder Anfangsverteilung als Liste
        gap: die zur Umrechnung verwendete Bandlücke in µeV
        punkte: Anzahl Punkte der Kurven (interpoliert)
        Vmin: untere Grenze fürs Fitten in Einheiten der Bandlücke
        Vmax: obere Grenze fürs Fitten in Einheiten der Bandlücke
        ErrRef: Temperatur in Einheiten von ErrBest
        Strength: Zufallsstörung
        KickOff: Rückschrittwahrscheinlichkeit
        verbose: Bei True wird alle 1000 Iterationen der Fehler ausgegeben
        ReturnError: Bei True wird das Tupel (Kanalliste, Fehler) zurückgegeben
                     bei False nur die Kanalliste.
        """
        
        from math import exp
        from numpy import mean,square,maximum,minimum
        from numpy.random import rand,uniform
        from random import random
        kanal=self.kanal

        Tx=np.arange(Vmin,Vmax,(Vmax-Vmin)/punkte)
        self.Tx=Tx
        Ty=[]
        for f in self.Tfs:
            newf=f.copy()
            #newf.equidistantx(x=Tx)
            #print len(Tx), len(newf[0]), len(newf[1])
            new_y = np.interp(Tx, newf[0], newf[1]) # was newf[1] = 

            Ty+=[new_y] # was newf[1]
        self.Tx=Tx; self.Ty=Ty
        self.len=len(Tx)

        m=messung.copy()
        m[0]*=1/(gap*1E-6) #Delta
        m[1]*=1/(gap*1E-6*7.74809220561E-5) #2*e*Delta/h
        #m.equidistantx(x=Tx)
        my = np.interp(Tx, m[0], m[1])
        #my = m[1]

        #Algorithmus nach AevCarlo
        if type(chanels) is int:
            TNew=rand(chanels)
        else:
            TNew=np.asarray(chanels,dtype='d')
            chanels=len(chanels)
        ch0=np.zeros(chanels,dtype='d')
        ch1=np.ones(chanels,dtype='d')
        ErrNow=ErrBest=mean(square(kanal(TNew)-my))
        TBest=TNow=TNew

        n=0
        while n<iter:
            n+=1
            ErrNew=mean(square(kanal(TNew)-my))
            #Always accept IV if new fit is better than previous one
            if (ErrNew-ErrNow<0): TNow,ErrNow=TNew,ErrNew 
            else: #Accept change if new fit is not too bad (ErrRef play the role of annealing temperature)
                if exp(-ErrNew/ErrRef)>random(): TNow,ErrNow=TNew,ErrNew
                #Accept change seldomly (even if new fit is very bad)
                elif random()<KickOff: TNow,ErrNow=TNew,ErrNew 
            # Check if new fit is the best one; if so, set best fit result
            if ErrNow<ErrBest: TBest,ErrBest=TNow,ErrNow 
            #Construct a new randomly changed temptative IV
            TNew=TNow+Strength*uniform(-1,1,chanels)
            TNew=maximum(TNew,ch0)
            TNew=minimum(TNew,ch1)
            #if n%50==0: fxy.append(n, xy.math.log(ErrNow,10))
            if verbose:
                if n%2500==0: print str(n)+': Error=',ErrBest
        TBest.sort()
        TBest=TBest[::-1]
        return (TBest, ErrBest) if ReturnError else TBest

# initialize fitting by loading all theoretical ivs
#mar=MAR('.\\t_4k_0_33\\')
mar=MAR('.\\t_0k\\')
#mar=MAR('.\\t_4k_0_25\\')

# set the fit parameter
_gap = 1370                 # uV  1370 
_punkte = 400               # sample points to interpolate
_vmin = 0.05                 # fitting min partial of gap
_vmax = 3.5                # max voltage of gap
_iterations = 20000          # iterations for fit
_max_channels = 5           # starting value of channels
_KickOff=0.01              # KickOff: Rückschrittwahrscheinlichkeit 0.002
_Strength=1e-3               # Strength: Zufallsstörung              0.2
additional_info = True      # print additional information in plot
show_plots = False          # show plots after fit (else direct save)

iv_dir = r"C:\Users\David Weber\Desktop\140911_Pb216_MAR01\ivs"
iv_files = []
for _file in os.listdir(iv_dir):
    if _file.endswith(".txt"):
        if not _file.startswith("out"):
            iv_files.append(_file)
iv_files.sort()
print "Found %i IV-Files."%(len(iv_files))

for iv_file in iv_files[:]:
    if iv_file != "iv_1410429384_4_0.txt":
        continue

    ### TORSTEN TORSTEN TORSTEN
    loaded_data = scipy.loadtxt(os.path.join(iv_dir,iv_file),unpack=True, skiprows=2)
    
    # aquire parameters from file
    f = open(os.path.join(iv_dir,iv_file))
    line = f.readline()
    parameters =  [x.split(":") for x in line.split(",")]
    params = {}
    for x in parameters:
        if len(x) == 2:
            params[x[0]] = x[1]
    
    
    print "\nProcessing %s"%iv_file
    u = loaded_data[1]
    i = loaded_data[2]
    i = np.array(i)/104000.0
    ### b HIER MUSS IN U UND I DIE RAW-DATEN SEIN
    
    u_min = np.argmin(abs(u))
    
    
    if True:    # DEBUG
        import pylab
        pylab.close("all")
        pylab.plot(u,i)
        ax = pylab.gca()
        ax.set_xlim([-0.01,0.01])
        ax.grid()
        pylab.show()
    
    # change the direction and only take one branch (+ or -)
    if u[0] < u[-1]:
        u = u[u_min:]
        i = i[u_min:]
    else:
        u = u[u_min:0:-1]
        i = i[u_min:0:-1]
    
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
    c = mar.fit(messung=mar1, iter=_iterations, chanels=_max_channels, gap=_gap, punkte=_punkte, Vmin=_vmin, Vmax=_vmax, ErrRef=1E-10, KickOff=_KickOff, Strength=_Strength); c #was gap=180 # kickoff 2e-4 # strength=0.1
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
    no_channel = 4e-2       # transmission indicating no real channel anymore
    pos_x,pos_y = 0.5,1.0
    
    
    pylab.axes()
    ax1 = pylab.gca()
    
    #ax3 = ax1.twiny()
    #ax3.set_xlabel("U ($\Delta$)")
    
    from matplotlib.patches import Rectangle
    extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
    
    ax1.set_xlabel("U ($\Delta$)")
    ax1.set_ylabel("I ($\mu$A)")
    ax1.set_title("MAR")
    ax1.hold("False")
    pl_fit, = ax1.plot(fit[0]*u_factor, fit[1]*i_factor, color = set2[1], linewidth=2,label="Fit %2.2f $G_0$"%(np.sum(c)))
    ax1.hold("True")
    pl_data, = ax1.plot(mar1[0]*u_factor, mar1[1]*i_factor, color = set2[4], linewidth=2,label="Experimental Data")
    
    #if additional_info:
    #    pl_data = ax1.plot(u*u_factor, i_linear*i_factor, color = set2[2], linewidth=1,label="Excess Current %2.2f $G_0$"%(p[0]*12906))
    
    ax1.set_xlim(xmin=0)
    ax1.set_ylim(ymin=0)
    ax1.set_xticks([1,2,3,4])
    
    ax1.legend(loc=2)    
    ax1.grid()
    if additional_info:
        #pl_data = ax1.plot(u*u_factor, i_linear*i_factor, color = set2[2], linewidth=1,label="Excess Current %2.2f $G_0$"%(p[0]*12906))
        #ax1.text(max(u*u_factor)*0.1,max(i*i_factor)*0.8, "Gap: %2.3fmeV"%(_gap/1000.0),ha="left")
        #ax1.text(max(u*u_factor)*0.1,max(i*i_factor)*0.75, "T: %2.1fK"%(float(params["temp2"])),ha="left")
        ax1.legend([pl_fit,pl_data,extra,extra],["Fit %2.2f $G_0$"%(np.sum(c)),"Data","$\Delta$ = %2.3f meV"%(_gap/1000.0),r"T$\,$ = %2.1f K"%(float(params["temp2"])) ],loc=2)
    else:
        ax1.legend([pl_fit,pl_data],["Fit","Data"],loc=2)
    """for i in range(len(c)):
        if c[i] < no_channel:
            rest = np.sum(c[i:])
            pylab.text(pos_x,pos_y-i*0.05,"Dropped:\t%f $G_0$"%(rest))
            break
        pylab.text(pos_x,pos_y-i*0.05,"Channel %i:\t%f $G_0$"%(i+1,c[i]))"""
    
    ch = [x for x in c if x >= no_channel]
    ch_rest = [x for x in c if x < no_channel]
    rest = np.sum(ch_rest)
    
    
    # PLOTTING THE CHANNELS
    pylab.axes([0.55, 0.15, 0.3, 0.3])
    ax2 = pylab.gca()
    pylab.bar(np.array(range(len(ch)))+1-0.4,ch, facecolor=set2[1], width=0.8)
    
    # CHANNEL TRANSMISSIONS
    ch_height_par = 3
    for i in range(len(ch)):
        pylab.text(i+1, ch[i]+ch[0]/ch_height_par, "%0.2f"%(ch[i]), color="#333333", ha="left", rotation="vertical")
    
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
    if True:    
        pylab.show()


# statistics of fitting
if not 'all_c' in locals():
    all_c = []
all_c.append(c)

if False:
    pylab.hold(True)
    pylab.plot([x[0] for x in all_c])
    pylab.plot([x[1] for x in all_c])
    pylab.plot([x[2] for x in all_c])