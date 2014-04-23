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
        self.volume_list = []
        self.start_time = time.time()
        self.volume_time = []
        
        self.timer_update = 2
        self.flow_range = 30
        
        from guiqwt.builder import make
        self.data_volume = make.curve([],[])
        self.data_flow = make.curve([],[], yaxis="right", color="b")
        self.ui.curvewidget.plot.set_axis_title(self.ui.curvewidget.plot.Y_LEFT, "Volume (L)")
        self.ui.curvewidget.plot.set_axis_title(self.ui.curvewidget.plot.Y_RIGHT, "Flow (L)")
        self.ui.curvewidget.plot.add_item(self.data_volume)
        self.ui.curvewidget.plot.add_item(self.data_flow)
        
        self.timer_display = QTimer()
        self.timer_display.timeout.connect(self.refresh_display)
        self.timer_display.start(self.timer_update * 1000)
        
        self.arduino = ARDUINO()


    def refresh_display(self):
        self.volume += self.arduino.read_volume()
        self.ui.labelVolume.setText("%i L"%(self.volume))
        
        self.volume_time.append(time.time())
        self.volume_list.append(self.volume)
        
        try:
            min_items = int(self.flow_range / self.timer_update)
            if len(self.volume_list) > min_items+1:
                p = np.polyfit(np.array(self.volume_time)[-min_items:-1]-self.start_time,self.volume_list[-min_items:-1],1)
                self.ui.labelFlow.setText("%2.2f LLHe/h"%(p[0]*3600/750))
            else:
                self.ui.labelFlow.setText("")
        except Exception, e:
            functions.log("Failed Calculating Flow",e)
            
        
        self.data_volume.set_data(np.array(self.volume_time)-self.start_time,self.volume_list)
        self.ui.curvewidget.plot.do_autoscale()
        
        self.flow_range = int(self.ui.editRange.text())
        self.timer_update = float(self.ui.editRefresh.text())
        self.timer_display.setInterval(int(self.timer_update * 1000))
        
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
            functions.log("Exiting")
        except Exception,e:
            print e
        event.accept()
        #else:
        #    event.ignore()
            
            
class ARDUINO:
    def __init__(self):
        #self.motor=serial.Serial('COM1',115200,timeout=0) 
        self.arduino=visa.SerialInstrument("ASRL5",delay=0.10,term_chars='\n',timeout=0.2,baud_rate=115200)
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
            
myapp = None     
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = main_program()
    myapp.show()

    sys.exit(app.exec_())