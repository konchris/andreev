# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 20:50:03 2013

@author: David Weber
"""

# OLD STUFF

#devices_andreev

"""        
try:
    femto=FEMTO(1,'DLPCA200')
    log("DLPCA Connected")
except Exception,e:
    log("DLPCA not found!",e)
    femto=None        
"""
"""        
try:
    motor=MOTOR()
    motor.disable()
    log("Motor Port Found")
except Exception,e:
    log("Motor not found!",e)
    motor=None
"""
"""        
try:
#    #yoko=YOKO7651(14)
    yoko=GS200(14)
    log("Yokogawa Voltage Source")
except Exception,e:
    log("Yokogawa Voltage Source not found!",e)
    yoko=None
"""
#try:
#    agilent_mm=AGILENT_MM(22)
#    log("Agilent Multimeter")
#except Exception,e:
#    log("Agilent Multimeter not found!",e)
#    agilent_mm=None

#try:
#    lakeshore=LAKESHORE(12)
#    log("Lakeshore Temperature Controller")
#except Exception,e:
#    log("Lakeshore Temperature Controller not found!",e)
#    lakeshore=None

"""
try:
    keithley=KEITHLEY2000(13)
    log("Keithley Multimeter")
except Exception,e:
    log("Keithley Multimeter not found!",e)
    keithley=None
"""
"""    
try:
    sr830_first=SR830(11)
    log("SR830 LockIn First")
except Exception,e:
    log("SR830 LockIn not found!",e)
    sr830_first=None
"""

#try:    
#    sr830_second=SR830(10)
#    log("SR830 LockIn Second")
#except Exception,e:
#    log("SR830 LockIn not found!",e)
#    sr830_second=None


     
       
                
        """
        first_r = -1
        first_theta = -1
        first_theta_ref = -1
        
        if DEV.sr830_first != None:
            try:
                first_values = DEV.sr830_first.get_values(3,4,9)
                first_r = first_values[0]
                first_theta = first_values[1]
                first_theta_ref = first_values[2]
            except:
                print "Communication with SR830 First failed!"
        
        self.data_array["First R"].append(first_r)
        self.data_array["First Theta"].append(first_theta)
        self.data_array["First ThetaRef"].append(first_theta_ref)
        """
        
        """
        self.ui.comboFirstSens.setCurrentIndex(DEV.sr830_first.get_sens_index())
        self.ui.comboFirstTC.setCurrentIndex(DEV.sr830_first.get_tc_index())
        if not self.ui.editFirstFrequency.hasFocus():
            self.ui.editFirstFrequency.setText(DEV.sr830_first.get_freq())
        self.ui.editFirstAmplitudeRead.setText(DEV.sr830_first.get_ac())
        self.ui.editFirstPhaseRead.setText(str(theta_ref))
        """      