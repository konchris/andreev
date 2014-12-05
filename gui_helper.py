# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 15:16:08 2014
All rights reserved by David Weber
@author: David Weber
"""
import devices_andreev as DEV
from functions import log

global _self
_self = None

def send_to_nature():
    from PyQt4 import QtGui
    QtGui.QMessageBox.question(_self, 'Export',
            "Upload in progress......", QtGui.QMessageBox.Ok)


def reset_begin_times():
    import time
    _self.begin_time_b2 = time.time()
    _self.begin_time_histogram = time.time()
    _self.begin_time_ultra = time.time()
    _self.begin_time_iv = time.time()
    _self.begin_time_b_circle = time.time()
            
            
def init_device_parameters():
    motor_set_limit()        # sets limits for motor
    lockin_set()             # sets lockin parameters
    lockin_read_phase()  
    lockin_set_phase()       # set phase to zero
    femto_set()
    set_bias()               # sets bias to last value
    _self.offset_correct()

# motor
def motor_break(speed=None, quiet=False):
    if speed == None:
        speed = float(_self.ui.editSpeed.text())
    DEV.motor.set_velocity(-speed)
    if not quiet:
        log("Motor break with %f"%(-speed))
def motor_unbreak(speed=None, quiet=False):
    if speed == None:
        speed = float(_self.ui.editSpeed.text())
    DEV.motor.set_velocity(speed)
    if not quiet:
        log("Motor unbreak with %f"%(speed))
def motor_stop():
    DEV.motor.set_velocity(0)
    log("Motor stop")
def motor_home():
    DEV.motor.set_home()
    log("Motor homing")
    
def motor_set_limit():
    DEV.motor.set_lower_limit(float(_self.ui.editLowerLimit.text()))
    DEV.motor.set_upper_limit(float(_self.ui.editUpperLimit.text()))
    DEV.motor.set_current(int(_self.ui.editMotorCurrent.text()))
    log("Motor set limits %f,%f"%(float(_self.ui.editLowerLimit.text()),
                                  float(_self.ui.editUpperLimit.text())))

# femto
def ch_a_up():
    DEV.femto.increase_amplification(0)
    log("Femto decrease a")
def ch_a_down():
    DEV.femto.decrease_amplification(0)
    log("Femto decrease b")
def ch_b_up():
    DEV.femto.increase_amplification(1)
    log("Femto increase a")
def ch_b_down():
    DEV.femto.decrease_amplification(1)
    log("Femto increase b")
def femto_set(a=0,b=0):
    if int(_self.form_data["editFactorVoltage"]) == 10:
        a = 0
    if int(_self.form_data["editFactorVoltage"]) == 100:
        a = 1
    if int(_self.form_data["editFactorVoltage"]) == 1000:
        a = 2
    if int(_self.form_data["editFactorVoltage"]) == 10000:
        a = 3
    
    if int(_self.form_data["editFactorCurrent"]) == 10:
        b = 0
    if int(_self.form_data["editFactorCurrent"]) == 100:
        b = 1
    if int(_self.form_data["editFactorCurrent"]) == 1000:
        b = 2
    if int(_self.form_data["editFactorCurrent"]) == 10000:
        b = 3
    
    _self.config_data["offset_voltage"] = _self.config_data["offset_agilent_voltage"][a]
    _self.config_data["offset_current"] = _self.config_data["offset_agilent_current"][b]
    _self.config_data["range_voltage"] = a
    _self.config_data["range_current"] = b
    DEV.lockin.femto_set(a,b)

def save_description():
    import os
    from functions import logfile,set_logfile
    desc = _self.ui.textDescription.toPlainText()
    
    try:
        d = str(_self.ui.editSetupDir.text())+str(_self.ui.editHeader.text())+"\\"    
        d_name = os.path.dirname(d)
        if not os.path.exists(d_name):
            os.makedirs(d_name)
        if logfile == None:
            set_logfile(d+"log.txt")
        log("========= LOG =========")
        for line in desc.split('\n'):
            log(line)
        log("=======================")
    except Exception,e:
        log("Description Error",e)


# magnet
# FIRST IPS
def magnet_goto():
    try:
        field = float(_self.ui.editBMax.text())
        rate = float(_self.ui.editBRate.text())
    except:
        field = 0
        rate = 0.01
    print "field: %f, rate: %f"%(field,rate)
    DEV.magnet.SetField(field,rate)
def magnet_init():
    DEV.magnet.initialize()
def magnet_zero():
    try:
        rate = float(_self.ui.editBRate.text())
    except:
        rate = 0.1
    DEV.magnet.ZeroField(rate)
def switchheater_on():
    DEV.magnet.set_switchheater('ON')
def switchheater_off():
    DEV.magnet.set_switchheater('zeroOFF')

# SECOND IPS
def magnet_goto_2():
    try:
        field = float(_self.ui.editBMax_2.text())
        rate = float(_self.ui.editBRate_2.text())
    except:
        field = 0
        rate = 0.01
    print "field: %f, rate: %f"%(field,rate)
    DEV.magnet_2.SetField(field,rate)
def magnet_init_2():
    DEV.magnet_2.initialize()
def magnet_zero_2():
    try:
        rate = float(_self.ui.editBRate_2.text())
    except:
        rate = 0.1
    DEV.magnet_2.ZeroField(rate)
def switchheater_on_2():
    DEV.magnet_2.set_switchheater('ON')
def switchheater_off_2():
    DEV.magnet_2.set_switchheater('zeroOFF')


def lockin_set():
    rate = int(_self.ui.editRate.text())
    amplitude = float(_self.ui.editLIAmpl.text())
    output_enabled = bool(_self.form_data["checkLIOutputEnabled"])
    tc = float(_self.ui.editLITC.text())
    freq = float(_self.ui.editLIFreq.text())
    order = _self.ui.comboLIOrder.currentIndex()+1
    coupling = _self.ui.checkLIAC.isChecked()
    DEV.lockin.set_rate(rate)
    DEV.lockin.set_amplitude(amplitude, output=output_enabled)
    DEV.lockin.set_frequency(freq,tc,order)
    DEV.lockin.set_ac(coupling)

def lockin_resync():
    DEV.lockin.resync()

def lockin_read_phase():
    import numpy as np
    try:
        _self.config_data["lockin_phases"][0] = _self.config_data["lockin_phases"][0] - 180.0/3.141592*np.arctan(_self.data["li_0_y"][-1]/_self.data["li_0_x"][-1])    
        _self.config_data["lockin_phases"][1] = _self.config_data["lockin_phases"][1] - 180.0/3.141592*np.arctan(_self.data["li_1_y"][-1]/_self.data["li_1_x"][-1])
        _self.config_data["lockin_phases"][2] = _self.config_data["lockin_phases"][2] - 180.0/3.141592*np.arctan(_self.data["li_3_y"][-1]/_self.data["li_3_x"][-1])
        _self.config_data["lockin_phases"][3] = _self.config_data["lockin_phases"][3] - 180.0/3.141592*np.arctan(_self.data["li_4_y"][-1]/_self.data["li_4_x"][-1])
        _self.ui.editLIPhase0.setText(str(round(_self.config_data["lockin_phases"][0],2)))
        _self.ui.editLIPhase1.setText(str(round(_self.config_data["lockin_phases"][1],2)))
        _self.ui.editLIPhase3.setText(str(round(_self.config_data["lockin_phases"][2],2)))
        _self.ui.editLIPhase4.setText(str(round(_self.config_data["lockin_phases"][3],2)))
    except Exception,e:
        log("Failed to read phase",e)
    
def lockin_set_phase():
    try:
        DEV.lockin.set_phases(
            _self.config_data["lockin_phases"][0],
            _self.config_data["lockin_phases"][1],
            _self.config_data["lockin_phases"][2],
            _self.config_data["lockin_phases"][3]
            )
    except Exception,e:
        log("Failed to set phase",e)


def measurement_btn_Stop():
    _self.stop_measure = True
    
def temp_sweep_stop():
    _self.temp_sweep_abort = True
    
def set_bias():
    try:     
        bias = float(_self.ui.editBias.text())
        DEV.yoko.set_voltage(bias)
        DEV.yoko.output(True)
    except Exception,e:
        log("Failed to set Bias",e)


# temp
def set_temp_parameters():
    try:
        setpoint = float(_self.ui.editTempSetpoint.text())
        heater = int(_self.ui.editTempHeater.text())
        p = float(_self.ui.editTempP.text())
        i = float(_self.ui.editTempI.text())
        d = float(_self.ui.editTempD.text())
        ramp = abs(float(_self.form_data["editTempRamp"]))
                
        if ramp < 0.1:
            DEV.lakeshore.set_setpoint_ramp(ramp=False, output=1)
        else:
            DEV.lakeshore.set_setpoint_ramp(ramp=True, output=1, rate=ramp)
            
        DEV.lakeshore.set_setpoint(setpoint)
        DEV.lakeshore.set_heater_range(heater)
        DEV.lakeshore.set_pid(p,i,d)
        
        
    except Exception,e:
        log("New Temp was not accepted",e)
        
def temp_custom():
    try:
        val_1a = _self.ui.comboTemperatureDisplay1a.currentIndex()
        val_1b = _self.ui.comboTemperatureDisplay1b.currentIndex()+1
        val_2a = _self.ui.comboTemperatureDisplay2a.currentIndex()
        val_2b = _self.ui.comboTemperatureDisplay2b.currentIndex()+1
        val_3a = _self.ui.comboTemperatureDisplay3a.currentIndex()
        val_3b = _self.ui.comboTemperatureDisplay3b.currentIndex()+1
        val_4a = _self.ui.comboTemperatureDisplay4a.currentIndex()
        val_4b = _self.ui.comboTemperatureDisplay4b.currentIndex()+1

        DEV.lakeshore.set_display(6)    # custom display
        DEV.lakeshore.set_display_field(1,val_1a,val_1b)
        DEV.lakeshore.set_display_field(2,val_2a,val_2b)
        DEV.lakeshore.set_display_field(3,val_3a,val_3b)
        DEV.lakeshore.set_display_field(4,val_4a,val_4b)
    except Exception,e:
        log("New Display Setup not accepted",e)
        


def keyPressEvent_Bias(self, event):
    
    from PyQt4 import QtCore
    key = event.key()
    if key == QtCore.Qt.Key_Return: 
        set_bias()
    
    