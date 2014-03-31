# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 14:19:42 2014

@author: David Weber
"""
import numpy as np
import time
from functions import log, find_min
from PyQt4 import QtGui
import devices_andreev as DEV

_self = None


def refresh_display():
    """This function is called every second for misc functions""" 
    #try:
    #    export_html(_self.ui, "C:\wamp\www\\")
    #except Exception,e:
    #    log("HTML export failed",e)                               
    global _self
    try:
        # filtering of values for plotting
        begin = int(_self.ui.editViewBegin.text())
        end = int(_self.ui.editViewEnd.text())
        _time = time.time()
        begin = _time - begin
        end = _time - end
        step = int(_self.ui.editViewStep.text()) 
        interval = int(_self.ui.editTimerInterval.text())
        
        try: # updating ui data
            _self.average_value = int(_self.ui.editAverage.text())
            _self.automatic_gain = _self.ui.checkAutomaticGain.isChecked()
            _self.editHistogramLower = float(_self.ui.editHistogramLower.text())
            _self.editHistogramUpper = float(_self.ui.editHistogramUpper.text())
            _self.editHistogramBias = float(_self.ui.editHistogramBias.text())
            _self.checkHistogramEscape = _self.ui.checkHistogramEscape.isChecked()
            _self.editHistogramOpeningSpeed = float(_self.ui.editHistogramOpeningSpeed.text())
            _self.editHistogramClosingSpeed = float(_self.ui.editHistogramClosingSpeed.text())
            
            # iv
            _self.editIVDelay = float(_self.ui.editIVDelay.text())
            _self.editIVSteps = float(_self.ui.editIVSteps.text())
            _self.editIVMin = float(_self.ui.editIVMin.text())
            _self.editIVMax = float(_self.ui.editIVMax.text())
            _self.checkIVSample = bool(_self.ui.checkIVSample.isChecked())
            
            # ultra
            _self.editUltraMin = float(_self.ui.editUltraMin.text())
            _self.editUltraMax = float(_self.ui.editUltraMax.text())
            _self.editUltraStabilizeTime = float(_self.ui.editUltraStabilizeTime.text())
            _self.editUltraColdTime = float(_self.ui.editUltraColdTime.text())
            
            _self.factor_voltage = float(_self.ui.editFactorVoltage.text())
            _self.factor_current = float(_self.ui.editFactorCurrent.text())
        except Exception,e:
            log("Failed updating ui parameters",e)
        
        max_datalength = int(_self.ui.editMaximumValues.text())
        for k,v in _self.data.items():
            _self.data[k] = v[-max_datalength:]
        
        _self.ui.labSample.setText(str(len(_self.data["agilent_voltage_timestamp"])))
        
        try:
            _sample_res= abs(_self.data["agilent_voltage_voltage"][-1]/_self.data["agilent_current_voltage"][-1]*_self.rref)
            sample_factor = _sample_res/(_sample_res+_self.rref)
            _self.ui.editIVTimeEstimate.setText("%i s"%(round((_self.editIVDelay)*(abs(_self.editIVMax-_self.editIVMin)/_self.editIVSteps)))) 
            if _self.checkIVSample:
                _self.ui.editIVMinEstimate.setText("%f mV"%(_self.editIVMin / sample_factor * 1e3))
                _self.ui.editIVMaxEstimate.setText("%f mV"%(_self.editIVMax / sample_factor * 1e3))
                _self.ui.editIVStepsEstimate.setText("%f uV"%(_self.editIVSteps / sample_factor * 1e6))
            else:
                _self.ui.editIVMinEstimate.setText("%f mV"%(sample_factor * _self.editIVMin * 1e3))
                _self.ui.editIVMaxEstimate.setText("%f mV"%(sample_factor * _self.editIVMax * 1e3))
                _self.ui.editIVStepsEstimate.setText("%f uV"%(sample_factor * _self.editIVSteps * 1e6))
        except Exception,e:
            log("Refresh Estimate Failed",e)
            
        try:
            # saving button
            saving = True
            saves = ""
            if not _self.f_config:
                saving = False
            else:
                saves = saves + "c"
            if not (_self.f_agilent_voltage and _self.f_agilent_current):
                saving = False
            else:
                saves = saves + "a"
            if not _self.f_ips:
                saving = False
            else:
                saves = saves + "i"
            if not (_self.f_li0 and _self.f_li1 and _self.f_li3 and _self.f_li4 and _self.f_femto):
                saving = False
            else:
                saves = saves + "l"
            if not _self.f_motor:
                saving = False
            else:
                saves = saves + "m"
            if not _self.f_temp:
                saving = False
            else:
                saves = saves + "t"
            if saving:
                _self.ui.btnSaving.setText("saving: "+saves)
                _self.ui.btnSaving.setStyleSheet('QPushButton {color: green}')
            else:
                _self.ui.btnSaving.setText("idle: "+saves)
                _self.ui.btnSaving.setStyleSheet('QPushButton {color: grey}')
        except Exception,e:
            log("Problem setting saving button color",e)
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
                
        # limit range
        interval = max(100, min(interval, 10000))
        _self.timer_display.setInterval(interval)
        
        # amplifier progressbars
        _self.ui.progA.setValue(_self.data["femto_channela"][-1]*20+20)
        _self.ui.progB.setValue(_self.data["femto_channelb"][-1]*20+20)
        
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
            _self.ui.cw1.plot.do_autoscale()
        except Exception,e:
            log("Displaying Voltage/Current",e)
        
        
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
            _self.data_curve6.set_data(temp_x, _self.data["temp1"][x0:x1:step])
            _self.data_curve6b.set_data(temp_x, _self.data["temp2"][x0:x1:step]) 
            _self.ui.cw3.plot.do_autoscale()
            
            x0 = find_min(_self.data["ips_timestamp"],begin)
            x1 = find_min(_self.data["ips_timestamp"],end)
                            
            ips_x = np.array(_self.data["ips_timestamp"][x0:x1:step])-_self._start_time
            _self.data_curve5.set_data(ips_x, _self.data["ips_mfield"][x0:x1:step])
            
            _self.ui.cw3.plot.do_autoscale()
        except Exception,e:
            log("Displaying IPS+TEMP",e)
        
        # 7 + 8  
        try:
            if len((_self.data["agilent_voltage_timestamp"])) > 2 and len((_self.data["agilent_current_timestamp"])) > 2 :
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
                    
                if _self.ui.checkViewConductance.isChecked():
                    try:
                        g_y = 12900.0/r_y
                        _self.data_curve8.set_data(resistance_x, g_y)
                    except Exception,e:
                        log("Conductance calculation failed",e)
                        _self.data_curve8.set_data([0,1,2],[1,5,2])
                else:
                    _self.data_curve8.set_data([],[])
                    
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
            _self.ui.tableWidget.setItem(i,0,QtGui.QTableWidgetItem(str(round(item[1],5))))
            i = i + 1
        #_self.ui.tableWidget.column
    except Exception,e:
        log("Error updating data table",e)