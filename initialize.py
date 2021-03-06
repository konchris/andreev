# -*- coding: utf-8 -*-
"""
Initialization Scripts for a thousand of init lines

Created on Sat Mar 22 13:05:08 2014
All rights reserved by David Weber
@author: David Weber
"""
global _self
_self = None
import config

def init_files(_self):
    _self.f_li0 = None
    _self.f_li1 = None
    _self.f_li3 = None
    _self.f_li4 = None
    _self.f_agilent_voltage = None
    _self.f_agilent_current = None
    _self.f_motor = None
    _self.f_temp = None
    _self.f_ips = None
    _self.f_ips_2 = None
    _self.f_femto = None
    
    _self.f_config = None
    _self.hdf5_file = None
    
def open_files():
    from functions import close_logfile,set_logfile
    import os
    import hdf5_interface

    if not _self.f_li0 == None:
        _self.f_li0.close()
        _self.f_li1.close()
        _self.f_li3.close()
        _self.f_li4.close()
        _self.f_agilent_voltage.close()
        _self.f_agilent_current.close()
        _self.f_motor.close()
        _self.f_temp.close()
        _self.f_itc.close()
        _self.f_femto.close()
        _self.f_ips.close()
        _self.f_ips_2.close()

    if not _self.f_config == None:
        _self.f_config.close()
    if not _self.hdf5_file == None:
        _self.hdf5_file.close()
    close_logfile()
        
    d = str(_self.ui.editSetupDir.text())+str(_self.ui.editHeader.text())+"\\"    
    d_name = os.path.dirname(d)
    if not os.path.exists(d_name):
        os.makedirs(d_name)
    if config.save_good_old_txt:
        _self.f_li0 = open(d+"li0.txt", 'a')    # TODO os.path.join()
        _self.f_li1 = open(d+"li1.txt", 'a')
        _self.f_li3 = open(d+"li3.txt", 'a')
        _self.f_li4 = open(d+"li4.txt", 'a')
        _self.f_agilent_voltage = open(d+"agilent_new.txt", 'a')
        _self.f_agilent_current = open(d+"agilent_old.txt", 'a')
        _self.f_femto = open(d+"femto.txt", 'a')
        _self.f_motor = open(d+"motor.txt", 'a')
        _self.f_temp = open(d+"temp.txt", 'a')
        _self.f_itc = open(d+"itc.txt", 'a')
        _self.f_ips = open(d+"ips.txt", 'a') 
        _self.f_ips_2 = open(d+"ips_2.txt", 'a') 
        
    _self.f_config = open(d+"config.txt", 'a')
    _self.hdf5_file = hdf5_interface.hdf5_saving(d)
    set_logfile(d+"log.txt")      
    
def close_files():
    from functions import close_logfile,log
    if not _self.f_li0 == None:
        try:
            _self.f_li0.close()
            _self.f_li1.close()
            _self.f_li3.close()
            _self.f_li4.close()
            _self.f_femto.close()
            _self.f_motor.close()
            _self.f_temp.close()
            _self.f_itc.close()
            _self.f_ips.close()
            _self.f_ips_2.close()
        except Exception,e:
            log("Failed to Close a File",e)
            
    if not _self.f_config == None:
        try:
            _self.f_config.close()
        except Exception,e:
            log("Failed to Close Config File",e)
        
        _self.f_li0 = None
        _self.f_li1 = None
        _self.f_li3 = None
        _self.f_li4 = None
        _self.f_agilent_voltage = None
        _self.f_agilent_current = None
        _self.f_femto = None
        _self.f_motor = None
        _self.f_temp = None
        _self.f_itc = None
        _self.f_ips = None
        _self.f_ips_2 = None
        _self.f_config = None
        
    if not _self.hdf5_file == None:
        try:
            _self.hdf5_file.close()
        except Exception,e:
            log("Failed to Close HDF5 File",e)
        _self.hdf5_file = None
    close_logfile()

def write_config(text):
    from functions import log
    try:
        if not _self.f_config == None:
            _self.f_config.write(text)
            _self.f_config.flush()
    except Exception,e:
        log("Failed to write config",e)

def init_curvewidgets(_self):
    from guiqwt.builder import make
    
    _self.data_curve1 = make.curve([],[])
    _self.data_curve2 = make.curve([],[], yaxis="right", color="b")
    _self.data_curve3 = make.curve([],[])
    _self.data_curve4 = make.curve([],[], yaxis="right", color="b")
    _self.data_curve5 = make.curve([],[]) # magnet
    _self.data_curve5b = make.curve([],[], color="G")   # magnet 2
    _self.data_curve6 = make.curve([],[], yaxis="right", color="b")
    _self.data_curve6b = make.curve([],[], yaxis="right", color="g")
    _self.data_curve6c = make.curve([],[], yaxis="right", color="y")
    _self.data_curve6d = make.curve([],[], yaxis="right", color="r")
    _self.data_curve6e = make.curve([],[], yaxis="right", color="l")
    
    _self.data_curve7 = make.curve([],[])
    _self.data_curve8 = make.curve([1],[1], yaxis="right", color="b")
    _self.data_curve8b = make.curve([1],[1], yaxis="right", color="g")
    
    _self.data_curve9 = make.curve([],[], linestyle="NoPen", marker="Rect",  markersize=3, markeredgecolor="k", markerfacecolor="b") # SolidLine NoPen
    _self.data_curve10 = make.curve([],[],yaxis="right",color="b")
    
    _self.data_curve11 = make.curve([],[], linestyle="NoPen", marker="Rect" ,markersize=3, markeredgecolor="k", markerfacecolor="k") # SolidLine NoPen
    _self.data_curve12 = make.curve([],[], yaxis="right", linestyle="NoPen", marker="Ellipse",  markersize=4, markeredgecolor="k",markerfacecolor="r") # SolidLine NoPen
        
    
    _self.ui.cw1.plot.set_axis_title(_self.ui.cw1.plot.Y_LEFT, "AUX0/Sample")
    _self.ui.cw1.plot.set_axis_title(_self.ui.cw1.plot.Y_RIGHT, "AUX1/RRef")
    _self.ui.cw1.plot.set_axis_color(_self.ui.cw1.plot.Y_RIGHT, "MediumBlue")
    _self.ui.cw2.plot.set_axis_title(_self.ui.cw2.plot.Y_LEFT, "Motor Position")
    _self.ui.cw2.plot.set_axis_title(_self.ui.cw2.plot.Y_RIGHT, "Motor Speed (RPM)")
    _self.ui.cw2.plot.set_axis_color(_self.ui.cw2.plot.Y_RIGHT, "MediumBlue")
    _self.ui.cw3.plot.set_axis_title(_self.ui.cw3.plot.Y_LEFT, "Magnet (B)")
    _self.ui.cw3.plot.set_axis_title(_self.ui.cw3.plot.Y_RIGHT, "Temperatures (K)")
    _self.ui.cw3.plot.set_axis_color(_self.ui.cw3.plot.Y_RIGHT, "MediumBlue")
    _self.ui.cw4.plot.set_axis_title(_self.ui.cw4.plot.Y_LEFT, "Resistance (Ohm)")
    _self.ui.cw4.plot.set_axis_title(_self.ui.cw4.plot.Y_RIGHT, "Conductance (Go)")
    _self.ui.cw4.plot.set_axis_color(_self.ui.cw4.plot.Y_RIGHT, "MediumBlue")
    _self.ui.cw4.plot.set_axis_scale(_self.ui.cw4.plot.Y_RIGHT, "log")
    
    _self.ui.cw5.plot.set_axis_title(_self.ui.cw5.plot.Y_LEFT, "I (A)")
    _self.ui.cw5.plot.set_axis_title(_self.ui.cw5.plot.Y_RIGHT, "dI/dV")
    _self.ui.cw5.plot.set_axis_title(_self.ui.cw5.plot.X_BOTTOM, "Voltage (V)") 
    
    _self.ui.cw6.plot.set_axis_title(_self.ui.cw6.plot.Y_LEFT, "d2I/dV2 Sample")
    _self.ui.cw6.plot.set_axis_color(_self.ui.cw6.plot.Y_RIGHT, "MediumBlue")
    _self.ui.cw6.plot.set_axis_title(_self.ui.cw6.plot.Y_RIGHT, "d2I/dV2 Reference")  
    _self.ui.cw6.plot.set_axis_title(_self.ui.cw6.plot.X_BOTTOM, "Voltage (V)") 
    _self.ui.cw6.plot.set_axis_color(_self.ui.cw6.plot.Y_RIGHT, "DarkRed")
        
    _self.ui.cw1.plot.add_item(_self.data_curve1)
    _self.ui.cw1.plot.add_item(_self.data_curve2)
    
    _self.ui.cw2.plot.add_item(_self.data_curve3)
    _self.ui.cw2.plot.add_item(_self.data_curve4)
    
    _self.ui.cw3.plot.add_item(_self.data_curve5)
    _self.ui.cw3.plot.add_item(_self.data_curve5b)
    _self.ui.cw3.plot.add_item(_self.data_curve6)
    _self.ui.cw3.plot.add_item(_self.data_curve6b)
    _self.ui.cw3.plot.add_item(_self.data_curve6c)
    _self.ui.cw3.plot.add_item(_self.data_curve6d)
    _self.ui.cw3.plot.add_item(_self.data_curve6e)
    
    _self.ui.cw4.plot.add_item(_self.data_curve7)
    _self.ui.cw4.plot.add_item(_self.data_curve8)
    _self.ui.cw4.plot.add_item(_self.data_curve8b)
    
    _self.ui.cw5.plot.add_item(_self.data_curve9)
    _self.ui.cw5.plot.add_item(_self.data_curve10)
    _self.ui.cw6.plot.add_item(_self.data_curve11)
    _self.ui.cw6.plot.add_item(_self.data_curve12)
    
    _self.ui.cw1.plot.enable_used_axes()
    _self.ui.cw2.plot.enable_used_axes()
    _self.ui.cw3.plot.enable_used_axes()
    _self.ui.cw4.plot.enable_used_axes()
    _self.ui.cw5.plot.enable_used_axes()
    _self.ui.cw6.plot.enable_used_axes()


def init_variables(_self):
    import time
    _self._start_time = time.time()
    
    # holds data to plot in specialized plots
    _self.plot_data = {}
    _self.plot_data["new"] = [False,False,False,False]
    _self.plot_data["save"] = False
    _self.plot_data["x1"] = []
    _self.plot_data["y1"] = []
    _self.plot_data["x2"] = []
    _self.plot_data["y2"] = []
    _self.plot_data["x3"] = []
    _self.plot_data["y3"] = []
    _self.plot_data["x4"] = []
    _self.plot_data["y4"] = []    
    
    # holds all the data read from devices
    _self.data = {}
    _self.data["li_timestamp_0"] = []
    _self.data["li_aux0"] = []
    _self.data["li_aux1"] = []
    _self.data["li_0_x"] = []
    _self.data["li_0_y"] = []
    
    _self.data["li_timestamp_1"] = []
    _self.data["li_1_x"] = []
    _self.data["li_1_y"] = []
    
    _self.data["li_timestamp_3"] = []
    _self.data["li_3_x"] = []
    _self.data["li_3_y"] = []
    
    _self.data["li_timestamp_4"] = []
    _self.data["li_4_x"] = []
    _self.data["li_4_y"] = []
    
    _self.data["agilent_voltage_timestamp"] = []
    _self.data["agilent_voltage_voltage"] = []
    
    _self.data["agilent_current_timestamp"] = []
    _self.data["agilent_current_voltage"] = []

    _self.data["motor_timestamp"] = []
    _self.data["motor_pos"] = []
    _self.data["motor_cur"] = []
    _self.data["motor_vel"] = []
    
    _self.data["temp_timestamp"] = []
    _self.data["temp1"] = []
    _self.data["temp2"] = []
    
    _self.data["itc_timestamp"] = []
    _self.data["itc_temp1"] = []
    _self.data["itc_temp2"] = []
    _self.data["itc_temp3"] = []
    
    _self.data["ips_timestamp"] = []
    _self.data["ips_mfield"] = []
    
    _self.data["ips_2_timestamp"] = []
    _self.data["ips_2_mfield"] = []
    
    _self.data["femto_timestamp"] = []
    _self.data["femto_channela"] = []
    _self.data["femto_channelb"] = []
    
    # holds some config data like offset
    _self.config_data = {}

    _self.config_data["lockin_phases"] = [0,0,0,0]
    _self.config_data["main_index"] = 0
    _self.config_data["sub_index"] = 0
    
    # holds all the fields and boxes of the form with recent values
    _self.form_data = {}
    
    # amplifiers
    _self.config_data["offset_agilent_voltage"] = [0,0,0,0]
    _self.config_data["offset_agilent_current"] = [0,0,0,0]
    _self.config_data["offset_agilent_voltage"][0] = float(_self.ui.editOffsetVoltage.text())
    _self.config_data["offset_agilent_current"][0] = float(_self.ui.editOffsetCurrent.text())
    _self.config_data["offset_agilent_voltage"][1] = float(_self.ui.editOffsetVoltage_2.text())
    _self.config_data["offset_agilent_current"][1] = float(_self.ui.editOffsetCurrent_2.text())
    _self.config_data["offset_agilent_voltage"][2] = float(_self.ui.editOffsetVoltage_3.text())
    _self.config_data["offset_agilent_current"][2] = float(_self.ui.editOffsetCurrent_3.text())
    _self.config_data["offset_agilent_voltage"][3] = float(_self.ui.editOffsetVoltage_4.text())
    _self.config_data["offset_agilent_current"][3] = float(_self.ui.editOffsetCurrent_4.text())
    
    _self.config_data["offset_voltage"] = 0
    _self.config_data["offset_current"] = 0
    _self.config_data["range_voltage"] = 1
    _self.config_data["range_current"] = 1
    
    _self.factor_voltage = float(_self.ui.editFactorVoltage.text())
    _self.factor_current = float(_self.ui.editFactorCurrent.text())

    _self._excluded_splits = ["timestamp","li","femto"]
    
    _self.histogram_in_progress = False
    _self.iv_in_progress = False
    


def init_shutdowns(_self):
    _self.stop_measure = False
    _self.shutdown = False
    _self.temp_sweep_abort = False
    _self.offset_in_progress = False

def init_validators(_self):
    from PyQt4 import QtCore, QtGui
    # validators
    intValidator = QtGui.QIntValidator()
    intValidator.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
    doubleValidator = QtGui.QDoubleValidator()
    doubleValidator.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))

    # histogram
    _self.ui.editHistogramBias.setValidator(doubleValidator)
    _self.ui.editHistogramLower.setValidator(doubleValidator)
    _self.ui.editHistogramUpper.setValidator(doubleValidator)
    _self.ui.editHistogramOpeningSpeed.setValidator(intValidator)
    _self.ui.editHistogramClosingSpeed.setValidator(intValidator)
    # motor
    _self.ui.editLowerLimit.setValidator(doubleValidator)
    _self.ui.editUpperLimit.setValidator(doubleValidator)
    _self.ui.editSpeed.setValidator(intValidator)  
    # view
    _self.ui.editViewBegin.setValidator(intValidator)
    _self.ui.editViewEnd.setValidator(intValidator)
    _self.ui.editViewStep.setValidator(intValidator)
    _self.ui.editTimerInterval.setValidator(intValidator)
    _self.ui.editMaximumValues.setValidator(intValidator)
    # iv
    _self.ui.editIVTime.setValidator(intValidator)
    _self.ui.editIVMin.setValidator(doubleValidator)
    _self.ui.editIVMax.setValidator(doubleValidator)
    # temperature
    _self.ui.editTempSetpoint.setValidator(doubleValidator)
    _self.ui.editTempHeater.setValidator(intValidator)
    _self.ui.editTempP.setValidator(intValidator)
    _self.ui.editTempI.setValidator(intValidator)
    _self.ui.editTempD.setValidator(intValidator)
    _self.ui.editTempSweepStart.setValidator(doubleValidator)
    _self.ui.editTempSweepStop.setValidator(doubleValidator)
    _self.ui.editTempSweepStep.setValidator(doubleValidator)
    _self.ui.editTempSweepDelay.setValidator(doubleValidator)    
    # b-field
    _self.ui.editBMax.setValidator(doubleValidator)
    _self.ui.editBRate.setValidator(doubleValidator)
    # lockin
    _self.ui.editLIFreq.setValidator(doubleValidator)
    _self.ui.editLITC.setValidator(doubleValidator)
    _self.ui.editLIAmpl.setValidator(doubleValidator)
    _self.ui.editRate.setValidator(intValidator)
    # setup
    _self.ui.editFactorVoltage.setValidator(intValidator)
    _self.ui.editFactorCurrent.setValidator(intValidator)


def init_connections(_self):
    from PyQt4 import QtCore
    import gui_helper
    
    QtCore.QObject.connect(_self.ui.btnUltraStart, QtCore.SIGNAL("clicked()"), _self.measurement_btn_Acquire_Ultra)
    QtCore.QObject.connect(_self.ui.btnHistogramStart, QtCore.SIGNAL("clicked()"), _self.measurement_btn_Acquire_Histogram)
    QtCore.QObject.connect(_self.ui.btnIVStart, QtCore.SIGNAL("clicked()"), _self.measurement_btn_Acquire_IV)  
    QtCore.QObject.connect(_self.ui.btnBCircleStart, QtCore.SIGNAL("clicked()"), _self.measurement_btn_Acquire_B_Circle)
    QtCore.QObject.connect(_self.ui.btnBSweepStart, QtCore.SIGNAL("clicked()"), _self.measurement_btn_Acquire_B_Sweep)
    QtCore.QObject.connect(_self.ui.btnBIVMapStart, QtCore.SIGNAL("clicked()"), _self.measurement_btn_Acquire_B_IV_Map)
    QtCore.QObject.connect(_self.ui.btnSwitchingStart, QtCore.SIGNAL("clicked()"), _self.measurement_btn_Acquire_Switching)
    
    QtCore.QObject.connect(_self.ui.btnNature, QtCore.SIGNAL("clicked()"), gui_helper.send_to_nature)
    QtCore.QObject.connect(_self.ui.btnResetBeginTime, QtCore.SIGNAL("clicked()"), gui_helper.reset_begin_times)
    QtCore.QObject.connect(_self.ui.btnInitDevices, QtCore.SIGNAL("clicked()"), gui_helper.init_device_parameters)

    QtCore.QObject.connect(_self.ui.btnBStart, QtCore.SIGNAL("clicked()"), gui_helper.magnet_goto)   
    QtCore.QObject.connect(_self.ui.btnBInitMagnet, QtCore.SIGNAL("clicked()"), gui_helper.magnet_init)    
    QtCore.QObject.connect(_self.ui.btnBZeroMagnet, QtCore.SIGNAL("clicked()"), gui_helper.magnet_zero)   
    QtCore.QObject.connect(_self.ui.btnSwitchHeaterOn, QtCore.SIGNAL("clicked()"), gui_helper.switchheater_on)  
    QtCore.QObject.connect(_self.ui.btnSwitchHeaterOff, QtCore.SIGNAL("clicked()"), gui_helper.switchheater_off) 
    
    QtCore.QObject.connect(_self.ui.btnBStart_2, QtCore.SIGNAL("clicked()"), gui_helper.magnet_goto_2)   
    QtCore.QObject.connect(_self.ui.btnBInitMagnet_2, QtCore.SIGNAL("clicked()"), gui_helper.magnet_init_2)    
    QtCore.QObject.connect(_self.ui.btnBZeroMagnet_2, QtCore.SIGNAL("clicked()"), gui_helper.magnet_zero_2)   
    QtCore.QObject.connect(_self.ui.btnSwitchHeaterOn_2, QtCore.SIGNAL("clicked()"), gui_helper.switchheater_on_2)  
    QtCore.QObject.connect(_self.ui.btnSwitchHeaterOff_2, QtCore.SIGNAL("clicked()"), gui_helper.switchheater_off_2) 
    
    QtCore.QObject.connect(_self.ui.btnMeasurementStop, QtCore.SIGNAL("clicked()"), gui_helper.measurement_btn_Stop)
    
    QtCore.QObject.connect(_self.ui.btnUnbreak, QtCore.SIGNAL("clicked()"), gui_helper.motor_unbreak)
    QtCore.QObject.connect(_self.ui.btnBreak, QtCore.SIGNAL("clicked()"), gui_helper.motor_break)
    QtCore.QObject.connect(_self.ui.btnStop, QtCore.SIGNAL("clicked()"), gui_helper.motor_stop)
    QtCore.QObject.connect(_self.ui.btnMotorHome, QtCore.SIGNAL("clicked()"), gui_helper.motor_home)
    QtCore.QObject.connect(_self.ui.btnMotorSetLimit, QtCore.SIGNAL("clicked()"), gui_helper.motor_set_limit) 
    
    QtCore.QObject.connect(_self.ui.btnSetBias, QtCore.SIGNAL("clicked()"), gui_helper.set_bias) 
    QtCore.QObject.connect(_self.ui.btnBiasInvert, QtCore.SIGNAL("clicked()"), gui_helper.bias_invert)
    
    QtCore.QObject.connect(_self.ui.btnSaveStart, QtCore.SIGNAL("clicked()"), open_files)
    QtCore.QObject.connect(_self.ui.btnSaveStop, QtCore.SIGNAL("clicked()"), close_files)
    QtCore.QObject.connect(_self.ui.btnSaveDescription, QtCore.SIGNAL("clicked()"), gui_helper.save_description)
    
    QtCore.QObject.connect(_self.ui.btnOffset, QtCore.SIGNAL("clicked()"), _self.offset_correct)
    QtCore.QObject.connect(_self.ui.btnLockinSet, QtCore.SIGNAL("clicked()"), gui_helper.lockin_set)
    QtCore.QObject.connect(_self.ui.btnLIReadPhase, QtCore.SIGNAL("clicked()"), gui_helper.lockin_read_phase)
    QtCore.QObject.connect(_self.ui.btnLIZeroPhase, QtCore.SIGNAL("clicked()"), gui_helper.lockin_set_phase)
    QtCore.QObject.connect(_self.ui.btnLIResync, QtCore.SIGNAL("clicked()"), gui_helper.lockin_resync)
    
    QtCore.QObject.connect(_self.ui.btnTempSet, QtCore.SIGNAL("clicked()"), gui_helper.set_temp_parameters)
    QtCore.QObject.connect(_self.ui.btnTempSweep, QtCore.SIGNAL("clicked()"), _self.temp_sweep)
    QtCore.QObject.connect(_self.ui.btnTempSweepStop, QtCore.SIGNAL("clicked()"), gui_helper.temp_sweep_stop)
    QtCore.QObject.connect(_self.ui.btnTemperatureCustom, QtCore.SIGNAL("clicked()"), gui_helper.temp_custom)
    
    QtCore.QObject.connect(_self.ui.btnExecute, QtCore.SIGNAL("clicked()"), _self.execute)
    
    QtCore.QObject.connect(_self.ui.btnFemtoSet, QtCore.SIGNAL("clicked()"), gui_helper.femto_set)
    
    # switching
    QtCore.QObject.connect(_self.ui.btnSwitchSetHigh, QtCore.SIGNAL("clicked()"), gui_helper.switch_high)
    QtCore.QObject.connect(_self.ui.btnSwitchSetLow, QtCore.SIGNAL("clicked()"), gui_helper.switch_low)
    
    
    
    #QtCore.QObject.connect(_self.ui.editBias, QtCore.SIGNAL("clicked()"), gui_helper.lockin_resync)
    
    