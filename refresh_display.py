# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 14:19:42 2014
All rights reserved by David Weber
@author: David Weber
"""
import numpy as np
import time
from functions import log, find_min, round_to_digits, interpolate
from PyQt4 import QtGui
import devices_andreev as DEV
import inspect
import re

_self = None


def refresh_display():
    """This function is called every second for misc functions""" 
                           
    global _self
    try:
        
        try: # updating ui data

            form_objects = inspect.getmembers(_self.ui)
            for element in form_objects:
                try:
                    if element[1].__class__.__name__ == 'QLineEdit':
                        _self.form_data[str(element[1].objectName())] = element[1].text()
                     
                    if element[1].__class__.__name__ == 'QTabWidget':
                        _self.form_data[str(element[1].objectName())] = element[1].currentIndex()
                    
                    if element[1].__class__.__name__ == 'QComboBox':
                        _self.form_data[str(element[1].objectName())] = element[1].currentIndex()
                    
                    if element[1].__class__.__name__ == 'QCheckBox':
                        _self.form_data[str(element[1].objectName())] = element[1].isChecked()
                        
                    if element[1].__class__.__name__ == 'QTextEdit':
                        _self.form_data[str(element[1].objectName())] = element[1].toPlainText()
                except Exception,e:
                    log("Failed to automatically read out the form parameters %s"%(str(element[1].objectName())),e)
        except Exception,e:
            log("Failed updating form parameters",e)
            
            
        # filtering of values for plotting
        _time = time.time()
        begin = _time - int(_self.form_data["editViewBegin"])
        end = _time - int(_self.form_data["editViewEnd"])

        step = int(_self.form_data["editViewStep"])
        interval = int(_self.form_data["editTimerInterval"])
        
        max_datalength = int(_self.ui.editMaximumValues.text())
        for k,v in _self.data.items():
            _self.data[k] = v[-max_datalength:]
        
        _self.ui.labSample.setText(str(len(_self.data["agilent_voltage_timestamp"])))
        
        try:
            _sample_res= abs(_self.data["agilent_voltage_voltage"][-1]/_self.data["agilent_current_voltage"][-1]*_self.rref)
            sample_factor = _sample_res/(_sample_res+_self.rref)
            #_self.ui.editIVTimeEstimate.setText("%i s"%(round((_self.editIVDelay)*(abs(_self.editIVMax-_self.editIVMin)/_self.editIVSteps)))) 
            edit_min = float(_self.form_data["editIVMin"])
            edit_max = float(_self.form_data["editIVMax"])
            if _self.form_data["checkIVSample"]:
                _self.ui.editIVMinEstimate.setText("%g mV"%(round_to_digits(edit_min / sample_factor * 1e3,3)))
                _self.ui.editIVMaxEstimate.setText("%g mV"%(round_to_digits(edit_max / sample_factor * 1e3,3)))
                #_self.ui.editIVStepsEstimate.setText("%g uV"%(round_to_digits(_self.editIVSteps / sample_factor * 1e6,3)))
            else:
                _self.ui.editIVMinEstimate.setText("%g mV"%(round_to_digits(sample_factor * edit_min * 1e3,3)))
                _self.ui.editIVMaxEstimate.setText("%g mV"%(round_to_digits(sample_factor * edit_max * 1e3,3)))
                #_self.ui.editIVStepsEstimate.setText("%g uV"%(round_to_digits(sample_factor * _self.editIVSteps * 1e6,3)))
        except Exception,e:
            log("Refresh Estimate Failed",e)#$(time::%d.%m.%y)
            
        try:
            # saving button
            if not _self.hdf5_file == None:
                _self.ui.btnSaving.setText("saving")
                _self.ui.btnSaving.setStyleSheet('QPushButton {color: green}')
            else:
                _self.ui.btnSaving.setText("idle")
                _self.ui.btnSaving.setStyleSheet('QPushButton {color: grey}')
        except Exception,e:
            log("Problem setting saving button color",e)
            
            
        try:
            voltage = _self.data["agilent_voltage_voltage"][-1] * (10**_self.config_data["range_voltage"]) + _self.config_data["offset_voltage"]
            current = _self.data["agilent_current_voltage"][-1] * (10**_self.config_data["range_current"]) + _self.config_data["offset_current"]
            _self.ui.btnFemtoVoltage.setText("%.3f"%(voltage))
            _self.ui.btnFemtoCurrent.setText("%.3f"%(current))
            if abs(voltage) > 11.5:
                _self.ui.btnFemtoVoltage.setStyleSheet('QPushButton {color: red}')
            else:
                _self.ui.btnFemtoVoltage.setStyleSheet('QPushButton {color: green}')
            if abs(current) > 11.5:
                _self.ui.btnFemtoCurrent.setStyleSheet('QPushButton {color: red}')
            else:
                _self.ui.btnFemtoCurrent.setStyleSheet('QPushButton {color: green}')
        except Exception,e:
            log("Button Femto update failed",e)        
        try:
            if DEV.lockin == None:
                _self.ui.btnStatusLockin.setStyleSheet('QPushButton {color: grey}')
            else:
                _self.ui.btnStatusLockin.setStyleSheet('QPushButton {color: green}')
            if DEV.agilent_new == None or DEV.agilent_old == None:
                _self.ui.btnStatusAgilents.setStyleSheet('QPushButton {color: grey}')
            else:
                _self.ui.btnStatusAgilents.setStyleSheet('QPushButton {color: green}')
            if DEV.lakeshore == None:
                _self.ui.btnStatusTemperatur.setStyleSheet('QPushButton {color: grey}')
            else:
                _self.ui.btnStatusTemperatur.setStyleSheet('QPushButton {color: green}')
            if DEV.yoko == None:
                _self.ui.btnStatusYoko.setStyleSheet('QPushButton {color: grey}')
            else:
                _self.ui.btnStatusYoko.setStyleSheet('QPushButton {color: green}')
            if DEV.motor == None:
                _self.ui.btnStatusMotor.setStyleSheet('QPushButton {color: grey}')
            else:
                _self.ui.btnStatusMotor.setStyleSheet('QPushButton {color: green}')
            if DEV.magnet == None:
                _self.ui.btnStatusMagnet.setStyleSheet('QPushButton {color: grey}')
            else:
                _self.ui.btnStatusMagnet.setStyleSheet('QPushButton {color: green}')
        except Exception,e:
            log("Button Status update failed",e)
        
        try:
            if DEV.magnet == None:
                _self.ui.labelSwitchHeater.setText("???")
            else:
                if DEV.magnet.heater:
                    _self.ui.labelSwitchHeater.setText("ON")
                else:
                    _self.ui.labelSwitchHeater.setText("OFF")
        except Exception,e:
            log("Switch Heater Status Update Error",e)
        try:
            if DEV.magnet_2 == None:
                _self.ui.labelSwitchHeater_2.setText("???")
            else:
                if DEV.magnet_2.heater:
                    _self.ui.labelSwitchHeater_2.setText("ON")
                else:
                    _self.ui.labelSwitchHeater_2.setText("OFF")
        except Exception,e:
            log("Switch Heater Status Update Error",e)
                
        # limit range
        interval = max(100, min(interval, 10000))
        _self.timer_display.setInterval(interval)

        
        # 1 + 2
        try:
            x0 = find_min(_self.data["agilent_voltage_timestamp"],begin)
            x1 = find_min(_self.data["agilent_voltage_timestamp"],end)
            y0 = find_min(_self.data["agilent_current_timestamp"],begin)
            y1 = find_min(_self.data["agilent_current_timestamp"],end)
            
            agilent_voltage_x = np.array(_self.data["agilent_voltage_timestamp"][x0:x1:step])-_self._start_time
            agilent_current_x = np.array(_self.data["agilent_current_timestamp"][y0:y1:step])-_self._start_time
            _self.data_curve1.set_data(agilent_voltage_x, np.array(_self.data["agilent_voltage_voltage"][x0:x1:step]))
            _self.data_curve2.set_data(agilent_current_x, np.array(_self.data["agilent_current_voltage"][y0:y1:step]))
            #if _self.form_data["checkAuto1a"]:
            #    _self.ui.cw1.plot.setAxisAutoScale(_self.ui.cw1.plot.Y_LEFT)
            #if _self.form_data["checkAuto1b"]:
            #    _self.ui.cw1.plot.setAxisAutoScale(_self.ui.cw1.plot.Y_RIGHT)
            #_self.ui.cw1.plot.setAxisAutoScale(_self.ui.cw1.plot.X_BOTTOM)
            #_self.ui.cw1.plot.replot()
            _self.ui.cw1.plot.do_autoscale()
        except Exception,e:
            log("Displaying Voltage/Current",e)
            #print _self.data["agilent_voltage_voltage"]
        
        
        # 3 + 4
        try:
            x0 = find_min(_self.data["motor_timestamp"],begin)
            x1 = find_min(_self.data["motor_timestamp"],end)
            
            motor_x = np.array(_self.data["motor_timestamp"][x0:x1:step])-_self._start_time
            _self.data_curve3.set_data(motor_x, _self.data["motor_pos"][x0:x1:step])
            _self.data_curve4.set_data(motor_x, _self.data["motor_vel"][x0:x1:step])
            _self.ui.cw2.plot.do_autoscale()
        except Exception,e:
            log("Displaying Motor",e)

        # 5 + 6 + 6b
        try:
            x0 = find_min(_self.data["temp_timestamp"],begin)
            x1 = find_min(_self.data["temp_timestamp"],end)                
            
            temp_x = np.array(_self.data["temp_timestamp"][x0:x1:step])-_self._start_time
            if _self.ui.checkViewT1.isChecked():            
                _self.data_curve6.set_data(temp_x, _self.data["temp1"][x0:x1:step])
            else:
                _self.data_curve6.set_data([],[])
            if _self.ui.checkViewT2.isChecked():
                _self.data_curve6b.set_data(temp_x, _self.data["temp2"][x0:x1:step]) 
            else:
                _self.data_curve6b.set_data([],[])
            _self.ui.cw3.plot.do_autoscale()
            
            try:
                x0 = find_min(_self.data["ips_timestamp"],begin)
                x1 = find_min(_self.data["ips_timestamp"],end)
                            
                ips_x = np.array(_self.data["ips_timestamp"][x0:x1:step])-_self._start_time
                _self.data_curve5.set_data(ips_x, _self.data["ips_mfield"][x0:x1:step])
            except Exception,e:
                log("IPS Display Failed",e)
            
            try:
                x0 = find_min(_self.data["ips_2_timestamp"],begin)
                x1 = find_min(_self.data["ips_2_timestamp"],end)
                                
                ips_x = np.array(_self.data["ips_2_timestamp"][x0:x1:step])-_self._start_time
                _self.data_curve5b.set_data(ips_x, _self.data["ips_2_mfield"][x0:x1:step])
            except Exception,e:
                log("IPS 2 Display Failed",e)
            _self.ui.cw3.plot.do_autoscale()
        except Exception,e:
            log("Displaying IPS+TEMP",e)
        
        # 7 + 8  
        try:
            if len((_self.data["agilent_voltage_timestamp"])) > 5 and len((_self.data["agilent_current_timestamp"])) > 5 :
                _self.rref = float(_self.ui.editRRef.text())
                
                x0 = find_min(_self.data["agilent_voltage_timestamp"],begin)
                x1 = find_min(_self.data["agilent_voltage_timestamp"],end)
                voltage_timestamp = _self.data["agilent_voltage_timestamp"][x0:x1]
                voltage = np.array(_self.data["agilent_voltage_voltage"][x0:x1])
                
                current_index = min(len(_self.data["agilent_current_timestamp"]),len(_self.data["agilent_current_voltage"]))-1
                current = np.interp(voltage_timestamp,_self.data["agilent_current_timestamp"][0:current_index],_self.data["agilent_current_voltage"][0:current_index])

                resistance_x = np.array(voltage_timestamp)-_self._start_time
                try:
                    min_index = min(len(voltage),len(current))-1
                    r_y = abs(voltage[0:min_index]/current[0:min_index]*_self.rref)
                    _self.data_curve7.set_data(resistance_x, r_y)
                except Exception,e:
                    _self.data_curve7.set_data([0,1,2],[3,1,2]) 
                    log("Lengths:diff x %i, x0 %i,x1 %i,voltage_timestamp %i, voltage %i, current %i, res %i"%(x1-x0,x0,x1,len(voltage_timestamp),len(voltage),len(current),len(resistance_x)))
                    log("Resistance Calculation failed",e)
                    
                if _self.form_data["checkViewConductance"]:
                    try:
                        g_y = 12900.0/r_y
                        _self.data_curve8.set_data(resistance_x, g_y)
                    except Exception,e:
                        log("Conductance calculation failed",e)
                        _self.data_curve8.set_data([0,1,2],[1,5,2])
                else:
                    _self.data_curve8.set_data([],[])

            if _self.form_data["checkViewConductanceLI"]:
                try:
                    # begin und end = jetzt - etwas kleines
                    x_list = np.arange(begin,end,0.25)
     
                    li_0_x_interp = interpolate(x_list, _self.data["li_timestamp_0"], _self.data["li_0_x"])
                    li_0_y_interp = interpolate(x_list, _self.data["li_timestamp_0"], _self.data["li_0_y"])
                    li_3_x_interp = interpolate(x_list, _self.data["li_timestamp_3"], _self.data["li_3_x"])
                    li_3_y_interp = interpolate(x_list, _self.data["li_timestamp_3"], _self.data["li_3_y"])
    
                    li_0_r = np.sqrt(np.square(li_0_x_interp)+np.square(li_0_y_interp))
                    li_3_r = np.sqrt(np.square(li_3_x_interp)+np.square(li_3_y_interp))
                    
                    li_first = li_3_r/li_0_r*12900.0/_self.rref
                    
                    _self.data_curve8b.set_data(x_list-_self._start_time, li_first)
                except Exception,e:
                    log("Failed to Display LI Conductance",e)
                    _self.data_curve8b.set_data([],[])
            else:
                _self.data_curve8b.set_data([],[])
                    
                
            #log("%i"%(len(_self.data["li_timestamp_0"])))
            try:
                _self.ui.cw4.plot.do_autoscale()
            except Exception,e:
                log("Autoscale CW4 failed",e)
   
        except Exception,e:
            log("Displaying Agilents Resistance",e)
 
        try:
            if _self.plot_data["new"][0]:
                _self.data_curve9.set_data(np.array(_self.plot_data["x1"]),np.array(_self.plot_data["y1"]))
                _self.ui.cw5.plot.do_autoscale()
                _self.plot_data["new"][0] = False
            if _self.plot_data["new"][2]:
                _self.data_curve11.set_data(np.array(_self.plot_data["x3"]),np.array(_self.plot_data["y3"]))
                _self.ui.cw6.plot.do_autoscale()
                _self.plot_data["new"][2] = False
            if _self.plot_data["new"][3]:
                _self.data_curve12.set_data(np.array(_self.plot_data["x4"]),np.array(_self.plot_data["y4"]))                
                _self.ui.cw6.plot.do_autoscale()
                _self.plot_data["new"][3] = False     
            if _self.plot_data["save"]:
                # save bitmap
                _self.plot_data["save"] = False
                d = str(_self.ui.editSetupDir.text())+str(_self.ui.editHeader.text())+"\\" 
                file_string = "iv_%s.png"%(_self.last_iv_name)
                _self.ui.cw5.plot.save_widget(d+file_string)
                file_string = "iv_%s_lockin.png"%(_self.last_iv_name)
                _self.ui.cw6.plot.save_widget(d+file_string)
                
        except Exception,e:
            log("Extra",e)            
    except Exception,e:
        log("Error updating Display",e)

    try:
        item_count = 0
        data = []
        for k,v in _self.data.items():
            try:
                _visible = True    # check for not wanted values
                for _split in _self._excluded_splits:
                    if _split in k.split("_"):
                        _visible = False
                if _visible and len(v) > 0:
                    data.append([str(k),v[-1]])
                    item_count += 1
            except Exception,e:
                log("Error displaying data: "+str(k),e)
        
        # this part adds on the fly calculated values used defined
        try:
            # additional calculated values
            add_values = {}
            diff_commands = str(_self.form_data["textAddValues"]).split(";")
            for com in diff_commands:
                splits = com.split(":")
                add_values[splits[0]] = splits[1]
                
            for k,v in add_values.iteritems():
                data_tokens = re.findall(r"\[(.*?)\]",v)

                for data_k,data_v in _self.data.items():
                    for token in data_tokens:
                        if data_k == token:
                            par_token = "["+token+"]"
                            #print par_token
                            v = v.replace(par_token, str(float(data_v[-1])))
                eval_v = eval(v)
                data.append([k,eval_v])
                item_count += 1
        except Exception,e:
            log("Failed to add additional values",e)
            
                
        data = sorted(data, key=lambda v: v[0])
        
        _self.ui.tableWidget.setColumnCount(1)
        _self.ui.tableWidget.setRowCount(item_count)
        _self.ui.tableWidget.setHorizontalHeaderLabels(["Value"])
        captions = []
        for item in data:
            captions.append(item[0])
        _self.ui.tableWidget.setVerticalHeaderLabels(captions)
        i=0
        for item in data:
            _self.ui.tableWidget.setItem(i,0,QtGui.QTableWidgetItem(str(round_to_digits(item[1],4))))
            i = i + 1
        #_self.ui.tableWidget.column
    except Exception,e:
        log("Error updating data table",e)