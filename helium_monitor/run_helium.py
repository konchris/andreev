# -*- coding: utf-8 -*-
"""
All rights reserved by David Weber
@author: David Weber
"""

import sys
import os
from PyQt4 import QtCore, QtGui
from gui_helium import Ui_MainWindow
#import devices_andreev as DEV

import thread
import time  
import numpy as np
import functions
import visa

from guidata.qt.QtCore import QTimer#,SIGNAL

class main_program(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        QtCore.QObject.connect(self.ui.btnSetVolume, QtCore.SIGNAL("clicked()"), self.set_volume)
        QtCore.QObject.connect(self.ui.btnHe, QtCore.SIGNAL("clicked()"), self.he_fast)
        QtCore.QObject.connect(self.ui.btnN2, QtCore.SIGNAL("clicked()"), self.n2_fast)
        QtCore.QObject.connect(self.ui.btnZzz, QtCore.SIGNAL("clicked()"), self.he_slow)
               
        #Read all the saved default values 
        try:
            functions.read_config(self.ui)
        except Exception,e:
            print e            
            functions.log("Can't read config file")
            
        try:
            self.volume = int(self.ui.editSetVolume.text())
        except:
            self.volume = 0
        
        self.start_time = time.time()
        self.level = 0
        
        try:
            
            npzfile = np.load("volume_data.npz")
            self.volume_list = list(npzfile["volume_list"])
            self.volume_time = list(npzfile["volume_time"])
            self.level_list = list(npzfile["level_list"])
        except Exception,e:
            self.volume_time = []
            self.volume_list = []
            self.level_list = []
            functions.log("Loading Volume failed",e)
        self.volume_time = []
        self.volume_list = []
        self.level_list = []
        
        self.timer_update = 2
        self.flow_range = 30
        
        from guiqwt.builder import make
        self.data_volume = make.curve([],[])
        self.data_flow = make.curve([],[], yaxis="right", color="b")
        self.data_level = make.curve([],[])
        self.ui.curvewidget.plot.set_axis_title(self.ui.curvewidget.plot.X_BOTTOM, "Time (s)")
        self.ui.curvewidget.plot.set_axis_title(self.ui.curvewidget.plot.Y_LEFT, "Volume (LHeGas)")
        self.ui.curvewidget.plot.set_axis_title(self.ui.curvewidget.plot.Y_RIGHT, "Flow (LLHe/h)")
        self.ui.curvewidget_2.plot.set_axis_title(self.ui.curvewidget.plot.X_BOTTOM, "Time (s)")
        self.ui.curvewidget_2.plot.set_axis_title(self.ui.curvewidget.plot.Y_LEFT, "Level (mm)")
        self.ui.curvewidget.plot.add_item(self.data_volume)
        self.ui.curvewidget.plot.add_item(self.data_flow)
        self.ui.curvewidget_2.plot.add_item(self.data_level)
        self.ui.curvewidget.plot.enable_used_axes()
        self.ui.curvewidget_2.plot.enable_used_axes()
        
        self.timer_display = QTimer()
        self.timer_autosave = QTimer()
        self.timer_display.timeout.connect(self.refresh_display)
        self.timer_display.timeout.connect(self.autosave)
        self.timer_display.start(1000)
        self.timer_autosave.start(60*1000)
        
        self.arduino = ARDUINO()
        try:
            self.levelmeter = TWICKENHAM()
        except Exception,e:
            self.levelmeter = None
            functions.log("TWICKENHAM",e)
        if not self.levelmeter == None:
            try:
                self.levelmeter = ILM210()
            except:
                self.levelmeter = None
                functions.log("ILM210",e)
        
        
    def level_to_liter(self, level=None):
        """returns a linear interpolation of the level"""
        if level == None:
            level = self.level
        return level/3.44+20
    
    def he_fast(self):
        self.levelmeter.set_probe(0)
        self.levelmeter.set_speed(2)
    def he_slow(self):
        self.levelmeter.set_probe(0)
        self.levelmeter.set_speed(1)
    def n2_fast(self):
        self.levelmeter.set_probe(1)
        self.levelmeter.set_speed(2)


    def refresh_display(self):
        try:
            adding_volume = self.arduino.read_volume()
            self.volume += adding_volume
            self.ui.labelVolume.setText("%i L"%(self.volume))
        except Exception,e:
            functions.log("Failed to update Volume",e)
        
        if not self.levelmeter == None:
            try:
                #self.level = self.levelmeter.read_volume()
                print self.level
                self.ui.labelLevelMeter.setText("%i mm"%(self.level)) 
                self.ui.labelLevelMeter_2.setText("%2.1f L"%(self.level_to_liter())) 
            except Exception,e:
                functions.log("Failed to update Level",e)
        else:
            self.level = 0
            self.ui.labelLevelMeter.setText("%i mm"%(self.level)) 
            self.ui.labelLevelMeter_2.setText("%2.1f L"%(self.level_to_liter())) 
            
        
        if adding_volume > 0.01: 
            self.volume_time.append(time.time())
            self.volume_list.append(self.volume)
            self.level_list.append(self.level)
        
        try:
            min_items = int(self.flow_range / self.timer_update)
            if len(self.volume_list) > min_items+1:
                p = np.polyfit(np.array(self.volume_time[-min_items:-1])-self.start_time,self.volume_list[-min_items:-1],1)
                self.ui.labelFlow.setText("%2.2f LLHe/h"%(p[0]*3600.0/757.0))
            else:
                self.ui.labelFlow.setText("")
            
            i = len(self.volume_list)-1
            flow = []
            flow_time = []
            while i > min_items+1:
                p = np.polyfit(np.array(self.volume_time[i-min_items:i])-self.start_time, self.volume_list[i-min_items:i], 1)
                if p[0] > 0:
                    flow.append(p[0]*3600.0/757.0)            
                    flow_time.append(self.volume_time[i-min_items/2])
                
                i -= min_items/2
            self.data_flow.set_data(np.array(flow_time)-self.start_time,flow)
        except Exception, e:
            functions.log("Failed Calculating Flow",e)           
        
        self.data_volume.set_data(np.array(self.volume_time)-self.start_time,self.volume_list)
        self.ui.curvewidget.plot.do_autoscale()
        self.data_level.set_data(np.array(self.volume_time)-self.start_time,self.level_list)
        self.ui.curvewidget_2.plot.do_autoscale()
        
        self.flow_range = int(self.ui.editRange.text())
        self.timer_update = float(self.ui.editRefresh.text())
        self.timer_display.setInterval(int(self.timer_update * 1000))
        
    def autosave(self):
        try:
            np.savez("volume_data", volume_list=self.volume_list, volume_time=self.volume_time)
        except Exception,e:
            functions.log("Saving Volume failed",e)
        
        functions.write_config(self.ui)
        functions.export_html(self.ui,"C:\wamp\www\helium\\")
    
    
    def set_volume(self):
        try:
            self.volume = int(self.ui.editSetVolume.text())
        except Exception,e:
            functions.log("Failed to set Volume",e)

            
    def closeEvent(self, event):
        '''Ask before closing'''
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        try:
            self.ui.editSetVolume.setText(str(self.volume))
            functions.write_config(self.ui)
            try:
                np.savez("volume_data", volume_list=self.volume_list, volume_time=self.volume_time, level_list=self.level_list)
            except Exception,e:
                functions.log("Saving Data failed",e)
            functions.log("Exiting")
        except Exception,e:
            print e
        event.accept()
        #else:
        #    event.ignore()
            
            
class ARDUINO:
    def __init__(self):
        #self.motor=serial.Serial('COM1',115200,timeout=0) 
        self.arduino=visa.SerialInstrument("ASRL5",delay=0.01,term_chars='\n',timeout=0.2,baud_rate=115200)
        self.arduino.clear()

    def initialize(self):
        """init arduino"""
        pass

    def read_volume(self):
        try:
            answer = self.arduino.ask("R")
            answer = int(answer)
        except Exception,e:
            answer = 0
            print ("Arduino Error while gathering Volume",e)
        return answer

class TWICKENHAM:
    def __init__(self):
        #self.motor=serial.Serial('COM1',115200,timeout=0) 
        self.twickenham=visa.SerialInstrument("ASRL7",delay=0.01,term_chars='\r\n',timeout=0.2,baud_rate=9600)
        self.twickenham.clear()

    def initialize(self):
        """init arduino"""
        pass

    def set_probe(self, mode=0):
        """Sets the reading mode 0=A, 1=B"""
        try:
            self.twickenham.ask("P%i"%mode)
        except Exception,e:
            print e
            
    def set_speed(self, mode=0):
        """0=Standby,1=Slow,2=Fast,3=Continuous"""
        try:
            self.twickenham.ask("M%i"%mode)
        except Exception,e:
            print e

    def read_volume(self):
        try:
            answer = self.twickenham.ask("G")
            answer = int(answer[3:6])
        except Exception,e:
            answer = 0
            print ("Twickenham Error while gathering Volume",e)
        return answer

class ILM210:
    def __init__(self, port='ASRL7', address='6'):
        #self.meter=serial.Serial('COM3',9600,timeout=0) 
        self.meter=visa.SerialInstrument(port,delay=0,term_chars='\r\n')
        self.address = address
        #thread.start_new_thread(self.motor_thread,(0.1,))
    
    def read_volume(self):
        """stop motor and deactivate motor control"""
        answer = self.meter.ask('@'+self.address+'R1')
        # answer: R+00588
        try:
            return float(answer[2:])/10
        except Exception,e:
            print e
            return 0
            
    def version(self):
        """stop motor and deactivate motor control"""
        answer = self.meter.ask('@'+self.address+'V')
        return answer
        
    def close(self):
        self.meter.close()
            
myapp = None     
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = main_program()
    myapp.show()

    sys.exit(app.exec_())