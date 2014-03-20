# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 09:04:09 2013
Measurement Thread with interpolation in time
@author: David Weber
"""

def measurement_thread(self):
        """This thread is measuring data all time"""
        self.data = {}

        self.data["timestamp"] = []
        self.data["aux0"] = []
        self.data["aux1"] = []
        self.data["li_0_x"] = []
        self.data["li_1_x"] = []
        self.data["li_3_x"] = []
        self.data["li_4_x"] = []
        
        self.data["li_0_y"] = []
        self.data["li_1_y"] = []
        self.data["li_3_y"] = []
        self.data["li_4_y"] = []
        
        self.data["pos"] = []
        self.data["cur"] = []
        self.data["vel"] = []
        
        self.data["temp1"] = []
        self.data["temp2"] = []
        
        self.data["mfield"] = []
        
        self.data["channela"] = []
        self.data["channelb"] = []
        

        while not self.stop:
            try:
                lockin_data = DEV.lockin.get_data_list()
                
                average_samples = int(self.ui.editAverage.text())
                
                li_timestamp = functions.average_chunks(lockin_data["0"]["timestamp"],average_samples)
                li_auxin0 = functions.average_chunks(lockin_data["0"]["auxin0"],average_samples)
                li_auxin1 = functions.average_chunks(lockin_data["0"]["auxin1"],average_samples)
                li_0_x = functions.average_chunks(lockin_data["0"]["x"],average_samples)
                li_1_x = functions.average_chunks(lockin_data["1"]["x"],average_samples)
                li_3_x = functions.average_chunks(lockin_data["3"]["x"],average_samples)
                li_4_x = functions.average_chunks(lockin_data["4"]["x"],average_samples)
                li_0_y = functions.average_chunks(lockin_data["0"]["y"],average_samples)
                li_1_y = functions.average_chunks(lockin_data["1"]["y"],average_samples)
                li_3_y = functions.average_chunks(lockin_data["3"]["y"],average_samples)
                li_4_y = functions.average_chunks(lockin_data["4"]["y"],average_samples)
                
                try:
                    motor_data = DEV.motor.get_data_list()    
                    motor_pos = np.interp(li_timestamp, motor_data["timestamp"], motor_data["position"],motor_data["position"][0],motor_data["position"][-1])
                    motor_cur = np.interp(li_timestamp, motor_data["timestamp"], motor_data["current"],motor_data["current"][0],motor_data["current"][-1])
                    motor_vel = np.interp(li_timestamp, motor_data["timestamp"], motor_data["velocity"],motor_data["velocity"][0],motor_data["velocity"][-1])
                except Exception,e:
                    motor_pos = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),-1,-1)
                    motor_cur = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),-1,-1)
                    motor_vel = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),-1,-1)
                    functions.log("Motor failed DAQ",e)

                try:
                    temp_data = DEV.lakeshore.get_data_list()
                    temp_1 = np.interp(li_timestamp, temp_data["timestamp"], temp_data["temperature1"],temp_data["temperature1"][0],temp_data["temperature1"][-1])
                    temp_2 = np.interp(li_timestamp, temp_data["timestamp"], temp_data["temperature2"],temp_data["temperature2"][0],temp_data["temperature2"][-1])
                except Exception,e:
                    temp_1 = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),-1,-1)
                    temp_2 = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),-1,-1)
                    functions.log("Temperature failed DAQ",e)

                try:
                    magnet_data = DEV.magnet.get_data_list()
                    magnet_field = np.interp(li_timestamp, magnet_data["timestamp"], magnet_data["field"],magnet_data["field"][0],magnet_data["field"][-1])
                except Exception,e:
                    magnet_field = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),-1,-1)
                    functions.log("Magnet failed DAQ",e)
                
                try:
                    femto_data = DEV.femto.get_data_list()
                    channela = np.interp(li_timestamp, femto_data["timestamp"], femto_data["channela"],femto_data["channela"][0],femto_data["channela"][-1])
                    channelb = np.interp(li_timestamp, femto_data["timestamp"], femto_data["channelb"],femto_data["channelb"][0],femto_data["channelb"][-1])
                except Exception,e:
                    channela = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),0,0)
                    channelb = np.interp(li_timestamp, li_timestamp, np.zeros_like(li_timestamp),0,0)
                    functions.log("Magnet failed DAQ",e) 

                self.data["timestamp"].extend(li_timestamp)
                self.data["aux0"].extend(li_auxin0)
                self.data["aux1"].extend(li_auxin1)
                self.data["li_0_x"].extend(li_0_x)
                self.data["li_1_x"].extend(li_1_x)
                self.data["li_3_x"].extend(li_3_x)
                self.data["li_4_x"].extend(li_4_x)
                
                self.data["li_0_y"].extend(li_0_y)
                self.data["li_1_y"].extend(li_1_y)
                self.data["li_3_y"].extend(li_3_y)
                self.data["li_4_y"].extend(li_4_y)
                
                self.data["pos"].extend(motor_pos)
                self.data["cur"].extend(motor_cur)
                self.data["vel"].extend(motor_vel)
                
                self.data["temp1"].extend(temp_1)
                self.data["temp2"].extend(temp_2)
                
                self.data["mfield"].extend(magnet_field)
                
                self.data["channela"].extend(channela)
                self.data["channelb"].extend(channelb)
            
                self.ui.labSample.setText(str(len(self.data["timestamp"])))
                
                if not self.f == None:
                    saving_data = [li_timestamp,li_auxin0,li_auxin1,li_0_x,li_1_x,li_3_x,li_4_x,li_0_y,li_1_y,li_3_y,li_4_y,motor_pos,motor_cur,motor_vel,temp_1,temp_2,magnet_field,channela,channelb]
                    for i in range(len(li_timestamp)):  # for all new data rows
                        line = ""
                        for j in range(len(saving_data)): # for all columns
                            line = line + "%f\t"%(saving_data[j][i])
                        line = line + "\n"
                        self.f.write(line)
                
                # shrink dataset
                max_datalength = 1000000
                for k,v in self.data.items():
                    self.data[k] = v[-max_datalength:-1]
                
                if self.ui.checkAutomaticGain.isChecked():
                    if np.abs(self.data["aux0"][-1]) > 8:
                        DEV.femto.decrease_amplification(0)
                    if np.abs(self.data["aux1"][-1]) > 8:
                        DEV.femto.decrease_amplification(1)
                    if np.abs(self.data["aux0"][-1]) < 0.2:
                        DEV.femto.increase_amplification(0)
                    if np.abs(self.data["aux1"][-1]) < 0.2:
                        DEV.femto.increase_amplification(1)
                    
                        
            except Exception,e:
                functions.log("Error while handling DAQ",e)

            time.sleep(0.2)