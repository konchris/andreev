# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 16:55:31 2013
Old data aquisition and saving run_andreev
@author: David Weber
"""
        """self.data["time"] = []
        self.data["bias"] = []
        self.data["voltage"] = []
        self.data["current"] = []
        self.data["real_pos"] = []
        self.data["speed"] = []
        self.data["motor_current"] = []
        self.data["temperature1"] = []
        self.data["temperature2"] = []
        self.data["magnet"] = []
        
        self.data["li_v_1_x"] = []
        self.data["li_v_1_y"] = []
        self.data["li_v_2_x"] = []
        self.data["li_v_2_y"] = []
        
        self.data["li_i_1_x"] = []
        self.data["li_i_1_y"] = []
        self.data["li_i_2_x"] = []
        self.data["li_i_2_y"] = []"""

"""try:
                voltage = DEV.agilent_old.measurement()
            except:
                voltage = -1
            try:
                current = DEV.agilent_new.measurement()
            except:
                current = -1
            try:
                real_pos = DEV.motor.get_real_pos()
                speed = DEV.motor.get_velocity()
                motor_current = DEV.motor.get_current()
            except:
                real_pos = -1
                speed = -1
                motor_current = -1
            try:
                temperature1 = DEV.neocera.get_temperature(1)
                temperature2 = DEV.neocera.get_temperature(2)
            except:
                temperature1 = -1
                temperature2 = -1
            try:
                magnet = DEV.magnet.ReadField()
            except:
                magnet = -1
            try:
                bias = DEV.yoko.get_voltage()
            except:
                bias = -1
            
            self.data["time"].append(time.time()-self._start_time)
            self.data["bias"].append(bias)
            self.data["voltage"].append(voltage)
            self.data["current"].append(current)
            
            self.data["real_pos"].append(real_pos)
            self.data["speed"].append(speed)
            self.data["motor_current"].append(motor_current)
            self.data["temperature1"].append(temperature1)
            self.data["temperature2"].append(temperature2)
            self.data["magnet"].append(magnet)

            
            #lockin_data = DEV.lockin.read()
            lockin_data = [[0,0],[0,0],[0,0],[0,0]]
            self.data["li_v_1_x"].append(lockin_data[0][0])
            self.data["li_v_1_y"].append(lockin_data[0][1])
            self.data["li_v_2_x"].append(lockin_data[1][0])
            self.data["li_v_2_y"].append(lockin_data[1][1])
            
            self.data["li_i_1_x"].append(lockin_data[2][0])
            self.data["li_i_1_y"].append(lockin_data[2][1])
            self.data["li_i_2_x"].append(lockin_data[3][0])
            self.data["li_i_2_y"].append(lockin_data[3][1])
            """
            
                        """data = []
            for k,v in self.data.items():
                data.append([str(k),v[-1]])
            data = sorted(data, key=lambda v: v[0])
            
            if not self.f == None:
                for k,v in data:
                    self.f.write("%e\t"%(v))
                self.f.write("\n")"""




### MATPLOTLIB

        """self.plot1 = mpl.MyMplCanvas(None, width=10, height=8, dpi=50)
        self.plot1b = self.plot1.axes.twinx()
        self.plot2 = mpl.MyMplCanvas(None, width=10, height=8, dpi=50)
        self.plot2b = self.plot2.axes.twinx()
        
        self.ui.plots1.addWidget(self.plot1)
        self.ui.plots1.addWidget(self.plot2)
        
        self.plot3 = mpl.MyMplCanvas(None, width=10, height=8, dpi=50)
        self.plot3b = self.plot3.axes.twinx()
        self.plot4 = mpl.MyMplCanvas(None, width=10, height=8, dpi=50)
        self.plot4b = self.plot4.axes.twinx()
     
        self.ui.plots2.addWidget(self.plot3)
        self.ui.plots2.addWidget(self.plot4)"""