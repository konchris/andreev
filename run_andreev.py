#!/usr/bin/python -d
import sys
import os
from PyQt4 import QtCore, QtGui
from gui_andreev import Ui_MainWindow
import devices_andreev as DEV

#Threading
import thread
import time  
import numpy as np
#import scipy.signal as signal
#import matplotlib.mlab as mlab
#import matplotlib.pyplot as plt
#import pylab as pl

from guidata.qt.QtCore import QTimer#,SIGNAL
#---Import plot widget base class
#from guiqwt.plot import CurveWidget
from guiqwt.builder import make

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

from functions import *
import initialize

import refresh_display
#import mpl

class main_program(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        DEV.app = app
             
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
        
        #self.ui.btnBInitMagnet.clic
        
        # periodic timer for refresh
        refresh_display._self = self
        self.timer_second = QTimer()
        self.timer_second.timeout.connect(refresh_display.refresh_display)
        self.timer_second.start(250)
        
        # start saving
        #self.save_btn_Start()
        
        #########################################################
        ############## MEASUREMENT PARAMETERS ###################
        #########################################################
        #self.rref = 122120.0 # grounded one
        self.rref = 100000.0 # floating one
        self.wiring = 620.0
        self.factor_aux0 = 1.0    # real absolute voltage
        self.factor_aux1 = 1.0
        
        
        self.automatic_gain = False
        self.average_value = 100

        self._excluded_splits = ["timestamp","li","femto"]
        
        self.data_lock = thread.allocate_lock()
        thread.start_new_thread(self.measurement_thread,())    


    # offset
    def offset_correct(self, delay=0.5):
        bias = DEV.yoko.get_voltage()
        self.offset_in_progress = True
        DEV.yoko.set_voltage(0)
        DEV.yoko.output(True)
        
        # time to settle 0 value
        for i in range(10):
                app.processEvents()
                time.sleep(0.1)
        DEV.lockin.get_data_list(averages=10)
        DEV.agilent_new.get_data_list()
        DEV.agilent_old.get_data_list()
        
        # backup recent values
        (a,b) = DEV.lockin.femto_get()
        
        # sets femto to 20dB
        DEV.lockin.femto_reset()
        for amplification in range(1):
            time.sleep(0.1)
            
            for i in range(10):
                app.processEvents()
                time.sleep(delay/10.0)
            offset_timestamp = time.time()
    
            lockin_data = DEV.lockin.get_data_list(averages=10)
            offset_aux0 = np.average(lockin_data["0"]["auxin0"])
            offset_aux1 = np.average(lockin_data["0"]["auxin1"])

            if not self.f_config == None:
                self.f_config.write("offset_aux0_%i\t%f\t%f\n"%(amplification,offset_timestamp,offset_aux0))
                self.f_config.write("offset_aux1_%i\t%f\t%f\n"%(amplification,offset_timestamp,offset_aux1))
            log("offset_aux0_%i\t%fV"%(amplification,offset_aux0))
            log("offset_aux1_%i\t%fV"%(amplification,offset_aux1))
            self.config_data["offset_aux0"][amplification] = offset_aux0
            self.config_data["offset_aux1"][amplification] = offset_aux1
            
            DEV.lockin.femto_increase_amplification(channel=0)
            DEV.lockin.femto_increase_amplification(channel=1)
            time.sleep(delay/10.0)
        
        new_data = DEV.agilent_new.get_data_list()
        offset_new = np.average(new_data["voltage"])
        old_data = DEV.agilent_old.get_data_list()
        offset_old = np.average(old_data["voltage"])
        
        self.config_data["offset_agilent_voltage"][0] = offset_new
        self.config_data["offset_agilent_current"][0] = offset_old
        log("offset agilent new\t%fV"%(offset_new))
        log("offset agilent old\t%fV"%(offset_old))
        
        time.sleep(delay/10.0)
        # restore recent values
        DEV.lockin.femto_set(a,b)            
        
        self.ui.editOffsetAux0_0.setText(str(round(self.config_data["offset_aux0"][0],6)))
        self.ui.editOffsetAux0_1.setText(str(round(self.config_data["offset_aux0"][1],6)))
        self.ui.editOffsetAux0_2.setText(str(round(self.config_data["offset_aux0"][2],6)))
        self.ui.editOffsetAux0_3.setText(str(round(self.config_data["offset_aux0"][3],6)))
        self.ui.editOffsetAux1_0.setText(str(round(self.config_data["offset_aux1"][0],6)))
        self.ui.editOffsetAux1_1.setText(str(round(self.config_data["offset_aux1"][1],6)))
        self.ui.editOffsetAux1_2.setText(str(round(self.config_data["offset_aux1"][2],6)))
        self.ui.editOffsetAux1_3.setText(str(round(self.config_data["offset_aux1"][3],6)))
        
        DEV.yoko.set_voltage(bias)
        time.sleep(0.1)
        # flush data to /dev/null
        DEV.lockin.get_data_list(averages=10)
        self.offset_in_progress = False
    
       

    
        

  
    def aquire_histogram(self):
        self.stop_measure = False
        
        #self.offset_correct()
        
        # init bias        
        bias = float(self.ui.editHistogramBias.text())
        DEV.yoko.set_voltage(bias)
        DEV.yoko.output(True)
        
        # calculate conductance
        #resistance = self.data["li_aux0"][-1] / self.data["li_aux1"][-1] / self.rref
        resistance = self.data["agilent_voltage_voltage"][-1] / self.data["agilent_current_voltage"][-1] * self.rref
        # check if conductance high -> break, else close first
        if resistance > upper_res:
            self.motor_break()
        else:
            self.motor_unbreak()
                 
        while not self.stop_measure:
            try:
                # update values
                lower_cond = self.editHistogramLower
                upper_cond = self.editHistogramUpper
                bias = self.editHistogramBias
                DEV.yoko.set_voltage(bias)
                
                # if conductance hits upper limit, break again
                if conductance > upper_cond:
                    self.motor_break()
                # at lower limit, close again, in between: nothing
                if conductance < lower_cond:
                    self.motor_unbreak()
                
                # if escape on motor limit hit
                if self.ui.checkHistogramEscape.isChecked():
                    if DEV.motor.higher_bound or DEV.motor.lower_bound:
                        log("Motor reached its bounds, escaping histogram!")
                        break
                else:
                    if DEV.motor.higher_bound:
                        log("Motor reached its bounds, trying to break again!")
                        self.motor_break()
                    if DEV.motor.lower_bound:
                        log("Motor reached its bounds, trying to close again!")
                        self.motor_unbreak()
            except Exception,e:
                log("Histogram failure",e)
            time.sleep(0.01) 
            
        DEV.motor.stop()


    
    def aquire_iv(self):
        _min = float(self.ui.editIVMin.text())
        _max = float(self.ui.editIVMax.text())
        steps = float(self.ui.editIVSteps.text())
        delay = float(self.ui.editIVDelay.text())
        
        self.stop_measure = False        
        step_list = voltage_ramp(_min,_max,steps,_circular=False)
        
        bias = DEV.yoko.get_voltage()
        
        DEV.yoko.set_voltage(step_list[0])
        DEV.yoko.output(True)
        time.sleep(0.5)
        
        # note down begin of sweep
        begin_time = time.time()
        if not self.f_config == None:
                self.f_config.write("IV_START\t%15.15f\n"%(begin_time))
        
        # last_time is used for display updating        
        last_time = time.time()          
        for _voltage in step_list:
                DEV.yoko.set_voltage(_voltage)
                
                if time.time() - last_time > 1: # check if update needed
                    last_time = time.time()

                try:
                    self.data_lock.acquire()
                    
                    x0 = find_min(self.data["agilent_voltage_timestamp"],begin_time)
                    x1 = find_min(self.data["agilent_voltage_timestamp"],last_time)
            
                    voltage_timestamp = np.array(self.data["agilent_voltage_timestamp"][x0:x1])
                    voltage_list = np.array(self.data["agilent_voltage_voltage"][x0:x1])
                    current_index = min(len(self.data["agilent_current_timestamp"]),len(self.data["agilent_current_voltage"]))-1
                    current_list = np.interp(voltage_timestamp,self.data["agilent_current_timestamp"][0:current_index],self.data["agilent_current_voltage"][0:current_index])
          
                    
                    # lockin data refurbishment
                    li_0_x = np.array(self.data["li_0_x"])        # voltage first
                    li_1_x = np.array(self.data["li_1_x"])        # voltage second
                    li_3_x = np.array(self.data["li_3_x"])        # current first
                    li_4_x = np.array(self.data["li_4_x"])        # current second
                    
                    li_0_y = np.array(self.data["li_0_y"])        # voltage first
                    li_1_y = np.array(self.data["li_1_y"])        # voltage second
                    li_3_y = np.array(self.data["li_3_y"])        # current first
                    li_4_y = np.array(self.data["li_4_y"])        # current second
            
                    li_0_timestamp = np.array(self.data["li_timestamp_0"])
                    li_1_timestamp = np.array(self.data["li_timestamp_1"])
                    li_3_timestamp = np.array(self.data["li_timestamp_3"])
                    li_4_timestamp = np.array(self.data["li_timestamp_4"])           
                    
                    #print("%i,%i"%(len(li_0_timestamp),len(li_0)))
                    min_0 = min(len(li_0_timestamp),len(li_0_x))-1
                    li_0_x_interp = np.interp(voltage_timestamp, li_0_timestamp[0:min_0], li_0_x[0:min_0])
                    li_0_y_interp = np.interp(voltage_timestamp, li_0_timestamp[0:min_0], li_0_y[0:min_0])
                    min_1 = min(len(li_1_x),len(li_1_timestamp))-1
                    li_1_x_interp = np.interp(voltage_timestamp, li_1_timestamp[0:min_1], li_1_x[0:min_1])
                    li_1_y_interp = np.interp(voltage_timestamp, li_1_timestamp[0:min_1], li_1_y[0:min_1])
                    min_3 = min(len(li_3_x),len(li_3_timestamp))-1
                    li_3_x_interp = np.interp(voltage_timestamp, li_3_timestamp[0:min_3], li_3_x[0:min_3])
                    li_3_y_interp = np.interp(voltage_timestamp, li_3_timestamp[0:min_3], li_3_y[0:min_3])
                    min_4 = min(len(li_4_x),len(li_4_timestamp))-1
                    li_4_x_interp = np.interp(voltage_timestamp, li_4_timestamp[0:min_4], li_4_x[0:min_4])
                    li_4_y_interp = np.interp(voltage_timestamp, li_4_timestamp[0:min_4], li_4_y[0:min_4])
                    
                    li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
                    li_1_r = np.sqrt(np.square(li_1_x_interp)+np.square(li_1_y_interp))
                    li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
                    li_4_r = np.sqrt(np.square(li_4_x_interp)+np.square(li_4_y_interp))
                    li_first = li_3_r/self.rref/li_0_r    # first
                    li_second = li_4_r/self.rref/li_1_r   # second
                    
            
                    self.plot_data["x1"] = voltage_list[:]
                    self.plot_data["y1"] = current_list[:]
                    
                    self.plot_data["x3"] = voltage_list[:]
                    self.plot_data["y3"] = li_first[:]
                    
                    self.plot_data["x4"] = voltage_list[:]
                    self.plot_data["y4"] = li_second[:]
                    
                    self.plot_data["new"][0] = True
                    self.plot_data["new"][2] = True
                    self.plot_data["new"][3] = True
                    
                finally:
                    self.data_lock.release()
                   
                time.sleep(delay)
                app.processEvents()
                if self.stop_measure:
                    break

        # note down end of iv sweep
        end_time = time.time()
        if not self.f_config == None:
                self.f_config.write("IV_START\t%15.15f\t\n"%(end_time))
                
        time.sleep(0.5)        
        # switch back voltage
        DEV.yoko.set_voltage(bias)
        
       


        try:
            self.data_lock.acquire()
            
            x0 = find_min(self.data["agilent_voltage_timestamp"],begin_time)
            x1 = find_min(self.data["agilent_voltage_timestamp"],last_time)
            
            voltage_timestamp = np.array(self.data["agilent_voltage_timestamp"][x0:x1])
            voltage_list = np.array(self.data["agilent_voltage_voltage"][x0:x1])
            current_index = min(len(self.data["agilent_current_timestamp"]),len(self.data["agilent_current_voltage"]))-1
            current_list = np.interp(voltage_timestamp,self.data["agilent_current_timestamp"][0:current_index],self.data["agilent_current_voltage"][0:current_index])
            
            # lockin data refurbishment
            li_0_x = np.array(self.data["li_0_x"])        # voltage first
            li_1_x = np.array(self.data["li_1_x"])        # voltage second
            li_3_x = np.array(self.data["li_3_x"])        # current first
            li_4_x = np.array(self.data["li_4_x"])        # current second
            
            li_0_y = np.array(self.data["li_0_y"])        # voltage first
            li_1_y = np.array(self.data["li_1_y"])        # voltage second
            li_3_y = np.array(self.data["li_3_y"])        # current first
            li_4_y = np.array(self.data["li_4_y"])        # current second
    
            li_0_timestamp = np.array(self.data["li_timestamp_0"])
            li_1_timestamp = np.array(self.data["li_timestamp_1"])
            li_3_timestamp = np.array(self.data["li_timestamp_3"])
            li_4_timestamp = np.array(self.data["li_timestamp_4"])           
            
            #print("%i,%i"%(len(li_0_timestamp),len(li_0)))
            min_0 = min(len(li_0_timestamp),len(li_0_x))-1
            li_0_x_interp = np.interp(voltage_timestamp, li_0_timestamp[0:min_0], li_0_x[0:min_0])
            li_0_y_interp = np.interp(voltage_timestamp, li_0_timestamp[0:min_0], li_0_y[0:min_0])
            min_1 = min(len(li_1_x),len(li_1_timestamp))-1
            li_1_x_interp = np.interp(voltage_timestamp, li_1_timestamp[0:min_1], li_1_x[0:min_1])
            li_1_y_interp = np.interp(voltage_timestamp, li_1_timestamp[0:min_1], li_1_y[0:min_1])
            min_3 = min(len(li_3_x),len(li_3_timestamp))-1
            li_3_x_interp = np.interp(voltage_timestamp, li_3_timestamp[0:min_3], li_3_x[0:min_3])
            li_3_y_interp = np.interp(voltage_timestamp, li_3_timestamp[0:min_3], li_3_y[0:min_3])
            min_4 = min(len(li_4_x),len(li_4_timestamp))-1
            li_4_x_interp = np.interp(voltage_timestamp, li_4_timestamp[0:min_4], li_4_x[0:min_4])
            li_4_y_interp = np.interp(voltage_timestamp, li_4_timestamp[0:min_4], li_4_y[0:min_4])
            
            li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
            li_1_r = np.sqrt(np.square(li_1_x_interp)+np.square(li_1_y_interp))
            li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
            li_4_r = np.sqrt(np.square(li_4_x_interp)+np.square(li_4_y_interp))
            li_first = li_3_r/self.rref/li_0_r    # first
            li_second = li_4_r/self.rref/li_1_r   # second
            
            
            self.plot_data["x1"] = voltage_list[:]
            self.plot_data["y1"] = current_list[:]
            
            self.plot_data["x3"] = voltage_list[:]
            self.plot_data["y3"] = li_first[:]
            
            self.plot_data["x4"] = voltage_list[:]
            self.plot_data["y4"] = li_second[:]
            
            self.plot_data["new"][0] = True
            self.plot_data["new"][2] = True
            self.plot_data["new"][3] = True
            
            try:        
                saving_data = [voltage_timestamp, voltage_list, current_list, li_0_x_interp, li_0_y_interp, li_1_x_interp, li_1_y_interp, li_3_x_interp, li_3_y_interp, li_4_x_interp, li_4_y_interp]
                d = str(self.ui.editSetupDir.text())+str(self.ui.editHeader.text())+"\\"    
                d_name = os.path.dirname(d)
                if not os.path.exists(d_name):
                    os.makedirs(d_name)
                file_string = "iv_%i.txt"%(round(time.time()))
                f_iv = open(d+file_string, 'a')
                save_data(f_iv, saving_data)
                f_iv.close()
                self.ui.editLastIV.setText(file_string)
            except Exception,e:
                log("Failed to Save IV",e)
        except Exception,e:
            log("IV Calculation Failed",e)
        finally:
            self.data_lock.release()
            
        

    
    def temp_sweep(self):       
        start = float(self.ui.editTempSweepStart.text())
        end = float(self.ui.editTempSweepStop.text())
        steps = abs(float(self.ui.editTempSweepStep.text()))
        delay = float(self.ui.editTempSweepDelay.text())
        log("Temperature Sweep %f Kto %f K,%f mK steps,%f s delay"%(start,end,steps*1000,delay))
        
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
        log("Temperature Sweep finished")
        
    
    def aquire_b_sweep(self):
        self.stop_measure = False
               
        min = float(self.ui.editBMin.text())
        max = float(self.ui.editBMax.text())
        rate = float(self.ui.editBRate.text())
        bias = float(self.ui.editBBias.text())
        
        fields = [0,max,0,min,0]
        field_index = 0
        
        DEV.yoko.set_voltage(bias)
        DEV.yoko.output(True)
        
        DEV.agilent_new.setup_dc()
        DEV.agilent_new.set_nplc(1)
        
        DEV.agilent_old.setup_dc()
        DEV.agilent_old.set_nplc(1)               
        
        while not self.stop_measure:
            if self.data["magnet_field"][-1] == fields[field_index]:
                if field_index >= len(fields)-1:
                    log("Fields done!")
                    self.stop_measure = True
                else:
                    field_index += 1
                    DEV.magnet.SetField(fields[field_index], rate)   
                
            time.sleep(0.01)
             
        # switch off voltage
        DEV.yoko.set_voltage(0)   
   
   
   

   
    def measurement_thread(self):
        """This thread is measuring data all time"""

        while not self.shutdown:
            try:
                self.data_lock.acquire()
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
                            lockin_data = DEV.lockin.get_data_list(averages=self.average_value)
        
                            li_timestamp_0 = average_chunks(lockin_data["0"]["timestamp"],self.average_value)
                            li_aux0 =  [(x - self.config_data["offset_aux0"][0])*(self.factor_aux0) for x in average_chunks(lockin_data["0"]["auxin0"],self.average_value)] 
                            li_aux1 =  [(x - self.config_data["offset_aux1"][0])*(self.factor_aux1) for x in average_chunks(lockin_data["0"]["auxin1"],self.average_value)]
                            li_0_x =  average_chunks(lockin_data["0"]["x"],self.average_value)
                            li_0_y =  average_chunks(lockin_data["0"]["y"],self.average_value)
                            li_timestamp_1 = average_chunks(lockin_data["1"]["timestamp"],self.average_value)
                            li_1_x =  average_chunks(lockin_data["1"]["x"],self.average_value)
                            li_1_y =  average_chunks(lockin_data["1"]["y"],self.average_value)
                            li_timestamp_3 = average_chunks(lockin_data["3"]["timestamp"],self.average_value)
                            li_3_x =  average_chunks(lockin_data["3"]["x"],self.average_value)
                            li_3_y =  average_chunks(lockin_data["3"]["y"],self.average_value)
                            li_timestamp_4 = average_chunks(lockin_data["4"]["timestamp"],self.average_value)
                            li_4_x =  average_chunks(lockin_data["4"]["x"],self.average_value)
                            li_4_y =  average_chunks(lockin_data["4"]["y"],self.average_value)
                            
                            femto_timestamp = lockin_data["femto"]["timestamp"]
                            femto_channela = lockin_data["femto"]["channela"]
                            femto_channelb = lockin_data["femto"]["channelb"]
                    except Exception,e:
                        log("LockIn failed DAQ",e)
                        
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
                    
                    saving_data = [li_timestamp_0,li_aux0,li_aux1,li_0_x,li_0_y]
                    save_data(self.f_li0, saving_data)
                    saving_data = [li_timestamp_0,li_1_x,li_1_y]
                    save_data(self.f_li1, saving_data)
                    saving_data = [li_timestamp_0,li_3_x,li_3_y]
                    save_data(self.f_li3, saving_data)
                    saving_data = [li_timestamp_0,li_4_x,li_4_y]
                    save_data(self.f_li4, saving_data)
                    
                    
                    saving_data = [femto_timestamp,femto_channela,femto_channelb]
                    save_data(self.f_femto, saving_data)
                    
                if not self.offset_in_progress:
                    agilent_voltage_timestamp = []
                    agilent_voltage_voltage = []
                    try:
                        if DEV.agilent_new != None:
                            agilent_new_data = DEV.agilent_new.get_data_list()   
                            agilent_voltage_timestamp = agilent_new_data["timestamp"]
                            agilent_voltage_voltage =  [(x - self.config_data["offset_agilent_voltage"][0]) for x in agilent_new_data["voltage"]] 
                    except Exception,e:
                        log("Agilent New failed DAQ",e)
                       
                    self.data["agilent_voltage_timestamp"].extend(agilent_voltage_timestamp)
                    self.data["agilent_voltage_voltage"].extend(agilent_voltage_voltage)              
                    saving_data = [agilent_voltage_timestamp,agilent_voltage_voltage]
                    save_data(self.f_agilent_new, saving_data)    

                if not self.offset_in_progress:
                    agilent_current_timestamp = []
                    agilent_current_voltage = []
                    try:
                        if DEV.agilent_old != None:
                            agilent_old_data = DEV.agilent_old.get_data_list()   
                            agilent_current_timestamp = agilent_old_data["timestamp"]
                            agilent_current_voltage =  [(x - self.config_data["offset_agilent_current"][0]) for x in agilent_old_data["voltage"]] 
                    except Exception,e:
                        log("Agilent old failed DAQ",e)
                       
                    self.data["agilent_current_timestamp"].extend(agilent_current_timestamp)
                    self.data["agilent_current_voltage"].extend(agilent_current_voltage)              
                    saving_data = [agilent_current_timestamp,agilent_current_voltage]
                    save_data(self.f_agilent_old, saving_data)    
                    
                 
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
                except Exception,e:
                    log("Motor failed DAQ",e)
                   
                self.data["motor_timestamp"].extend(motor_timestamp)
                self.data["motor_pos"].extend(motor_pos)
                self.data["motor_cur"].extend(motor_cur)
                self.data["motor_vel"].extend(motor_vel)                
                
                saving_data = [motor_timestamp,motor_pos,motor_cur,motor_vel]

                save_data(self.f_motor, saving_data)

                temp_timestamp = []
                temp1 = []
                temp2 = []
                try:
                    if DEV.lakeshore != None:
                        temp_data = DEV.lakeshore.get_data_list()
                        temp_timestamp = temp_data["timestamp"]
                        temp1 = temp_data["temperature1"]
                        temp2 = temp_data["temperature2"]
                except Exception,e:
                    log("Temperature failed DAQ",e)
                    
                self.data["temp_timestamp"].extend(temp_timestamp)
                self.data["temp1"].extend(temp1)
                self.data["temp2"].extend(temp2)
                
                saving_data = [temp_timestamp,temp1,temp2]
                save_data(self.f_temp, saving_data)
   
                """
                ips_timestamp = []
                ips_mfield = []
                try:
                    if DEV.magnet != None:
                        ips_data = DEV.magnet.get_data_list()
                        ips_timestamp = ips_data["timestamp"]
                        ips_mfield = ips_data["field"]
                except Exception,e:
                    log("Magnet failed DAQ",e)
                    
                self.data["ips_timestamp"].extend(ips_timestamp)
                self.data["ips_mfield"].extend(ips_mfield)

                saving_data = [ips_timestamp,ips_mfield]
                save_data(self.f_ips, saving_data)"""
            
            except Exception,e:
                log("Error while handling DAQ",e)
            finally:
                self.data_lock.release()

            time.sleep(0.2)
        self.close_files()
    
     # motor
    def motor_break(self, speed=None):
        if speed == None:
            speed = float(self.ui.editSpeed.text())
        DEV.motor.set_velocity(-speed)
        log("Motor break with %f"%(-speed))
    def motor_unbreak(self, speed=None):
        if speed == None:
            speed = float(self.ui.editSpeed.text())
        DEV.motor.set_velocity(speed)
        log("Motor unbreak with %f"%(speed))
    def motor_stop(self):
        DEV.motor.set_velocity(0)
        log("Motor stop")
    def motor_home(self):
        DEV.motor.set_home()
        log("Motor homing")
    def motor_set_limit(self):
        DEV.motor.set_lower_limit(float(self.ui.editLowerLimit.text()))
        DEV.motor.set_upper_limit(float(self.ui.editUpperLimit.text()))
        DEV.motor.set_current(int(self.ui.editMotorCurrent.text()))
        DEV.motor.set_current_limit(int(self.ui.editMotorCurrentLimit.text()))
        log("Motor set limits %f,%f"%(float(self.ui.editLowerLimit.text()),
                                      float(self.ui.editUpperLimit.text())))
    
    # femto
    def ch_a_up(self):
        DEV.femto.increase_amplification(0)
        log("Femto decrease a")
    def ch_a_down(self):
        DEV.femto.decrease_amplification(0)
        log("Femto decrease b")
    def ch_b_up(self):
        DEV.femto.increase_amplification(1)
        log("Femto increase a")
    def ch_b_down(self):
        DEV.femto.decrease_amplification(1)
        log("Femto increase b")
    
    def save_description(self):
        desc = self.ui.textDescription.toPlainText()
        
        try:
            d = str(self.ui.editSetupDir.text())+str(self.ui.editHeader.text())+"\\"    
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
    def magnet_goto(self):
        try:
            field = float(self.ui.editBMax.text())
            rate = float(self.ui.editBRate.text())
        except:
            field = 0
            rate = 0.01
        print "field: %f, rate: %f"%(field,rate)
        DEV.magnet.SetField(field,rate)
    def magnet_init(self):
        DEV.magnet.initialize()
    def magnet_zero(self):
        try:
            rate = float(self.ui.editBRate.text())
        except:
            rate = 0.1
        DEV.magnet.ZeroField(rate)
    def switchheater_on(self):
        DEV.magnet.set_switchheater('ON')
    def switchheater_off(self):
        DEV.magnet.set_switchheater('OFF')
    
    def lockin_set(self):
        rate = int(self.ui.editRate.text())
        amplitude = float(self.ui.editLIAmpl.text())
        DEV.lockin.set_rate(rate)
        DEV.lockin.set_amplitude(amplitude)
    
    def lockin_read_phase(self):
        try:
            self.config_data["lockin_phases"][0] = self.config_data["lockin_phases"][0] + 180.0/3.141592*np.arctan(self.data["li_0_y"][-1]/self.data["li_0_x"][-1])    
            self.config_data["lockin_phases"][1] = self.config_data["lockin_phases"][1] + 180.0/3.141592*np.arctan(self.data["li_1_y"][-1]/self.data["li_1_x"][-1])
            self.config_data["lockin_phases"][2] = self.config_data["lockin_phases"][2] + 180.0/3.141592*np.arctan(self.data["li_3_y"][-1]/self.data["li_3_x"][-1])
            self.config_data["lockin_phases"][3] = self.config_data["lockin_phases"][3] + 180.0/3.141592*np.arctan(self.data["li_4_y"][-1]/self.data["li_4_x"][-1])
            self.ui.editLIPhase0.setText(str(round(self.config_data["lockin_phases"][0],2)))
            self.ui.editLIPhase1.setText(str(round(self.config_data["lockin_phases"][1],2)))
            self.ui.editLIPhase3.setText(str(round(self.config_data["lockin_phases"][2],2)))
            self.ui.editLIPhase4.setText(str(round(self.config_data["lockin_phases"][3],2)))
        except Exception,e:
            log("Failed to read phase",e)
        
    def lockin_set_phase(self):
        try:
            DEV.lockin.set_phases(
                self.config_data["lockin_phases"][0],
                self.config_data["lockin_phases"][1],
                self.config_data["lockin_phases"][2],
                self.config_data["lockin_phases"][3]
                )
        except Exception,e:
            log("Failed to set phase",e)
    
    def measurement_btn_IV_Sweep(self):
        thread.start_new_thread(self.measurement_IV_Sweep,())
    def measurement_btn_Acquire_Histogram(self):
        thread.start_new_thread(self.aquire_histogram,())
    def measurement_btn_Acquire_IV(self):
        thread.start_new_thread(self.aquire_iv,())
    def measurement_btn_Acquire_B(self):
        thread.start_new_thread(self.aquire_b_sweep,())
    def measurement_btn_Stop(self):
        self.stop_measure = True
    def temp_sweep_stop(self):
        self.temp_sweep_abort = True
        
    def set_bias(self):     
        bias = float(self.ui.editBias.text())
        DEV.yoko.set_voltage(bias)
        DEV.yoko.output(True)
        
    def save_btn_Start(self):
        if not self.f_li0 == None:
            self.f_li0.close()
            self.f_li1.close()
            self.f_li3.close()
            self.f_li4.close()
            self.f_agilent_new.close()
            self.f_agilent_old.close()
            self.f_motor.close()
            self.f_temp.close()
            self.f_femto.close()
            self.f_ips.close()
            self.f_config.close()
        close_logfile()
            
        d = str(self.ui.editSetupDir.text())+str(self.ui.editHeader.text())+"\\"    
        d_name = os.path.dirname(d)
        if not os.path.exists(d_name):
            os.makedirs(d_name)
        self.f_li0 = open(d+"li0.txt", 'a')
        self.f_li1 = open(d+"li1.txt", 'a')
        self.f_li3 = open(d+"li3.txt", 'a')
        self.f_li4 = open(d+"li4.txt", 'a')
        self.f_agilent_new = open(d+"agilent_new.txt", 'a')
        self.f_agilent_old = open(d+"agilent_old.txt", 'a')
        self.f_femto = open(d+"femto.txt", 'a')
        self.f_motor = open(d+"motor.txt", 'a')
        self.f_temp = open(d+"temp.txt", 'a')
        self.f_ips = open(d+"ips.txt", 'a') 
        self.f_config = open(d+"config.txt", 'a')
        set_logfile(d+"log.txt")      
        
    def close_files(self):
        if not self.f_li0 == None:
            self.f_li0.close()
            self.f_li1.close()
            self.f_li3.close()
            self.f_li4.close()
            self.f_femto.close()
            self.f_motor.close()
            self.f_temp.close()
            self.f_ips.close()
            self.f_config.close()
            self.f_li0 = None
            self.f_li1 = None
            self.f_li3 = None
            self.f_li4 = None
            self.f_agilent_new = None
            self.f_agilent_old = None
            self.f_femto = None
            self.f_motor = None
            self.f_temp = None
            self.f_ips = None
            self.f_config = None
            close_logfile()
    
    # temp
    def set_temp_parameters(self):
        try:
            setpoint = float(self.ui.editTempSetpoint.text())
            heater = int(self.ui.editTempHeater.text())
            p = float(self.ui.editTempP.text())
            i = float(self.ui.editTempI.text())
            d = float(self.ui.editTempD.text())
            
            DEV.lakeshore.set_setpoint(setpoint)
            DEV.lakeshore.set_heater_range(heater)
            DEV.lakeshore.set_pid(p,i,d)
        except Exception,e:
            log("New Temp was not accepted",e)
            
    def temp_custom(self):
        try:
            val_1a = self.ui.comboTemperatureDisplay1a.currentIndex()
            val_1b = self.ui.comboTemperatureDisplay1b.currentIndex()+1
            val_2a = self.ui.comboTemperatureDisplay2a.currentIndex()
            val_2b = self.ui.comboTemperatureDisplay2b.currentIndex()+1
            val_3a = self.ui.comboTemperatureDisplay3a.currentIndex()
            val_3b = self.ui.comboTemperatureDisplay3b.currentIndex()+1
            val_4a = self.ui.comboTemperatureDisplay4a.currentIndex()
            val_4b = self.ui.comboTemperatureDisplay4b.currentIndex()+1

            DEV.lakeshore.set_display(6)    # custom display
            DEV.lakeshore.set_display_field(1,val_1a,val_1b)
            DEV.lakeshore.set_display_field(2,val_2a,val_2b)
            DEV.lakeshore.set_display_field(3,val_3a,val_3b)
            DEV.lakeshore.set_display_field(4,val_4a,val_4b)
        except Exception,e:
            log("New Display Setup not accepted",e)
        
        
    def execute(self):
        try:
            exec(str(self.ui.editCommand.text()))
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
                log("Exiting")
            except Exception,e:
                print e
            event.accept()
        else:
            event.ignore()
    
            
     
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = main_program()
   
    myapp.show()

    sys.exit(app.exec_())