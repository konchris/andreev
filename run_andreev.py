# -*- coding: utf-8 -*-
"""
All rights reserved by David Weber
@author: David Weber
"""
import config
import sys
import os
from PyQt4 import QtCore, QtGui
from gui_andreev import Ui_MainWindow
import devices_andreev as DEV

import thread
import time  
import numpy as np

from guidata.qt.QtCore import QTimer#,SIGNAL


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from functions import *

# exported self written functions
import initialize,refresh_display,gui_helper
import hdf5_interface as hdf

def collect_garbage():
    import gc
    gc.collect()

class main_program(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        DEV.app = app
        
       
        initialize._self = self
        refresh_display._self = self
        gui_helper._self = self
             
        #Read all the saved default values 
        try:
            read_config(self.ui)
        except Exception,e:
            print e            
            log("Can't read config file")
        
 
        # initialize.py - most of long initializations 
        initialize.init_connections(self)            
        initialize.init_variables(self)
        initialize.init_curvewidgets(self)
        initialize.init_files(self)
        initialize.init_shutdowns(self)
        initialize.init_validators(self)       
        
        #########################################################
        ##############    REFRESH DISPLAY     ###################
        #########################################################
        # periodic timer for refresh, value is changed by gui   
        self.timer_display = QTimer()
        self.timer_display.timeout.connect(refresh_display.refresh_display)
        self.timer_display.start(250)
        
        self.html_timer = QTimer()
        self.html_timer.timeout.connect(self.slow_timer)
        self.html_timer.start(30000)
        
        self.form_data = {}
        #self.ui.cw1.plot.set_axis_scale
        #########################################################
        ############## MEASUREMENT PARAMETERS ###################
        #########################################################
        #self.rref = 122120.0 # grounded one
        self.rref = 104000.0 # floating one
        self.wiring = 620.0


        #########################################################
        ##############   MEASUREMENT THREAD   ###################
        #########################################################
        # lock to synchronize access
        self.data_lock = thread.allocate_lock()
        thread.start_new_thread(self.measurement_thread,())    

    def slow_timer(self):
        export_html(self.ui)
        
        if not self.f_config == None:
            self.f_config.flush()
        
    # offset
    def offset_correct(self, delay=1):
        bias = DEV.yoko.get_voltage()
        self.offset_in_progress = True
        DEV.yoko.set_voltage(0)
        DEV.yoko.output(True)

        DEV.lockin.set_amplitude(0.01, output=False)
        
        # time to settle 0 value
        for i in range(10):
            app.processEvents()
            time.sleep(delay/10.0)
        
        # flush cache
        DEV.lockin.get_data_list(averages=1)
        DEV.agilent_new.get_data_list()
        DEV.agilent_old.get_data_list()
        
        # backup recent values
        a,b = DEV.lockin.femto_get()
        offset_a,offset_b = [0,0,0,0],[0,0,0,0]
        self.config_data["offset_voltage"] = 0
        self.config_data["offset_current"] = 0
        self.config_data["offset_agilent_voltage"] = [0,0,0,0]
        self.config_data["offset_agilent_current"] = [0,0,0,0]
        
        for i in range(4):
            DEV.lockin.femto_set(i,i)
    
            # discard data
            for j in range(10):
                app.processEvents()
                time.sleep(delay/10.0)
            DEV.agilent_new.get_data_list()
            DEV.agilent_old.get_data_list()
            
            # gather new data
            for j in range(10):
                app.processEvents()
                time.sleep(delay/10.0)
            
            new_data = DEV.agilent_new.get_data_list()
            offset_voltage = np.average(new_data["voltage"])
            old_data = DEV.agilent_old.get_data_list()
            offset_current = np.average(old_data["voltage"])

            offset_a[i] = offset_voltage
            offset_b[i] = offset_current
            log("Offset Agilent Voltage %fmV"%(offset_voltage*1e3))
            log("Offset Agilent Current %fmV"%(offset_current*1e3))
            
            time.sleep(delay/10.0)
        
        for i in range(4):
            self.config_data["offset_agilent_voltage"][i] = offset_a[i]
            self.config_data["offset_agilent_current"][i] = offset_b[i]
            
        self.ui.editOffsetVoltage.setText(str(round(self.config_data["offset_agilent_voltage"][0]*1e3,6)))
        self.ui.editOffsetCurrent.setText(str(round(self.config_data["offset_agilent_current"][0]*1e3,6)))
        self.ui.editOffsetVoltage_2.setText(str(round(self.config_data["offset_agilent_voltage"][1]*1e3,6)))
        self.ui.editOffsetCurrent_2.setText(str(round(self.config_data["offset_agilent_current"][1]*1e3,6)))
        self.ui.editOffsetVoltage_3.setText(str(round(self.config_data["offset_agilent_voltage"][2]*1e3,6)))
        self.ui.editOffsetCurrent_3.setText(str(round(self.config_data["offset_agilent_current"][2]*1e3,6)))
        self.ui.editOffsetVoltage_4.setText(str(round(self.config_data["offset_agilent_voltage"][3]*1e3,6)))
        self.ui.editOffsetCurrent_4.setText(str(round(self.config_data["offset_agilent_current"][3]*1e3,6)))

        gui_helper.femto_set(a,b) 
        DEV.yoko.set_voltage(bias)
        amplitude = float(self.form_data["editLIAmpl"])
        output_enabled = bool(self.form_data["checkLIOutputEnabled"])

        DEV.lockin.set_amplitude(amplitude, output=output_enabled)
               
        
        for i in range(10):
            app.processEvents()
            time.sleep(delay/10.0)

        # flush data to /dev/null
        DEV.lockin.get_data_list(averages=1)
        DEV.agilent_new.get_data_list()
        DEV.agilent_old.get_data_list()
        self.offset_in_progress = False

  
    def aquire_histogram(self):
        self.stop_measure = False
        self.histogram_in_progress = True
        
        # init bias        
        bias = float(self.form_data["editHistogramBias"])

        DEV.yoko.set_voltage(bias)
        DEV.yoko.output(True)
    
        log("Histogram Start")
        breaking = True         # sets direction of motor
        cold_timer = 0
        histo_sleep = 0.1
        
        self.begin_time_histogram = time.time()
        if not self.f_config == None:
            self.f_config.write("HISTOGRAM_OPEN\t%15.15f\n"%(self.begin_time_histogram))
        try:         
            while not self.stop_measure:
                try:
                    # update values
                    resistance = abs(self.data["agilent_voltage_voltage"][-1] / self.data["agilent_current_voltage"][-1] * self.rref)
                    lower_res = float(self.form_data["editHistogramLower"])
                    upper_res = float(self.form_data["editHistogramUpper"])
                    cold_time = float(self.form_data["editHistogramColdTime"])
                    bias = float(self.form_data["editHistogramBias"])
                    if not self.offset_in_progress:
                        DEV.yoko.set_voltage(bias)
                    
                    # if sample broken
                    if resistance > upper_res:  
                        # check for cold_time timeout
                        if cold_timer > 0:
                            cold_timer -= histo_sleep
                        else:   # if timeout expired
                            if breaking == True: 
                                self.begin_time_histogram = time.time()
                                if not self.f_config == None:
                                    self.f_config.write("HISTOGRAM_CLOSE\t%15.15f\n"%(self.begin_time_histogram))
                                self.config_data["main_index"] += 1
                                log("Main Index %i"%(self.config_data["main_index"]))
                                self.config_data["sub_index"] = 0
                            breaking = False    # if resistance high -> CLOSE
                            
                        
                    # if sample closed
                    if resistance < lower_res:
                        if cold_timer > 0:
                            cold_timer -= histo_sleep
                        else:   # if timeout expired
                            if breaking == False: 
                                self.begin_time_histogram = time.time()
                                if not self.f_config == None:
                                    self.f_config.write("HISTOGRAM_OPEN\t%15.15f\n"%(self.begin_time_histogram))   
                                self.config_data["main_index"] += 1
                                self.config_data["sub_index"] = 0
                            breaking = True     # if resistance low -> BREAK
                    
                    if resistance < upper_res and resistance > lower_res:
                        cold_timer = cold_time
                    
                    if breaking:
                        gui_helper.motor_break(int(self.form_data["editHistogramOpeningSpeed"]), quiet=True)
                    else:
                        gui_helper.motor_unbreak(int(self.form_data["editHistogramClosingSpeed"]), quiet=True)
                        
                    # if escape on motor limit hit
                    if bool(self.form_data["checkHistogramEscape"]):
                        if DEV.motor.higher_bound or DEV.motor.lower_bound:
                            log("Motor reached its bounds, escaping histogram!")
                            break
                    else:
                        if DEV.motor.higher_bound:
                            log("Motor reached its bounds, trying to break again in 10s!")
                            time.sleep(10)
                            breaking = True
                        if DEV.motor.lower_bound:
                            log("Motor reached its bounds, trying to close again in 10s!")
                            time.sleep(10)
                            breaking = False
                except Exception,e:
                    log("Histogram inner failure",e)
                time.sleep(histo_sleep) 
        except Exception,e:
            log("Histogram outer failure",e)
        finally:
            DEV.motor.stop()
        DEV.motor.stop()
        self.histogram_in_progress = False
        log("Histogram Stop")
    
    
    
    
    def aquire_ultra(self):
        self.stop_measure = False
        self.histogram_in_progress = True
        # init bias        
        bias = float(self.form_data["editHistogramBias"])

        DEV.yoko.set_voltage(bias)
        DEV.yoko.output(True)
    
        log("Ultra Start")
        breaking = True         # sets direction of motor
        last_engage = 100
        ultra_sleep = 0.1

        self.config_data["main_index"] = 0  
        self.config_data["sub_index"] = 0
        
        self.begin_time_ultra = time.time()
        if not self.f_config == None:
            self.f_config.write("HISTOGRAM_OPEN\t%15.15f\n"%(self.begin_time_ultra))     
        while not self.stop_measure:
            try:
                # update values
                resistance = abs(self.data["agilent_voltage_voltage"][-1] / self.data["agilent_current_voltage"][-1] * self.rref)
                try:
                    _time = time.time()
                    x_list = np.arange(_time-5,_time,0.25)
                    current = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                    voltage = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                    r_array = voltage/current*self.rref
                
                    d_res = np.polyfit(x_list, r_array, 1)
                    
                    self.ui.label_138.setText("R_1(t)=%ft"%(d_res[0]))
                except Exception,e:
                    log("Failed to derivate Resistance",e)
                    
                lower_res = float(self.form_data["editHistogramLower"])
                upper_res = float(self.form_data["editHistogramUpper"])
                #print "upper_res"

                if last_engage > float(self.form_data["editUltraColdTime"]):
                    if resistance < float(self.form_data["editUltraMax"]) and resistance > float(self.form_data["editUltraMin"]):
                        log("Found desired Resistance for Action")
                        log("Stopping Motor")
                        last_engage = 0
                        
                        # wait to stabilize
                        DEV.motor.stop()
                        time.sleep(float(self.form_data["editUltraStabilizeTime"]))
                        resistance_new = abs(self.data["agilent_voltage_voltage"][-1] / self.data["agilent_current_voltage"][-1] * self.rref)
                        
                        log("Resistance changed by %f"%(resistance_new*100/resistance-100))

                        if abs(resistance_new / resistance - 1) < 0.1:
                            sample_factor = resistance_new/(resistance_new+self.rref)
                            if int(self.form_data["comboUltraAction"]) == 0:
                                # ivs
                                log("Starting IVs")
                                is_double = bool(self.form_data["checkUltraIVDouble"])
                                is_sample = bool(self.form_data["checkUltraIVSample"])
                                is_mar = bool(self.form_data["checkUltraMAR"])
                                v_mar = float(self.form_data["editUltraIVMARV"])/1000.0
                                t_mar = float(self.form_data["editUltraIVMARt"])
                                li_mar = abs(float(self.form_data["editUltraIVMARLI"]))/100.0
                                v_iets = float(self.form_data["editUltraIVIETSV"])
                                t_iets = float(self.form_data["editUltraIVIETSt"])
                                li_iets = abs(float(self.form_data["editUltraIVIETSLI"]))/100.0
                                
                                if is_mar: # mar sweep if checked                                    
                                    # set lockin (switch on/off)
                                    output_enabled = True
                                    if li_mar < 1e-5:
                                        log("LI MAR disabled!")
                                        output_enabled = False 
                                    if is_sample:
                                        li_mar = li_mar / sample_factor
                                    if li_mar > 1:
                                        log("LI MAR too high! Reduced!")
                                        li_mar = 1
                                    DEV.lockin.set_amplitude(li_mar, output=output_enabled)
                                    self.aquire_iv(_min=-v_mar, _max=v_mar, _time=t_mar, _sample=is_sample, _double=is_double)
                                                                  
                                # set lockin (switch on/off)
                                output_enabled = True
                                if li_iets < 1e-5:
                                    log("LI IETS disabled!")
                                    output_enabled = False
                                
                                if is_sample:
                                    li_iets = li_iets / sample_factor
                                if li_iets > 1:
                                        log("LI IETS too high! Reduced!")
                                        li_iets = 1
                                DEV.lockin.set_amplitude(li_iets, output=output_enabled)
                                self.aquire_iv(_min=-v_iets, _max=v_iets, _time=t_iets, _sample=is_sample, _double=is_double)
                                
                            if self.form_data["comboUltraAction"] == 1:
                                # bsweep
                                log("Starting B Sweep")
                                _max = float(self.form_data["editUltraBSweepMax"])
                                _rate = float(self.form_data["editUltraBSweepRate"])
                                _ips = int(self.form_data["comboUltraBSweepAxes"])
                                self.aquire_b_sweep(_max,_rate,_ips)
                                #self.stop_measure = False
                                
                            if self.form_data["comboUltraAction"] == 2:
                                # stretching
                                log("Starting Stretching")
                                
                            if self.form_data["comboUltraAction"] == 3:
                                # exit
                                log("Start Exiting")
                                self.stop_measure = True
                                break
                        
                            if self.stop_measure:
                                break
                            
                            if breaking:
                                self.config_data["sub_index"] += 1
                            else:
                                self.config_data["sub_index"] -= 1
                        else:
                            log("Resuming Ultra")
                     
          
                last_engage = last_engage + ultra_sleep # increase variable only when not in action
                bias = float(self.form_data["editHistogramBias"])
                if not self.offset_in_progress:
                    DEV.yoko.set_voltage(bias)
                # if conductance hits upper limit, close again
                if resistance > upper_res:            
                    if breaking == True: 
                        self.begin_time_ultra = time.time()
                        if not self.f_config == None:
                            self.f_config.write("HISTOGRAM_CLOSE\t%15.15f\n"%(self.begin_time_ultra))
                        self.config_data["main_index"] += 1
                        self.config_data["sub_index"] = 0
                    breaking = False
                    
                    
                # at lower limit, break again, in between: set speed
                if resistance < lower_res:
                    if breaking == False: 
                        self.begin_time_ultra = time.time()
                        if not self.f_config == None:
                            self.f_config.write("HISTOGRAM_OPEN\t%15.15f\n"%(self.begin_time_ultra)) 
                        self.config_data["main_index"] += 1
                        self.config_data["sub_index"] = 0
                    breaking = True
                    

                if breaking:
                    gui_helper.motor_break(int(self.form_data["editHistogramOpeningSpeed"]), quiet=True)
                else:
                    gui_helper.motor_unbreak(int(self.form_data["editHistogramClosingSpeed"]), quiet=True)
                    
                # if escape on motor limit hit
                if bool(self.form_data["checkHistogramEscape"]):
                    if DEV.motor.higher_bound or DEV.motor.lower_bound:
                        log("Motor reached its bounds, escaping histogram!")
                        break
                else:
                    if DEV.motor.higher_bound:
                        log("Motor reached its bounds, trying to break again in 10s!")
                        time.sleep(10)
                        breaking = True
                    if DEV.motor.lower_bound:
                        log("Motor reached its bounds, trying to close again in 10s!")
                        time.sleep(10)
                        breaking = False
                time.sleep(ultra_sleep)
            except Exception,e:
                log("Ultra Inner Failure",e)
                DEV.motor.stop()
                break
        DEV.motor.stop()
        self.histogram_in_progress = False
        log("Ultra Stop")


    
    def aquire_iv(self, _min=None, _max=None, _time=None, _sample=None, _double=None, _resync_lockin=True):
        """(self, _min=None, _max=None, _time=None, _sample=None, _double=None)"""
        log("IV Sweep Starting") 
        self.stop_measure = False
        self.iv_in_progress = True
        
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.X_BOTTOM, "V (V)")
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.Y_LEFT, "I (A)") 
        
        if _resync_lockin:
            DEV.lockin.resync()
        
        try:
            sample_res = abs(self.data["agilent_voltage_voltage"][-1] / self.data["agilent_current_voltage"][-1] * self.rref)
            sample_factor = sample_res/(sample_res+self.rref)
        except Exception,e:
            sample_factor = 1000.0
            log("IV voltage calculation failed",e)
        
        if _sample:
            _min = _min / sample_factor
            _max = _max / sample_factor

        # range maximum protection
        _voltage_limits = 5.0
        _min = max(-_voltage_limits, min(_min, _voltage_limits))
        _max = max(-_voltage_limits, min(_max, _voltage_limits))
                
        bias = DEV.yoko.get_voltage()
        DEV.yoko.program_goto_ramp(_min, 1)
        time.sleep(1)
        time.sleep(5 * float(self.form_data["editLITC"]))       
        
                
        
        log("IV Loop %fV,%fV,%4.0fs"%(_min,_max,_time)) 
        # load counter
        loop_count = 2
        # last_time is used for display updating 
        self.begin_time_iv = time.time()
        last_time = time.time() 
        start_sweep_yoko = True
        while loop_count > 0.1:
            if start_sweep_yoko:
                # note down begin of sweep
                self.begin_time_iv = time.time()
                               
                param_string = self.return_param_string()
                initialize.write_config("IV_START\t%15.15f\t%s\n"%(self.begin_time_iv,param_string))

                start_sweep_yoko = False
                if loop_count % 2: # if not even = odd (2nd/4th run in double)
                    DEV.yoko.program_goto_ramp(_min, _time)
                    log("IV goto Min")
                else: # if even run (first run)
                    DEV.yoko.program_goto_ramp(_max, _time) 
                    log("IV goto Max")

            if time.time() - last_time > 1: # check if update needed
                last_time = time.time()

                try:
                    self.data_lock.acquire()
                    x_list = np.arange(self.begin_time_iv,last_time,0.1)
                    
                    try:
                        voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                        current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                        li_0_x_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_x"])
                        li_0_y_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_y"])
                        li_1_x_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_x"])
                        li_1_y_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_y"])
                        li_3_x_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_x"])
                        li_3_y_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_y"])
                        li_4_x_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_x"])
                        li_4_y_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_y"])
         
                         #dG:np.sqrt(np.power([li_3_x],2)+np.power([li_3_y],2))/np.sqrt(np.power([li_0_x],2)+np.power([li_0_y],2))/104000.0*12900.0

                        li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
                        li_1_r = np.sqrt(np.square(li_1_x_interp)+np.square(li_1_y_interp))
                        li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
                        li_4_r = np.sqrt(np.square(li_4_x_interp)+np.square(li_4_y_interp))
                        
                        li_first = li_3_r/li_0_r*12900    # first
                        #li_second = li_4_r/li_1_r*12900   # trash
                        li_second = li_4_r   # second
                                            
                        self.plot_data["x3"] = voltage_list[:]
                        self.plot_data["y3"] = [x/self.rref for x in li_first[:]]
                        
                        self.plot_data["x4"] = voltage_list[:]
                        self.plot_data["y4"] = [x/self.rref for x in li_second[:]]
                        
                        self.plot_data["new"][2] = True
                        self.plot_data["new"][3] = True
                    except Exception,e:
                        log("IV interpolation failed",e)
            
                    self.plot_data["x1"] = voltage_list[:]
                    self.plot_data["y1"] = [x/self.rref for x in current_list[:]]
                    self.plot_data["new"][0] = True 
                    
                finally:
                    self.data_lock.release()
            
            time.sleep(0.1)
            app.processEvents()
            
            if self.stop_measure: # check for stop condition
                DEV.yoko.program_hold()
                loop_count = 0
                break
            
            if DEV.yoko.program_is_end():
                start_sweep_yoko = True
                if _double: # if double, only subtract one (odd/even), triangular sweep
                    loop_count -= 1
                else: # if not double, sawtooth sweep
                    loop_count -= 2 
                
                # note down end of iv sweep
                end_time = time.time()
                initialize.write_config("IV_STOP\t%15.15f\t\n"%(end_time))
                # save file
                try:
                    self.data_lock.acquire()
                    
                    x_list = np.arange(self.begin_time_iv,end_time,0.1)
         
                    # lockin data refurbishment
                    voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                    current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                    li_0_x_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_x"])
                    li_0_y_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_y"])
                    li_1_x_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_x"])
                    li_1_y_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_y"])
                    li_3_x_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_x"])
                    li_3_y_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_y"])
                    li_4_x_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_x"])
                    li_4_y_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_y"])
                    
                    li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
                    li_1_r = np.sqrt(np.square(li_1_x_interp)+np.square(li_1_y_interp))
                    li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
                    li_4_r = np.sqrt(np.square(li_4_x_interp)+np.square(li_4_y_interp))
                    li_first = li_3_r/li_0_r*12900    # first
                    li_second = li_4_r/li_1_r*12900   # second
                    
                    self.plot_data["x1"] = voltage_list[:]
                    self.plot_data["y1"] = [x/self.rref for x in current_list[:]]
                    
                    self.plot_data["x3"] = voltage_list[:]
                    self.plot_data["y3"] = [x/self.rref for x in li_first[:]]
                    
                    self.plot_data["x4"] = voltage_list[:]
                    self.plot_data["y4"] = [x/self.rref for x in li_second[:]]
                    
                    # refresh plots and save them
                    self.plot_data["new"][0] = True
                    self.plot_data["new"][2] = True
                    self.plot_data["new"][3] = True
                    
                    try:        
                        saving_data = [x_list, voltage_list, current_list, li_0_x_interp, li_0_y_interp, li_1_x_interp, li_1_y_interp, li_3_x_interp, li_3_y_interp, li_4_x_interp, li_4_y_interp]
                        d = str(self.form_data["editSetupDir"])+str(self.form_data["editHeader"])+"\\"    
                        d_name = os.path.dirname(d)
                        if not os.path.exists(d_name):
                            os.makedirs(d_name)
                        time_string = str(int(round(time.time())))
                        file_string = "iv_%s_%i_%i.txt"%(time_string,self.config_data["main_index"],self.config_data["sub_index"])
                        f_iv = open(d+file_string, 'a')
        
                        try:
                            param_string = self.return_param_string()
                            f_iv.write("%s\n"%(param_string))
                            f_iv.write("timestamp, voltage, current, li_0_x, li_0_y, li_1_x, li_1_y, li_3_x, li_3_y, li_4_x, li_4_y\n")
                        except Exception,e:
                            log("IV Parameter Save failed",e)
                        save_data(f_iv, saving_data)
                        f_iv.close()
                        self.ui.editLastIV.setText(file_string)
                        
                        self.last_iv_name = time_string
                    except Exception,e:
                        log("Failed to Save IV",e)
                    
                    self.plot_data["save"] = True
                except Exception,e:
                    log("IV Calculation Failed",e)
                finally:
                    self.data_lock.release()
                    
        log("IV Loop End") 
        
        
                
        time.sleep(0.25)      
        DEV.yoko.program_goto_ramp(bias, 1)
        time.sleep(2)
        log("IV Sweep finished")
        self.iv_in_progress = False


    
    def temp_sweep(self):       
        start = float(self.form_data["editTempSweepStart"])
        end = float(self.form_data["editTempSweepStop"])
        steps = abs(float(self.form_data["editTempSweepStep"]))
        delay = float(self.form_data["editTempSweepDelay"])
        log("Temperature Sweep %f K to %f K, %f mK steps, %f s delay"%(start,end,steps*1000,delay))
        
        step_list = []
        
        if start > end: # rotate if inverse
            steps = -steps

        self.temp_sweep_abort = False

        value = start
        # while distance to end is smaller than 10%
        while True:   
            step_list.append(round(value,5))
            # if next step issnt fitting to range
            if abs(value-end) < abs(steps):  
                if abs(value-end) > abs(steps*0.2):
                    step_list.append(end)
                break
            
            value = value+steps
          
        if not self.f_config == None:
            self.f_config.write("TEMPERATURE_START\t%15.15f\t\n"%(time.time()))
        for _temperature in step_list:
                DEV.lakeshore.set_setpoint(_temperature)
                _i = delay
                while _i > 0:
                    if self.temp_sweep_abort:
                        break
                    app.processEvents()
                    time.sleep(0.05)
                    _i -= 0.05
                    
                if self.temp_sweep_abort:
                        break
                    
        if not self.f_config == None:
            self.f_config.write("TEMPERATURE_STOP\t%15.15f\t\n"%(time.time()))
        log("Temperature Sweep finished")
        
    
    def aquire_b_circle(self, _radius, _stepsize, _start, _stop):
        self.stop_measure = False
        
        rate_1 = float(self.form_data["editBRate"])
        rate_2 = float(self.form_data["editBRate_2"])
        
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.X_BOTTOM, "Bz (T)")
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.Y_LEFT, "Bx (T)") 
        self.ui.cw6.plot.set_axis_title(self.ui.cw5.plot.X_BOTTOM, "Angle (Deg))")
        self.ui.cw6.plot.set_axis_title(self.ui.cw5.plot.Y_LEFT, "G (Go)") 

        angles = np.arange(_start,_stop,_stepsize)
        angle_index = 0

        self.begin_time_b_circle = time.time()
        if not self.f_config == None:
            self.f_config.write("BCIRCLE_START\t%15.15f\n"%(self.begin_time_b_circle))
        log("B Circle %f"%(self.begin_time_b_circle))
        last_time = time.time()      
        while not self.stop_measure:
            if time.time() - last_time > 1: # check if update needed
                last_time = time.time()

                try:
                    self.data_lock.acquire()
                    
                    x_list = np.arange(self.begin_time_b_circle,last_time,0.25)
 
                    voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                    current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                    li_0_x_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_x"])
                    li_0_y_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_y"])
                    li_3_x_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_x"])
                    li_3_y_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_y"])
                    b_1 = interpolate(x_list, self.data["ips_timestamp"], self.data["ips_mfield"])
                    b_2 = interpolate(x_list, self.data["ips_2_timestamp"], self.data["ips_2_mfield"])
                    
                    li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
                    li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
                    
                    li_first = li_3_r/li_0_r*12900    # first
                    
                    np.seterr(divide="ignore")
                    
                    # trying to get full circle
                    try:
                        self.plot_data["x1"] = b_1[:]
                        self.plot_data["y1"] = b_2[:]
                        
                        self.plot_data["x3"] = np.rad2deg(np.arctan(b_1/b_2))
                        self.plot_data["y3"] = [x/self.rref for x in li_first[:]]
                        self.plot_data["x4"] = np.arctan(b_1/b_2)
                        self.plot_data["y4"] = current_list/voltage_list/self.rref
                        for i in range(len(b_2)):
                            if b_2[i] < 0:
                                self.plot_data["x3"][i] += 180.0
                                self.plot_data["x4"][i] += 180.0
                        self.plot_data["new"][0] = True 
                        self.plot_data["new"][2] = True
                        self.plot_data["new"][3] = True
                        
                        DEV.yoko.display_set_text("%2.2fT %2.2fT %i"%(b_1[-1],b_2[-1],self.plot_data["x3"][-1]))
                    except Exception,e:
                        log("Angle Constructing Plot Failed",e)
                    
                except Exception,e:
                        log("IV interpolation failed",e)
                finally:
                    self.data_lock.release()
                    np.seterr(divide="print")
                    
            if DEV.magnet.field_reached() and DEV.magnet_2.field_reached():
                # do whatever
                
                angle = angles[angle_index]
                b_1 = np.cos(np.deg2rad(angle))*_radius
                b_2 = np.sin(np.deg2rad(angle))*_radius 
                
                DEV.magnet.SetField(b_1, rate_1, verbal=False)
                DEV.magnet_2.SetField(b_2, rate_2, verbal=False)
                
                if angle_index >= len(angles)-1:
                    log("Angles done!")
                    self.stop_measure = True
                angle_index += 1
                
                if self.stop_measure: # check for stop condition
                    break
            time.sleep(0.1)
        if not self.f_config == None:
            self.f_config.write("BCIRCLE_STOP\t%15.15f\n"%(time.time()))
            
        DEV.yoko.display_main_screen()
        log("Waiting for Magnets set to Zero")
        DEV.magnet.ZeroField(rate_1)
        DEV.magnet_2.ZeroField(rate_2)

        if self.form_data["checkBSweepHeater"]:
            log("Requested to Switch of Heaters")
            log("Waiting for Magnets to run down")
            self.stop_measure = False
            while not self.stop_measure:
                if DEV.magnet.field_reached() and DEV.magnet_2.field_reached():
                    self.stop_measure = True
                time.sleep(0.25)
            
            log("Magnets at Zero Field")
            try:
                if DEV.magnet.field_reached():
                    DEV.magnet.set_switchheater("zeroOFF")
                    log("IPS1 Heater Off")
                else:
                    log("Magnet Sweeping. Couldn't Turn off Heater!",e)
            except Exception,e:
                log("Failed Auto-Off Heater IPS1",e)
            try:
                if DEV.magnet_2.field_reached():
                    DEV.magnet_2.set_switchheater("zeroOFF")
                    log("IPS2 Heater Off")
                else:
                    log("Magnet 2 Sweeping. Couldn't Turn off Heater!",e)
            except Exception,e:
                log("Failed Auto-Off Heater IPS2",e)
        
        
        

   
    def aquire_b_sweep(self, _max=None, _rate=None, _axes=None):  
        """aquire sweep to b field and perhaps back
        take care of _max and _rate!
        _axes should be 0 or 1; 0=zSweep, 1=xSweep"""
        self.stop_measure = False
        _axes += 1              
        log("B Sweep Started")
        fields = [_max,-_max,_max,0]
        field_index = 0
        print fields
        
        try:
            # if automatic switch heater mode is checked
            if self.form_data["checkBAutoSwitchHeater"]:
                if _axes == 1:
                    if not DEV.magnet == None:
                        if DEV.magnet.heater == False:
                            log("IPS1 Heater was OFF, Switching ON")
                            DEV.magnet.set_switchheater("ON")
                            for i in range(20):
                                time.sleep(1)
                                app.processEvents()
                if _axes == 2:
                    if not DEV.magnet_2 == None:
                        if DEV.magnet_2.heater == False:
                            log("IPS2 Heater was OFF, Switching ON")
                            DEV.magnet_2.set_switchheater("ON")
                            for i in range(20):
                                time.sleep(1)
                                app.processEvents()
            
            # if check for switch heater is checked
            if self.form_data["checkBSwitchHeater"]:
                if _axes == 1:
                    if not DEV.magnet == None:
                        if DEV.magnet.heater == False:
                            log("IPS1 Heater is OFF. Exiting.")
                            self.stop_measure = True
                            return -1  
                if _axes == 2:
                    if not DEV.magnet_2 == None:
                        if DEV.magnet_2.heater == False:
                            log("IPS2 Heater is OFF. Exiting.")
                            self.stop_measure = True
                            return -1            
        except Exception,e:
            log("Auto Set Switchheater Failed. Exiting.",e)
            self.stop_measure = True
            return -1
        
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.X_BOTTOM, "B (T)")
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.Y_LEFT, "Resistance (Ohm)") 
        self.begin_time_b2 = time.time()
        last_time = time.time() 
        while not self.stop_measure:
            if _axes == 1:
                if DEV.magnet.field_reached():
                    if field_index >= len(fields):
                        log("Fields done!")
                        self.stop_measure = True
                    else:
                        time.sleep(5)
                        DEV.magnet.SetField(fields[field_index], _rate) 
                        print "IPS set to %f T"%(fields[field_index])
                        field_index += 1
                try:
                    DEV.yoko.display_set_text("%f mV\n%2.1f mT"
                        %(round(DEV.yoko.get_voltage()*1e3),
                          round(self.data["ips_mfield"][-1]*1e3))
                          )
                except Exception,e:
                    log("Failed to Update Yoko Display",e)
                
            if _axes == 2:
                if DEV.magnet_2.field_reached():
                    if field_index >= len(fields):
                        log("Fields done!")
                        self.stop_measure = True
                    else:    
                        time.sleep(5)
                        DEV.magnet_2.SetField(fields[field_index], _rate) 
                        print "IPS set to %f T"%(fields[field_index])
                        field_index += 1
                      
            # replotting data if one second elapsed
            if time.time() - last_time > 1: # check if update needed
                    last_time = time.time()
    
                    try:
                        self.data_lock.acquire()
                        x_list = np.arange(self.begin_time_b2,last_time,0.1)

                        voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                        current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                        
                        if _axes == 1:
                            b = interpolate(x_list, self.data["ips_timestamp"], self.data["ips_mfield"])
                        if _axes == 2:
                            b = interpolate(x_list, self.data["ips_2_timestamp"], self.data["ips_2_mfield"])
 
                        self.plot_data["x1"] = b
                        self.plot_data["y1"] = voltage_list/current_list*self.rref
                        self.plot_data["new"][0] = True
                    except Exception,e:
                        log("B Sweep interpolation failed",e)       
                    finally:
                        self.data_lock.release()
                        
            if self.stop_measure: # check for stop condition
                break
            time.sleep(0.5)
        end_time = time.time()    
        
        # Switch Heater shut down
        if self.form_data["checkBSweepHeater"]:
            try:
                if DEV.magnet.field_reached():
                    DEV.magnet.set_switchheater("zeroOFF")
                else:
                    log("Magnet Sweeping. Couldn't Turn off Heater!",e)
            except Exception,e:
                log("Failed Auto-Off Heater IPS1",e)
            try:
                if DEV.magnet_2.field_reached():
                    DEV.magnet_2.set_switchheater("zeroOFF")
                else:
                    log("Magnet 2 Sweeping. Couldn't Turn off Heater!",e)
            except Exception,e:
                log("Failed Auto-Off Heater IPS2",e)
        
        # interpolating and saving of the data                
        try:
            self.data_lock.acquire()
            
            x_list = np.arange(self.begin_time_b2,end_time,0.1)
            voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
            current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
            if _axes == 1:
                b = interpolate(x_list, self.data["ips_timestamp"], self.data["ips_mfield"])
            if _axes == 2:
                b = interpolate(x_list, self.data["ips_2_timestamp"], self.data["ips_2_mfield"])
    
            self.plot_data["x1"] = b
            self.plot_data["y1"] = voltage_list/current_list*self.rref
            self.plot_data["new"][0] = True
      
            saving_data = [x_list, voltage_list, current_list, b]
            d = str(self.ui.editSetupDir.text())+str(self.ui.editHeader.text())+"\\"   
            d_name = os.path.dirname(d)
            if not os.path.exists(d_name):
                os.makedirs(d_name)
            time_string = str(int(round(time.time())))
            file_string = "bsweep_%s.txt"%(time_string)
            f_iv = open(d+file_string, 'a')
            try:
                param_string = self.return_param_string
                f_iv.write("%s\n"%(param_string))
                f_iv.write("timestamp, voltage, current, b\n")
            except Exception,e:
                log("B Sweep Parameter Save failed",e)
            save_data(f_iv, saving_data)
            f_iv.close()
            self.ui.editLastIV.setText(file_string)
            
            self.last_iv_name = time_string
        except Exception,e:
            log("B Sweep interpolation and Saving failed",e)     
        finally:
            self.data_lock.release()

        log("B Sweep Done")
        

    def aquire_b_iv_map(self, _minB=None, _maxB=None, _steps=None, _rate=0.2,
                        _axes=0, _minV=None, _maxV=None, _timeV=None,
                        _sample=True, _double=True, _resync_lockin=True):  
        """acquire a b-iv-map with given ranges and properties
        
        This function initializes the different devices so the can be used for 
        this sweep. The field is driven from `_minB` to `_maxB` in steps with
        the increment of `_steps`. At each value a IV sweep with the voltage
        boundaries `_minV` `_maxV` in `_timeV` seconds is performed.
        
        Parameters
        ----------
        _minB : float
            Minimum field, where the sweep begins, in Tesla.
        _maxB : float
            Maximum field, where the sweep ends, in Tesla.
        _steps : float
            The increment of the B sweep. Every `_step` T a IV sweep will be
            started. Give in T.
        _rate : float, optional
            The speed of the change of the magnetic field. Default: 0.2 T/min
        _axes : {0, 1}, optional
            Selects the axis of the magnetic field. 0 : z direction (default)
                                                    1 : x direction
        _minV : float
            Lower voltage boundary of the IV sweep
        _maxV : float
            Higher voltage boundary of the IV sweep
        _timeV : float
            Time in which the IV sweep from `_minV` to `_maxV` or 
            from `_maxV` to `_minV` is performed. Give in seconds.
        _sample : logical, optional
            This variable manipulates the applied voltage:
            True : Given voltage at the sample (default)
            False : Given voltage over all.
        _double : logical, optional
            This variable decides the shape of the IV sweep:
            True : triangular (default)
            False: saw tooth
            
        Returns
        -------
        None
        
        Other Parameters
        ----------------        
        _resync_lockin: logical, optional
            The Lock-In is resyncronized at the beginning of each invocation of
            this function, optional value is True
        
        Raises
        ------
        No Exception is thrown with this function.
        
        See Also
        --------
        aquire_iv : a single IV sweep
        aquire_b_sweep : a sweep of the magnetic field without any interruptions"""
        
        log("B-IV-map Started")
        self.stop_measure = False    
        
        """defining which labels on the axis should appear"""
        self.ui.cw5.plot.set_axis_title(self.ui.cw6.plot.X_BOTTOM, "U(V)")
        self.ui.cw5.plot.set_axis_title(self.ui.cw6.plot.Y_LEFT,"I(A)")
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.X_BOTTOM, "B (T)")
        self.ui.cw5.plot.set_axis_title(self.ui.cw5.plot.Y_LEFT, "Resistance (Ohm)")
        
        """prelocations and precalculations for iv sweeps"""
        if _resync_lockin:
            DEV.lockin.resync()
            
        try:
            sample_res = abs(self.data["agilent_voltage_voltage"][-1] / self.data["agilent_current_voltage"][-1] * self.rref)
            sample_factor = sample_res/(sample_res + self.rref)
        except Exception,e:
            sample_factor = 1000.0
            log("IV voltage calculation failed",e)
            
        if _sample:
            _minV = _minV / sample_factor
            _maxV = _maxV / sample_factor
            
       # range maximum protection
        _voltage_limits = 5.0
        _minV = max(-_voltage_limits, min(_minV, _voltage_limits))
        _maxV = max(-_voltage_limits, min(_maxV, _voltage_limits))
        
        """prelocations and allocations for b changes"""
        _axes += 1
        field = np.arange(_minB,_maxB+_steps,_steps)
        print field
        
        #switch on switch heater of the chosen magnet
        try:
            # automatic switch heater mode is checked
            if self.form_data["checkBAutoSwitchHeater"]:
                if _axes == 1:
                    if not DEV.magnet == None:
                        if DEV.magnet.heater == False:
                            log("IPS1 Heater was OFF, Switching ON")
                            DEV.magnet.set_switchheater("ON")
                            for i in range(20):
                                time.sleep(1)
                                app.processEvents()
                if _axes == 2:
                    if not DEV.magnet_2 == None:
                        if DEV.magnet_2.heater == False:
                            log("IPS2 Heater was OFF, Switching ON")
                            DEV.magnet_2.set_switchheater("ON")
                            for i in range(20):
                                time.sleep(1)
                                app.processEvents()
            
            # check if switch heater is in right state
            if self.form_data["checkBSwitchHeater"]:
                if _axes == 1:
                    if not DEV.magnet == None:
                        if DEV.magnet.heater == False:
                            log("IPS1 Heater is OFF. Exiting.")
                            self.stop_measure = True
                            return -1  
                if _axes == 2:
                    if not DEV.magnet_2 == None:
                        if DEV.magnet_2.heater == False:
                            log("IPS2 Heater is OFF. Exiting.")
                            self.stop_measure = True
                            return -1            
        except Exception,e:
            log("Auto Set Switchheater Failed. Exiting.",e)
            self.stop_measure = True
            return -1
        
        """ Start with the b-iv-map """
        self.begin_time_biv = time.time()
        for k in field:
            self.begin_time_biv_b = time.time()
            last_time = time.time()
            # set b field to target value
            if _axes == 1:
                DEV.magnet.SetField(k, _rate)
                print "IPS set to %f T"%(k)
                while not DEV.magnet.field_reached():
                    time.sleep(5)
                
            if _axes == 2:
                DEV.magnet_2.SetField(k, _rate)
                print "IPS set to %f T"%(k)

             
            #check if update is needed and displays the new data
            while not DEV.magnet_2.field_reached():
                if time.time() - last_time > 1:
                    last_time = time.time()
                    
                    try:
                        self.data_lock.acquire()
                        x_list = np.arange(self.begin_time_biv_b,last_time,0.1)
                        
                        voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                        current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                        
                        if _axes == 1:
                            b = interpolate(x_list, self.data["ips_timestamp"], self.data["ips_mfield"])
                        if _axes == 2:
                            b = interpolate(x_list, self.data["ips_2_timestamp"], self.data["ips_2_mfield"])
                        
                        self.plot_data["x2"] = b
                        self.plot_data["y2"] = voltage_list/current_list*self.rref
                        self.plot_data["new"][0] = True
                    except Exception,e:
                        log("B Sweep interpolation failed",e)       
                    finally:
                        self.data_lock.release()
                time.sleep(0.1)
                
                if self.stop_measure():
                    if _axes == 1:
                        DEV.magnet.SetField(DEV.magnet.actual_field(), _rate)
                    if _axes == 2:
                        DEV.magnet_2.SetField(DEV.magnet_2.actual_field(), _rate)
                    break
                
            # Saving b sweep from begin_time_biv_b
            end_time_biv_b
            try:
                self.data_lock.acquire()
                x_list = np.arange(self.begin_time_biv_b,end_time_biv_b,0.1)
                voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                if _axes == 1:
                    b = interpolate(x_list, self.data["ips_timestamp"], self.data["ips_mfield"])
                elif _axes == 2:
                    b = interpolate(x_list, self.data["ips_2_timestamp"], self.data["ips_2_mfield"])
                
                self.plot_data["x2"] = b
                self.plot_data["y2"] = voltage_list/current_list * self.rref
                self.plot_data["new"][0] = True
                
                saving_data = [x_list, voltage_list, current_list, b]
                d = str(self.ui.editSetupDir.text())+str(self.ui.editHeader.text())+"\\"
                d_name = os.path.dirname(d)
                if not os.path.exists(d_name):
                    os.makedirs(d_name)
                time_string = str(int(round(time.time())))
                file_string = "bsweep_%s.txt"%(time_string)
                f_b = open(d+file_string, 'a')
                try:
                    param_string = self.return_param_string
                    f_b.write("%s\n"%(param_string))
                    f_b.write("timestamp, voltage, current, b\n")
                except Exception,e:
                    log("B Sweep Parameter Save failed",e)
                save_data(f_b, saving_data)
                f_b.close()
                self.ui.editLastIV.setText(file_string)
                slef.last_iv_name = time_string
            except Exception,e:
                log("B Sweep interpolation and saving failed",e)
            finally:
                self.data_lock.release()
            
            time.sleep(0.1)
            app.processEvents()
            log("B = %1.4f reached"%(k))
            
                
            # performing a iv sweep
            bias = DEV.yoko.get_voltage() #bias to make postmeasuring allocations
            DEV.yoko.program_goto_ramp(_minV,1)
            time.sleep(1)
            time.sleep(5 * float(self.form_data["editLITC"]))
            
            log("IV loop %f V,%f V, %4.0f s"%(_minV,_maxV,_timeV))
            loop_count = 2
            last_time = time.time()
            start_sweep_yoko = True
            while loop_count>0.1:
                if start_sweep_yoko:
                    self.begin_time_biv_iv = time.time()
                    
                    param_string = self.return_param_string()
                    initialize.write_config("IV START\t%15.15f\t%s\n"%(self.begin_time_iv,param_string))

                    start_sweep_yoko = False                    
                    if loop_count % 2:
                        DEV.yoko.program_goto_ramp(_minV,_timeV)
                        log("IV goto Min")
                    else:
                        DEV.yoko.program_goto_ramp(_maxV,_timeV)
                        log("IV goto Max")
                        
                    
                # check if update is needed an displays the new data
                if time.time() - last_time > 1:
                    last_time = time.time()
                    
                    try:
                        self.data_lock.acquire()
                        x_list = np.arange(self.begin_time_biv_iv,last_time,0.1)
                        
                        try:
                            voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                            current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                            li_0_x_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_x"])
                            li_0_y_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_y"])
                            li_1_x_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_x"])
                            li_1_y_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_y"])
                            li_3_x_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_x"])
                            li_3_y_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_y"])
                            li_4_x_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_x"])
                            li_4_y_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_y"])
                            
                            li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
                            li_1_r = np.sqrt(np.square(li_1_x_interp)+np.square(li_1_y_interp))
                            li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
                            li_4_r = np.sqrt(np.square(li_4_x_interp)+np.square(li_4_y_interp))
                            
                            li_first = li_3_r/li_0_r*12900
                            li_second = li_4_r/li_1_r*12900
                            
                            self.plot_data["x3"] = voltage_list[:]
                            self.plot_data["x4"] = voltage_list[:]
                            self.plot_data["y4"] = [x/self.rref for x in li_second[:]]
                    
                            self.plot_data["new"][2] = True
                            self.plot_data["new"][3] = True
                        except Exception,e:
                            log("IV interpolation failed",e)
                            
                        self.plot_data["x1"] = voltage_list[:]
                        self.plot_data["y1"] = [x/self.rref for x in current_list[:]]
                        self.plot_data["new"][0] = True
                    finally:
                        self.data_lock.release()
                        
                time.sleep(0.1)
                app.processEvents()
                    
                #check for stopping condition
                if self.stop_measure:
                    DEV.yoko.program_hold()
                    loop_count = 0
                    break
                
                if DEV.yoko.program_is_end():
                    start_sweep_yoko = True
                    if _double: #Dreiecksverlauf
                        loop_count -=1
                    else: #Sägezahn
                        loop_count -=2
                        
                end_time_biv_iv = time.time()
                initialize.write_config("IV STOP\t%15.15f\t\n"%(end_time_biv_iv))
                
                #save file of this iv-sweep
                try:
                    self.data_lock.acquire()
                    
                    x_list = np.arange(self.begin_time_biv_iv,end_time_biv_iv,0.1)
                    
                    # lockin data refurbishment
                    voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
                    current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
                    li_0_x_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_x"])
                    li_0_y_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_y"])
                    li_1_x_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_x"])
                    li_1_y_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_y"])
                    li_3_x_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_x"])
                    li_3_y_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_y"])
                    li_4_x_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_x"])
                    li_4_y_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_y"])
                
                    li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
                    li_1_r = np.sqrt(np.square(li_1_x_interp)+np.square(li_1_y_interp))
                    li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
                    li_4_r = np.sqrt(np.square(li_4_x_interp)+np.square(li_4_y_interp))
                    li_first = li_3_r/li_0_r*12900    # first derivative (dI/dV)
                    li_second = li_4_r/li_1_r*12900   # second derivative (d^2I/dV^2)
                
                    self.plot_data["x1"] = voltage_list[:]
                    self.plot_data["y1"] = [x/self.rref for x in current_list[:]]
                    
                    self.plot_data["x3"] = voltage_list[:]
                    self.plot_data["y3"] = [x/self.rref for x in li_first[:]]
                        
                    self.plot_data["x4"] = voltage_list[:]
                    self.plot_data["y4"] = [x/self.rref for x in li_second[:]]
                    
                    # refresh plots and save them
                    self.plot_data["new"][0] = True
                    self.plot_data["new"][2] = True
                    self.plot_data["new"][3] = True
                        
                    try:
                        saving_data = [x_list, voltage_list, current_list, li_0_x_interp, li_0_y_interp, li_1_x_interp, li_1_y_interp, li_3_x_interp, li_3_y_interp, li_4_x_interp, li_4_y_interp]
                        d = str(self.ui.editSetupDir.text())+str(self.ui.editHeader.text())+"\\"    
                        d_name = os.path.dirname(d)
                        if not os.path.exists(d_name):
                            os.makedirs(d_name)
                        time_string = str(int(round(time.time())))
                        file_string = "iv_%1.4f_%s_%i_%i.txt"%(k,time_string,self.config_data["main_index"],self.config_data["sub_index"])
                        f_iv = open(d+file_string,'a')
                            
                        try:
                            param_string = self.return_param_string()
                            f_iv.write("%s\n"%(param_string))
                            f_iv.write("timestamp, voltage, current, li_0_x, li_0_y, li_1_x, li_1_y, li_3_x, li_3_y, li_4_x, li_4_y\n")
                        except Exception,e:
                            log("IV Parameter Save failed",e)
                        save_data(f_iv, saving_data)
                        f_iv.close()
                        self.ui.editLastIV.setText(file_string)
                    except Exception,e:
                        log("Failed to Save IV",e)
                            
                    self.plot_data["save"] = True
                except Exception,e:
                    log("IV Calculation Failed",e)
                finally:
                    self.data_lock.release()
            
            log("IV Loop End")
            time.sleep(0.5)
            DEV.yoko.program_goto_ramp(bias, 1)
            time.sleep(2)
            log("IV Sweep finished")
            
            if self.stop_measure():
                break
            time.sleep(0.5)
            end_time = time.time()
            
        """post measuring things"""
        # Switch Heater shut down
        if self.form_data["checkBSweepHeater"]:
            try:
                if DEV.magnet.field_reached():
                    DEV.magnet.set_switchheater("zeroOFF")
                else:
                    log("Magnet Sweeping. Couldn't Turn off Heater!",e)
            except Exception,e:
                log("Failed Auto-Off Heater IPS1",e)
            try:
                if DEV.magnet_2.field_reached():
                    DEV.magnet_2.set_switchheater("zeroOFF")
                else:
                    log("Magnet 2 Sweeping. Couldn't Turn off Heater!",e)
            except Exception,e:
                log("Failed Auto-Off Heater IPS2",e)
        
        # interpolating and saving of the data        
        try:
            self.data_lock.acquire()
            
            x_list = np.arange(self.begin_time_biv,end_time,0.1)
            voltage_list = interpolate(x_list, self.data["agilent_voltage_timestamp"], self.data["agilent_voltage_voltage"])
            current_list = interpolate(x_list, self.data["agilent_current_timestamp"], self.data["agilent_current_voltage"])
            li_0_x_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_x"])
            li_0_y_interp = interpolate(x_list, self.data["li_timestamp_0"], self.data["li_0_y"])
            li_1_x_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_x"])
            li_1_y_interp = interpolate(x_list, self.data["li_timestamp_1"], self.data["li_1_y"])
            li_3_x_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_x"])
            li_3_y_interp = interpolate(x_list, self.data["li_timestamp_3"], self.data["li_3_y"])
            li_4_x_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_x"])
            li_4_y_interp = interpolate(x_list, self.data["li_timestamp_4"], self.data["li_4_y"])
                
            if _axes == 1:
                b = interpolate(x_list, self.data["ips_timestamp"], self.data["ips_mfield"])
            if _axes == 2:
                b = interpolate(x_list, self.data["ips_2_timestamp"], self.data["ips_2_mfield"])
      
            saving_data = [x_list, voltage_list, current_list, li_0_x_interp, li_0_y_interp, li_1_x_interp, li_1_y_interp, li_3_x_interp, li_3_y_interp, li_4_x_interp, li_4_y_interp, b]
            d = str(self.ui.editSetupDir.text())+str(self.ui.editHeader.text())+"\\"    
            d_name = os.path.dirname(d)
            if not os.path.exists(d_name): #Überprüfen ob Ordner existiert, sonst erstellen
                os.makedirs(d_name)
            time_string = str(int(round(time.time())))
            file_string = "bivmap_%s.txt"%(time_string)
            f_iv = open(d+file_string, 'a')
            try:
                param_string = self.return_param_string
                f_iv.write("%s\n"%(param_string))
                f_iv.write("timestamp, voltage, current, li_0_x, li_0_y, li_1_x, li_1_y, li_3_x, li_3_y, li_4_x, li_4_y, b\n")
            except Exception,e:
                log("B IV Map Parameter Save failed",e)
            save_data(f_iv, saving_data)
            f_iv.close()
            self.ui.editLastIV.setText(file_string)
            
            self.last_iv_name = time_string
        except Exception,e:
            log("B IV Map interpolation and Saving failed",e)     
        finally:
            self.data_lock.release()

        log("B-IV-Map Done")



    def measurement_thread(self):
        """This thread is gathering data all time.
        
        This thread initialize the readout of the data from the single 
        devices and write it into a variable called self.data["measured_variable"].
        Additionally the data is written into the single files and the hdf5 file.
        
        For more information look down to the single try where the data is read."""

        while not self.shutdown:
            try:
                self.data_lock.acquire()
                # Readout of the Lock-In amplifier.
                # The data of all channels is corrected with the amplification 
                # factor `factor_voltage` of `factor_current`. The two auxillary
                # channels are additionally corrected with the offset of the
                # agilents.
                
                if not self.offset_in_progress:
                    li_timestamp_0 = []
                    li_aux0 = []
                    li_aux1 = []
                    li_0_x =  []
                    li_0_y =  []
                    li_timestamp_1 = []
                    li_1_x =  []
                    li_1_y =  []
                    li_timestamp_3 = []
                    li_3_x =  []
                    li_3_y =  []
                    li_timestamp_4 = []
                    li_4_x =  []
                    li_4_y =  []
                    femto_timestamp = []
                    femto_channela = []
                    femto_channelb = []
                    
                    try:
                        if DEV.lockin != None:
                            lockin_data = DEV.lockin.get_data_list(averages=1)
                            
                            li_timestamp_0 = lockin_data["0"]["timestamp"][:]
                            li_aux0 =  [(x - self.config_data["offset_voltage"])/self.factor_voltage for x in lockin_data["0"]["auxin0"]]
                            li_aux1 =  [(x - self.config_data["offset_current"])/self.factor_current for x in lockin_data["0"]["auxin1"]]
                            li_0_x =  [x / self.factor_voltage for x in lockin_data["0"]["x"]]
                            li_0_y =  [x / self.factor_voltage for x in lockin_data["0"]["y"]]
                            li_timestamp_1 = lockin_data["1"]["timestamp"][:]
                            li_1_x =  [x / self.factor_voltage for x in lockin_data["1"]["x"]]
                            li_1_y =  [x / self.factor_voltage for x in lockin_data["1"]["y"]]
                            li_timestamp_3 = lockin_data["3"]["timestamp"][:]
                            li_3_x =  [x / self.factor_current for x in lockin_data["3"]["x"]]
                            li_3_y =  [x / self.factor_current for x in lockin_data["3"]["y"]]
                            li_timestamp_4 = lockin_data["4"]["timestamp"][:]
                            li_4_x =  [x / self.factor_current for x in lockin_data["4"]["x"]]
                            li_4_y =  [x / self.factor_current for x in lockin_data["4"]["y"]]
                            
                        femto_timestamp = lockin_data["femto"]["timestamp"]
                        femto_channela = lockin_data["femto"]["channela"]
                        femto_channelb = lockin_data["femto"]["channelb"]
                        
                        self.data["li_timestamp_0"].extend(li_timestamp_0)
                        self.data["li_aux0"].extend(li_aux0)
                        self.data["li_aux1"].extend(li_aux1)
                        self.data["li_0_x"].extend(li_0_x)
                        self.data["li_0_y"].extend(li_0_y)
                        
                        self.data["li_timestamp_1"].extend(li_timestamp_1)
                        self.data["li_1_x"].extend(li_1_x)
                        self.data["li_1_y"].extend(li_1_y)
                        
                        self.data["li_timestamp_3"].extend(li_timestamp_3)
                        self.data["li_3_x"].extend(li_3_x)
                        self.data["li_3_y"].extend(li_3_y)
                        
                        self.data["li_timestamp_4"].extend(li_timestamp_4)
                        self.data["li_4_x"].extend(li_4_x)
                        self.data["li_4_y"].extend(li_4_y) 
                        
                        self.data["femto_timestamp"].extend(femto_timestamp)
                        self.data["femto_channela"].extend(femto_channela)
                        self.data["femto_channelb"].extend(femto_channelb)
                        
                        if config.save_good_old_txt:
                            saving_data = [li_timestamp_0,li_aux0,li_aux1,li_0_x,li_0_y]
                            save_data(self.f_li0, saving_data)
                            saving_data = [li_timestamp_1,li_1_x,li_1_y]
                            save_data(self.f_li1, saving_data)
                            saving_data = [li_timestamp_3,li_3_x,li_3_y]
                            save_data(self.f_li3, saving_data)
                            saving_data = [li_timestamp_4,li_4_x,li_4_y]
                            save_data(self.f_li4, saving_data)
                        
                        if not self.hdf5_file == None:
                            try:
                                self.hdf5_file.save_lockin(0,li_timestamp_0,li_0_x,li_0_y)
                                self.hdf5_file.save_lockin(1,li_timestamp_1,li_1_x,li_1_y)
                                self.hdf5_file.save_lockin(3,li_timestamp_3,li_3_x,li_3_y)
                                self.hdf5_file.save_lockin(4,li_timestamp_4,li_4_x,li_4_y)
                            except Exception,e:
                                log("Failed to Save LockIn HDF5",e)
                        
                    except Exception,e:
                        log("LockIn failed DAQ",e)
                        
                    
                # The first Agilent which is connected to the voltage of the
                # sample is read out. The voltage is corrected by the amplification
                # factor and the offset of the Agilent.                    
                if not self.offset_in_progress:
                    agilent_voltage_timestamp = []
                    agilent_voltage_voltage = []
                    try:
                        if DEV.agilent_new != None:
                            agilent_new_data = DEV.agilent_new.get_data_list()   
                            agilent_voltage_timestamp = agilent_new_data["timestamp"]#_self.config_data["range_voltage"]
                            agilent_voltage_voltage =  [(x - self.config_data["offset_voltage"])/(10**self.config_data["range_voltage"]) for x in agilent_new_data["voltage"]] 

                        self.data["agilent_voltage_timestamp"].extend(agilent_voltage_timestamp)
                        self.data["agilent_voltage_voltage"].extend(agilent_voltage_voltage)
                        if config.save_good_old_txt:
                            saving_data = [agilent_voltage_timestamp,agilent_voltage_voltage]
                            save_data(self.f_agilent_voltage, saving_data)   
                        
                        if not self.hdf5_file == None:
                            try:
                                self.hdf5_file.save_voltage(0,agilent_voltage_timestamp,agilent_voltage_voltage)
                            except Exception,e:
                                log("Failed to Save Voltage0 HDF5",e)
                    except Exception,e:
                        log("Agilent New failed DAQ",e)

                # The second Agilent which is connected to the voltage of the
                # reference resistor is read out. The voltage is corrected by
                # the amplification factor and the offset of the Agilent.
                if not self.offset_in_progress:
                    agilent_current_timestamp = []
                    agilent_current_voltage = []
                    try:
                        if DEV.agilent_old != None:
                            agilent_old_data = DEV.agilent_old.get_data_list()   
                            agilent_current_timestamp = agilent_old_data["timestamp"]
                            agilent_current_voltage =  [(x - self.config_data["offset_current"])/(10**self.config_data["range_current"]) for x in agilent_old_data["voltage"]] 
                    
                       
                        self.data["agilent_current_timestamp"].extend(agilent_current_timestamp)
                        self.data["agilent_current_voltage"].extend(agilent_current_voltage) 
                        
                        if config.save_good_old_txt:
                            saving_data = [agilent_current_timestamp,agilent_current_voltage]
                            save_data(self.f_agilent_current, saving_data)   
                        
                        if not self.hdf5_file == None:
                            try:
                                self.hdf5_file.save_voltage(1,agilent_current_timestamp,agilent_current_voltage)
                            except Exception,e:
                                log("Failed to Save Voltage1 HDF5",e)
                    except Exception,e:
                        log("Agilent old failed DAQ",e)
                    
                # The position, the current and the velocity is read out. No correction.                 
                motor_timestamp = []
                motor_pos = []
                motor_cur = []
                motor_vel = []
                try:
                    if DEV.motor != None:
                        motor_data = DEV.motor.get_data_list()   
                        motor_timestamp = motor_data["timestamp"]
                        motor_pos = motor_data["position"]
                        motor_cur = motor_data["current"]
                        motor_vel = motor_data["velocity"]
                                   
                    self.data["motor_timestamp"].extend(motor_timestamp)
                    self.data["motor_pos"].extend(motor_pos)
                    self.data["motor_cur"].extend(motor_cur)
                    self.data["motor_vel"].extend(motor_vel)                
                    
                    if config.save_good_old_txt:
                        saving_data = [motor_timestamp,motor_pos,motor_cur,motor_vel]
                        save_data(self.f_motor, saving_data)
                    
                    if not self.hdf5_file == None:
                        try:
                            self.hdf5_file.save_motor(motor_timestamp,motor_pos,motor_vel)
                        except Exception,e:
                            log("Failed to Save Motor HDF5",e)
                except Exception,e:
                    log("Motor failed DAQ",e)
                
                # The Temperatur of the sample and the 1K pot is read out
                # No corrections.                
                temp_timestamp = []
                temp1 = []
                temp2 = []
                try:
                    if DEV.lakeshore != None:
                        temp_data = DEV.lakeshore.get_data_list()
                        temp_timestamp = temp_data["timestamp"]
                        temp1 = temp_data["temperature1"]
                        temp2 = temp_data["temperature2"]

                    self.data["temp_timestamp"].extend(temp_timestamp)
                    self.data["temp1"].extend(temp1)
                    self.data["temp2"].extend(temp2)
                    
                    if config.save_good_old_txt:
                        saving_data = [temp_timestamp,temp1,temp2]
                        save_data(self.f_temp, saving_data)
                    
                    if not self.hdf5_file == None:
                        try:
                            self.hdf5_file.save_temperature(temp_timestamp,temp1,temp2)
                        except Exception,e:
                            log("Failed to Save Temperatur HDF5",e)
                except Exception,e:
                    log("Temperature failed DAQ",e)
                
                # The magnet in z-direction is read out.                
                ips_timestamp = []
                ips_mfield = []
                try:
                    if DEV.magnet != None:
                        ips_data = DEV.magnet.get_data_list()
                        ips_timestamp = ips_data["timestamp"]
                        ips_mfield = ips_data["field"]
                
                    self.data["ips_timestamp"].extend(ips_timestamp)
                    self.data["ips_mfield"].extend(ips_mfield)
                    
                    if config.save_good_old_txt:    
                        saving_data = [ips_timestamp,ips_mfield]
                        save_data(self.f_ips, saving_data)
                    
                    if not self.hdf5_file == None:
                        try:
                            self.hdf5_file.save_magnet(0,ips_timestamp,ips_mfield)
                        except Exception,e:
                            log("Failed to Save IPS1 HDF5",e)
                except Exception,e:
                    log("Magnet failed DAQ",e)
                
                # The magnet in x-direction is read out.                
                ips_2_timestamp = []
                ips_2_mfield = []
                try:
                    if DEV.magnet_2 != None:
                        ips_2_data = DEV.magnet_2.get_data_list()
                        ips_2_timestamp = ips_2_data["timestamp"]
                        ips_2_mfield = ips_2_data["field"]

                    self.data["ips_2_timestamp"].extend(ips_2_timestamp)
                    self.data["ips_2_mfield"].extend(ips_2_mfield)
    
                    if config.save_good_old_txt:
                        saving_data = [ips_2_timestamp,ips_2_mfield]
                        save_data(self.f_ips_2, saving_data)
                
                    if not self.hdf5_file == None:
                        try:
                            self.hdf5_file.save_magnet(1,ips_2_timestamp,ips_2_mfield)
                        except Exception,e:
                            log("Failed to Save IPS2 HDF5",e)
                except Exception,e:
                    log("Magnet 2 failed DAQ",e)
            
            except Exception,e:
                log("Error while handling DAQ",e)
            finally:
                self.data_lock.release()

            time.sleep(0.2)
        initialize.close_files()
    
    """ The following functions call the different functions for different 
    measurements like IV sweep, B sweep ...
    
    Each function is called by a button action on the gui, which leads to an 
    action in 'initialize.init_connections' which calls the functions hear.
    Depending on the measurment different variable are read out. Then a new
    thread is started with the function for the measurement and the variables
    are passed."""
    
    def measurement_btn_Acquire_Ultra(self):
        thread.start_new_thread(self.aquire_ultra,())
    def measurement_btn_Acquire_Histogram(self):
        thread.start_new_thread(self.aquire_histogram,())
    def measurement_btn_Acquire_IV(self):
        _min = float(self.form_data["editIVMin"])
        _max = float(self.form_data["editIVMax"])
        _time = float(self.form_data["editIVTime"])
        _sample = self.form_data["checkIVSample"]
        _double = self.form_data["checkIVDouble"]
        #(self, _min=None, _max=None, _time=None, _sample=None, _double=None)
        thread.start_new_thread(self.aquire_iv,(_min,_max,_time,_sample,_double))
        
    def measurement_btn_Acquire_B_Circle(self):
        _radius = float(self.form_data["editBCircleRadius"])
        _stepsize = int(self.form_data["editBCircleStepsize"])     
        _start = int(self.form_data["editBCircleStart"])
        _stop = int(self.form_data["editBCircleStop"])
        
        # self, _radius, _stepsize, _start, _stop)
        thread.start_new_thread(self.aquire_b_circle,(_radius, _stepsize, _start, _stop))
    def measurement_btn_Acquire_B_Sweep(self):
        _max = float(self.form_data["editBSweepMax"])
        _axes = int(self.form_data["comboBSweepAxes"])
        if _axes == 0:
            _rate = float(self.form_data["editBRate"])
        else:
            _rate = float(self.form_data["editBRate_2"])
        # self, _max=None, _rate=None, _axes=None
        thread.start_new_thread(self.aquire_b_sweep,(_max,_rate,_axes))
        
    def measurement_btn_Acquire_B_IV_Map(self):
        # variables for the B field
        _minB = float(self.form_data["editBIVMapMinB"])
        _maxB = float(self.form_data["editBIVMapMaxB"])
        _steps = float(self.form_data["editBIVMapIncB"])
        _rate = float(self.from_data["editBIVMapRateB"])
        _axes = int(self.form_data["comboBIVMapAxes"])
        # variables for the IV sweeps
        _minV = float(self.form_data["editBIVMapMinV"])
        _maxV = float(self.form_data["editBIVMapMaxV"])
        _timeV = float(self.form_data["editBIVMapTimeV"])
        _double = self.form_data["checkBIVdouble"]
        _sample = self.form_data["checkBIVsample"]
        #self, _minB=None, _maxB=None, _steps=None, _rate=None, _axes=None, _minV=None, _maxV=None, _timeV=None, _sample=None, _double=None, _resync_lockin=True
        thread.start_new_thread(self.aquire_b_iv_map,(_minB,_maxB,_steps,_rate,_axes,
                                                      _minV,_maxV,_timeV,_sample,_double))
            
    def return_param_string(self):
        """This function produces a string which all latest values of all 
        devices includes.
        
        Returns
        -------
        params_str : String
            This string contains all values of all devices in an order of the 
            dictionary --> looks quiet arbitrary.
            This string is saved in all collected data files at the beginning."""
            
        params_str = ""
        try:
            params = self.data.copy()
            params.update(DEV.lockin.get_param())
            params_str = "PARAMS:%i,"%(len(params))
            for k,v in params.items():
                if len(v) > 0:
                    params_str += ("%s:%s,"%(str(k),str(v[-1])))
            for k,v in self.config_data.items():
                if type(v).__name__ == "float" or type(v).__name__ == "int":
                    params_str += ("%s:%s,"%(str(k),str(v)))
        except Exception,e:
            print k,v
            log("IV Parameter Save failed",e)   
        return params_str      
        
    def execute(self):
        """Executes a command given in the command line.
        
        This function is called by a line in 'initialize.init_connection, which
        gets in action bythe Button 'Execute' in the Main Tab. Then it executes
        the command given in the command line in the Main Tab."""
        
        try:
            exec(str(self.form_data["editCommand"]))
        except Exception,e:
            log("Execution failed",e)
        
    def closeEvent(self, event):
        '''Ask before closing'''
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            try:
                write_config(self.ui)
                DEV.stop = True # send terminate signal
                self.stop_measure = True # send terminate signal main app
                self.shutdown = True # send terminate signal main app
                self.temp_sweep_abort = True
                time.sleep(2)   # wait all threads to terminate
                initialize.close_files()
                log("Exiting")
            except Exception,e:
                print e
            event.accept()
        else:
            event.ignore()
    
            
myapp = None     
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    global myapp
    myapp = main_program()
    myapp.show()

    sys.exit(app.exec_())