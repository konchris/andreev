# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 15:16:08 2014

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
    DEV.motor.set_current_limit(int(_self.ui.editMotorCurrentLimit.text()))
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
    DEV.magnet.set_switchheater('OFF')

def lockin_set():
    rate = int(_self.ui.editRate.text())
    amplitude = float(_self.ui.editLIAmpl.text())
    DEV.lockin.set_rate(rate)
    DEV.lockin.set_amplitude(amplitude)

def lockin_read_phase():
    import numpy as np
    try:
        _self.config_data["lockin_phases"][0] = _self.config_data["lockin_phases"][0] + 180.0/3.141592*np.arctan(_self.data["li_0_y"][-1]/_self.data["li_0_x"][-1])    
        _self.config_data["lockin_phases"][1] = _self.config_data["lockin_phases"][1] + 180.0/3.141592*np.arctan(_self.data["li_1_y"][-1]/_self.data["li_1_x"][-1])
        _self.config_data["lockin_phases"][2] = _self.config_data["lockin_phases"][2] + 180.0/3.141592*np.arctan(_self.data["li_3_y"][-1]/_self.data["li_3_x"][-1])
        _self.config_data["lockin_phases"][3] = _self.config_data["lockin_phases"][3] + 180.0/3.141592*np.arctan(_self.data["li_4_y"][-1]/_self.data["li_4_x"][-1])
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
    bias = float(_self.ui.editBias.text())
    DEV.yoko.set_voltage(bias)
    DEV.yoko.output(True)


# temp
def set_temp_parameters():
    try:
        setpoint = float(_self.ui.editTempSetpoint.text())
        heater = int(_self.ui.editTempHeater.text())
        p = float(_self.ui.editTempP.text())
        i = float(_self.ui.editTempI.text())
        d = float(_self.ui.editTempD.text())
        
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
    
    
def execute():
    try:
        exec(str(_self.ui.editCommand.text()))
    except Exception,e:
        log("Execution failed",e)