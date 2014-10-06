import os
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

# initialize fitting by loading all theoretical ivs
#mar=MAR('.\\t_4k_0_33\\')
mar=MAR('.\\t_0k\\')
#mar=MAR('.\\t_4k_0_25\\')