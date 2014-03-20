import visa
import numpy as np

"""
visa.get_instruments_list(use_aliases=True)
del NC
NC=visa.instrument('GPIB0::%i'%9, delay=0.1, term_chars=';\n')

#- test stuff
NC.write('*RST')
NC.write('*CLS')
NC.ask('*IDN?')
NC.ask('QUNIT?1')
float(NC.ask('QSAMP?1')[:-1])
#- construct CX-1030 calibration table"""
if 1:
    Rmin=46.0
    Rmax=14291.5
    
    R1=np.linspace(257.0, 510, 119)
    R2=np.linspace(46.10, 240.0, 19)
    R=np.hstack((R1, R2))
    R.sort()

    r=(2*np.log10(R)-np.log10(Rmax)-np.log10(Rmin))/(np.log10(Rmax)-np.log10(Rmin))
    T=55.34924-97.76682*np.cos(np.arccos(r))+68.8287*np.cos(2*np.arccos(r))-38.5868*np.cos(3*np.arccos(r))+17.08834*np.cos(4*np.arccos(r))-6.3504*np.cos(5*np.arccos(r))+2.93285*np.cos(6*np.arccos(r))-2.35006*np.cos(7*np.arccos(r))+1.97358*np.cos(8*np.arccos(r))-1.20816*np.cos(9*np.arccos(r))+0.38118*np.cos(10*np.arccos(r))
    print R
    print T
if 1:
    import matplotlib.pyplot as plt
    plt.plot(T, R, 'bo')    
    plt.show()
"""
if 1:
    cmd='SCALT5,1,CX-1030-CU-THz-hi,-1.0,'
    table=''
    for i in range(len(R)):
        table+='%f,%f,'%(T[i], R[i])
        
    table+='$'
    cmd+=table
print(cmd[0:60])
cmd
#-- add Calibration table to Neocera Mem
cmd='SCALT5,1,CX-1030-CU-THz-hi,-1.0,291.582176,46.100000,158.131704,66.533333,$'
NC.write(cmd)

#-- send in blocks
from time import sleep
NC.write('SCALT5,1,CX-1030-CU-THz-Hi,-1.0,')
for i in range(len(R)):
    NC.write('%f,%f,'%(T[i], R[i]))
    sleep(0.25)
NC.write('$;')"""
