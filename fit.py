# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 14:21:23 2012

@author: Daniel Schmid, improved by David Weber
"""
from scipy.optimize import leastsq
import numpy as np
from numpy import arctan #es funktioniert nicht mit allen atan funktionen
from array import array # kann verändert und verlängert werden


def fit_slm(data):
    """Fits to given data [[U],[I]] the Single Level Model"""
    # Funktionen # erst eigentliche Funktion 
    # dann Funktion für Abweichung von eigentlicher Funktion
    # z= ["a","Gamma=L1", "e0"]
    f = lambda z, u: z[0]*2*1.6e-19/4.135e-15*(4*z[1]*z[1])/(2*z[1])*(arctan(((u/2)-z[2])/(2*z[1]))+arctan(((u/2)+z[2])/(2*z[1])))
    ferr = lambda z, u, i: (f(z,u)-i) 
    
    z0 = [0.894208, 0.00576777, -0.235965]  #Anfangswerte
    
    z, success = leastsq(ferr, z0, args=(data[0],data[1]), maxfev=10000) # minimiert die Quadrate der Abweichungs-Funktion
    
    print("a="+str(z[0])+" L1="+str(z[1])+" e0="+str(z[2])+"  success="+ str(success))
    return (z,success)


