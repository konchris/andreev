import os
import scipy
import numpy as np

#from MARfit_David import mar    # data fitting


# set the fit parameter
_gap = 1370                 # uV
_punkte = 400               # sample points to interpolate
_vmin = 0.1                 # fitting min partial of gap
_vmax = 3.3                 # max voltage of gap
_iterations = 5000          # iterations for fit
_max_channels = 4           # starting value of channels
additional_info = True     # print additional information in plot
show_plots = True          # show plots after fit (else direct save)

def movingaverage(interval, window_size):
    window= np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')
    
def load_iv_files(directory, start="out", end=".txt"):
    iv_files = []
    for _file in os.listdir(directory):
        if _file.endswith(end):
            if not _file.startswith(start):
                iv_files.append(_file)
    iv_files.sort()
    print "Found %i IV-Files."%(len(iv_files))
    return iv_files


def load_iv_data(filename, index_u=1, index_i=2, skip=2):
    loaded_data = scipy.loadtxt(filename,unpack=True, skiprows=skip)
    
    # aquire parameters from file
    f = open(filename)
    line = f.readline()
    parameters =  [x.split(":") for x in line.split(",")]
    params = {}
    for x in parameters:
        if len(x) == 2:
            params[x[0]] = x[1]
    
    print "Loading %s"%filename
    u = loaded_data[index_u]
    i = loaded_data[index_i]
    
    return u,i,params

def align_direction(data):
    """Inverses Datasets according to first Dataset"""
    if data[0][0] > data[0][-1]:
        return_data = []
        for axe in data:
            axe = axe[::-1]
            return_data.append(axe)
    else:
        return_data = data        
    return return_data



def find_iv_offset(data=[[],[]],x_adjustment=2.5e-4, y_adjustment=1e-8, verbal=False, show_plot=False, plot_path=None):
    """Estimates the offset in x and y direction"""
    import pylab
    u,i = data[0],data[1]
    [u,i] = align_direction([u,i])
    length = len(u)
    if length%2==1:
        length += 1
        
    interp_factor = 30
    length *= interp_factor
    
    limit = min(abs(min(u)),abs(max(u)))*0.2
    new_u = np.linspace(-limit,limit,length,endpoint=True)
    new_i = np.interp(new_u, u, i)
    new_u,new_i = new_u[1:-1],new_i[1:-1]
    length -= 2
    
    if show_plot:
        
        
        pylab.close("all")
        pylab.plot(u,i,label="Raw Data")
        pylab.hold(True)
        pylab.plot(new_u,new_i,"b--",linewidth=2,label="Interpolate")
    
    u1,i1 = new_u[0:length/2],new_i[0:length/2]
    u2,i2 = new_u[length/2:],new_i[length/2:]
    diff = i1[:] + i2[::-1]
    diff_sum = np.sum(np.abs(diff))
    
    if verbal:
        print "limit %f, sample length %i"%(limit, length)
    dx_range = int(x_adjustment/(2*limit/length))
    dx = np.arange(-dx_range,dx_range,10)    # move along array elements
    
    
    _min,min_x = 999,0


    for x in dx:#range(len_x):
        center = length/2+x
        
        u1,i1 = new_u[dx_range+x : center] , new_i[dx_range+x : center]-new_i[center]
        u2,i2 = new_u[center:-dx_range+x] , new_i[center:-dx_range+x]-new_i[center]

        u2,i2 = u2[::-1],i2[::-1]
        diff_sum = np.sum(abs(i1+i2))

        if diff_sum < abs(_min):
            _min = abs(diff_sum)
            min_x = x

    
    x = min_x
    center = length/2+x
    u1,i1 = new_u[dx_range+x : center]-new_u[center] , new_i[dx_range+x : center]-new_i[center]
    u2,i2 = new_u[center:-dx_range+x]-new_u[center] , new_i[center:-dx_range+x]-new_i[center]
   
    diff = i1+i2[::-1]
    anti_sym = i1-i2[::-1]
    
    if verbal:
        print "Offset: %fuV %fnA"%(new_u[center]*1e6,new_i[center]*1e9)
    
    if plot_path != None:
        # plot offset correction
        pylab.ioff()
        pylab.plot(u1,i1,"r",label="Corrected")
        pylab.plot(u2,i2,"r")
        pylab.grid(True)
        pylab.legend()
        
    if show_plot:
        pylab.show()
    if plot_path != None:
        pylab.savefig(plot_path)
    
    du,di,shift = new_u[center],new_i[center],x
    
    # correct all u/i values with found offset
    u,i = u-du,i-di
    # find new center of i/v-sweep
    u_min = np.argmin(abs(u))
    
    # for anti symmetrize we must have two equally long
    # branches to add them up, so look for the maximum length
    # our output may have since we're no longer symmetric
    max_length = min(len(u)-u_min, u_min)    
    #print u_min, max_length
    #print u_min, u_min+max_length, u_min-max_length
    
    # thenn cut a bit of the edges to fit for both results
    anti_sym = (i[u_min:u_min+max_length] - i[u_min:u_min-max_length:-1])/2.0
    u,i = u[u_min:u_min+max_length],i[u_min:u_min+max_length]

    return du,di,shift,u,i,anti_sym

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

    def fit(self, messung, iter=10, channels=8, gap=180, punkte=400, Vmin=.15, Vmax=5.5 , ErrRef=1.0E-10, KickOff=0.0001, Strength=0.01, verbose=True, ReturnError=False):
        """messung: Messkurve vom Typ xy (nur monotone x-Werte)
        channels: Maximalzahl von Kanälen oder Anfangsverteilung als Liste
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
        if type(channels) is int:
            TNew=rand(channels)
        else:
            TNew=np.asarray(channels,dtype='d')
            channels=len(channels)
        ch0=np.zeros(channels,dtype='d')
        ch1=np.ones(channels,dtype='d')
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
            TNew=TNow+Strength*uniform(-1,1,channels)
            TNew=maximum(TNew,ch0)
            TNew=minimum(TNew,ch1)
            #if n%50==0: fxy.append(n, xy.math.log(ErrNow,10))
            if verbose:
                if n%2500==0: print str(n)+': Error=',ErrBest
        TBest.sort()
        TBest=TBest[::-1]
        return (TBest, ErrBest) if ReturnError else TBest


if __name__ == "__main__":
    iv_dir = r"C:\Users\David Weber\Desktop\Pb216\\"
    iv_files = load_iv_files(iv_dir)
    iv_file = iv_files[5]

       
    u,i,params = load_iv_data(os.path.join(iv_dir,iv_file))    
    u_min = np.argmin(abs(u))
    find_iv_offset([u,i])