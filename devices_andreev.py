# -*- coding: latin1 -*-
"""
Some parts copyright by David Weber
@author: David Weber
"""
import config
import visa
import numpy as np
import time
from functions import log
import config
#import luci
#import struct   # ascii to single/double
import thread
#import threading
#from nidaqmx import AnalogInputTask
# ZURICH INSTRUMENTS
import zhinst.ziPython, zhinst.utils
#import matplotlib as mpl

# stops all threads
stop = False
app = None

gpib_lock = thread.allocate_lock()
try:
    board_0 = visa.Gpib(0)
    board_0.send_ifc()
except Exception,e:
    log("Failed to Clear Interface 0",e)
try:
    board_0 = visa.Gpib(1)
    board_0.send_ifc()
except Exception,e:
    log("Failed to Clear Interface 1",e)


def collect_garbage():
    import gc
    gc.collect()

    
class Magnet:
    def __init__(self, GPIB_No=27):
        self.magnet=visa.instrument('GPIB0::%i'%GPIB_No, delay=0.0, term_chars='\r', timeout=0.2)#VI_EXCLUSIVE_LOCK
        self.magnet.clear()
        self.rate=0.1
        self.max_rate=2
        self.goto_field = 0
        self.actual_field = 0

        self.status_a = 0
        self.status_b = 0
        self.activity = 0
        self.local = 0
        self.heater = False
        
        self.data = {}
        self.data_lock = thread.allocate_lock()
        self.data["timestamp"] = []
        self.data["field"] = []
        
        self.thread_id = None
        self.start_thread()

    def start_thread(self, delay=0.2):
        if self.thread_id != None:
            self._stop = True                # send stop to thread
            _timeout = time.time()+1        # timeout = 1s
            # check if thread exited or timeout occured
            while self.thread_id != None and time.time() < _timeout:
                pass
        self._stop = False                   # reset terminate signal
        # create new thread and insert id
        self.thread_id = thread.start_new_thread(self.measurement_thread,(delay,))
        log("Thread #%i started"%(self.thread_id))

    def initialize(self):
        try:
            gpib_lock.acquire()
            self.magnet.write('$C3')     #remote & unlocked        
            time.sleep(0.1)
            self.magnet.write('$Q4')     #four digits extended resolution            
            self.magnet.write('$M1')     #set mode, units "tesla", fast   
            time.sleep(0.1)
            if not self.heater == None:
                self.magnet.write('$H1')     #switch heater on
                time.sleep(0.1)
                self.heater=True
                print('Magnet Initializing...Please Wait 20s')
                for i in range (40):
                    time.sleep(0.5)
                    try:
                        app.processEvents()
                    except:
                        pass
            self.magnet.write('$A0')     #hold operation
            return True 
        except Exception,e:
            log('ERROR: magnet initialization failed',e)
            return False
        finally:
            gpib_lock.release()

    def ZeroField(self, rate=0.1):
        self.goto_field = 0
        if rate > self.max_rate:
            rate = self.max_rate
        try:            
            self.magnet.write('$T%f'%rate)
            time.sleep(0.1)
            self.magnet.write('$A2')
            print('Magnet Goto Zero...OK')
        except:
            print('ERROR: Magnet Goto Zero Failed')
            return False
    
    def ReadStatus(self):
        """Saves the Status of the magnet to local variables."""        
        try:
            answer = self.magnet.ask('X')
            if answer[0] == "X":
                self.status_a = int(answer[1])
                self.status_b = int(answer[2])
                self.activity = int(answer[4])
                self.local = int(answer[6])
                self.heater_status = int(answer[8])
                
                if self.heater_status==1:
                    self.heater = True
                else:
                    self.heater = False
            else:
                raise ValueError("Not a valid Status Answer!")
        except Exception,e:
            print answer
            log("Magnet Status Error",e)
            
            
    def ReturnStatus(self, verbal=False):
        """Returns strings if True."""
        Xm = {0: "Normal", 1: "Quenched", 2: "Over Heated", 4: "Warming Up", 8: "Fault"}
        Xn = {0: "Normal", 1: "On Positive Voltage Limit", 2: "On Negative Voltage Limit",\
                4: "Outside Negative Current Limit", 8: "Outside Positive Current Limit"}
        An = {0: "Hold", 1: "To Set Point", 2: "To Zero", 4: "Clamped"}
        Cn = {0: "Local&Locked", 1: "Remote&Locked", 2: "Local&Unlocked", 3: "Remote&Unlocked",\
                4: "Auto-Run-Down", 5: "Auto-Run-Down", 6: "Auto-Run-Down", 7: "Auto-Run-Down"}
        Hn = {0: "Off Magnet at Zero", 1: "On", 2: "Off Magnet at Field", 5: "Heater Fault",\
                8: "No Switch Fitted"}    
        
        if verbal:
            return {"status_a": Xm[self.status_a], "status_b": Xn[self.status_b], \
                    "activity": An[self.activity], "local": Cn[self.local],\
                    "heater": Hn[self.heater_status]}
        else:
            return {"status_a": self.status_a, "status_b": self.status_b, \
                    "activity": self.activity, "local": self.local,\
                    "heater": self.heater_status}
                    
    def ReadField(self):
        return self.actual_field       

    def SetField(self, target=0.0, rate=0.1, verbal=True): 
        if rate > self.max_rate:
            rate = self.max_rate
        if not rate is None:
            self.rate=rate
        try:
            self.goto_field = target
            self.magnet.write('$J%f'%target)
            self.magnet.write('$T%f'%self.rate)
            self.magnet.write('$A1')
            if verbal:
                print 'Field Set to %f...OK'%(target)
            #sleep(0.2)
        except:
            print('ERROR: Set B field failed')
    
    def field_reached(self):
        """ returns True if the desired field is already reached
            returns False if not"""
        try:
            if abs(self.actual_field - self.goto_field) < 0.0001:
                return True
            else:
                return False
        except Exception,e:
            log("Couldn't determine if field reached!",e)
            return False

    def set_switchheater(self, value='ON'):
        """set switch heater 'ON', 'OFF' or 'zeroOFF'"""
        settings={'zeroOFF':0, 'ON':1, 'OFF':2}
        if value in settings.keys():
            self.magnet.write('$H%s'%str(settings[value]))
            print '$H%s'%str(settings[value])
            if value in ['OFF', 'zeroOFF'] and self.heater==True:
                log('Wait for switch heater....Cooldown',force=True)
                for i in range (40):
                    time.sleep(0.5)
                    app.processEvents()
                self.heater=False
            elif value in ['ON'] and self.heater==False:
                log('Wait for switch heater....Warming',force=True)
                for i in range (40):
                    time.sleep(0.5)
                    app.processEvents()
                self.heater=True
        else:
            print('switch heater: invalid setting')

# data handling
    def get_data_list(self, erase=True):
        """returns all the gathered data in one bunch
        and erases the list """       
        # get lock first
        self.data_lock.acquire()
        # copy data
        return_data = self.data.copy()

        if erase:    
            self.data["timestamp"] = []
            self.data["field"] = []
        # release lock
        self.data_lock.release()
        return return_data

    def measurement_thread(self, delay=0.1):
        log("Magnet Thread started!")
        while not (self._stop or stop):
            try:
                gpib_lock.acquire()
                #self.magnet.clear()
                try:
                    answer = self.magnet.ask('R7')
                    self.actual_field = float(answer[1:])
                    self.ReadStatus()
                except Exception,e:
                    self.actual_field=11
                    log("Field Aquire Failed",e)
                    self.magnet.clear()
            except Exception,e:
                
                log("Magnet Thread Acquire Failed",e)
            finally:
                gpib_lock.release()

            # append gathered data to internal data dictionary
            self.data_lock.acquire()
            self.data["timestamp"].append(time.time())
            self.data["field"].append(self.actual_field)
            self.data_lock.release()
            
            time.sleep(delay)
        # indicate that thread terminated 
        log("Thread #%i finished"%(self.thread_id))
        self.thread_id = None


        
class LAKESHORE:
    def __init__(self,GPIB_No=12, label="Lakeshore 336"):
        self.lakeshore=visa.instrument("GPIB0::%i"%(GPIB_No), timeout=0.1, term_chars="\r\n")
        #self.initialize()
        
        self.data = {}
        self.data_lock = thread.allocate_lock()
        self.data["timestamp"] = []
        self.data["temperature1"] = []
        self.data["temperature2"] = []
        self.data["sensor1"] = []
        self.data["sensor2"] = []
        
        self.thread_id = None
        self.start_thread()

    def start_thread(self, delay=0.05):
        if self.thread_id != None:
            self._stop = True                # send stop to thread
            _timeout = time.time()+1        # timeout = 1s
            # check if thread exited or timeout occured
            while self.thread_id != None and time.time() < _timeout:
                pass
        self._stop = False                   # reset terminate signal
        # create new thread and insert id
        self.thread_id = thread.start_new_thread(self.measurement_thread,(delay,))
        log("Thread #%i started"%(self.thread_id))
        

    def initialize(self):
        """Initializes the device by reading all the values"""
        self.reset()
        self.get_temperature()
        self.get_setpoint()
        self.get_heater_range()
        
    
    def reset(self):
        """Sends Reset-Command"""
        self.lakeshore.write('*RST')
        log('RESET: '+self.lakeshore.ask("*IDN?"))
    
    def clear(self):
        """Clears the interface"""
        self.lakeshore.write('*CLS')
    
    def get_temperature(self, channel="A"):
        """Asks for the temperature of sample of channel A oder B"""
        return self.data["temperature1"][-1]
    
    def get_setpoint(self):
        """Gets the setpoint"""
        try:
            gpib_lock.acquire()
            self.setpoint = self.lakeshore.ask('SETP? 1')
        except Exception,e:
            log("Failed to acquire setpoint",e)
        finally:
            gpib_lock.release()
        return self.setpoint
    
    def set_setpoint(self, temperature=4):
        """Sets the new setpoint"""
        self.setpoint = temperature
        try:
            gpib_lock.acquire()
            self.lakeshore.write('SETP 1,%f'%(temperature))
        except Exception,e:
            log("Failed to set setpoint",e)
        finally:
            gpib_lock.release()
        
    def set_heater_range(self, _range=0):
        """Set the heater range to specified value:
                0 = off
                1 = low
                2 = med
                3 = high"""
        self.heater_range = _range
        #log('RANGE 1,%i;'%(range))
        try:
            gpib_lock.acquire()
            self.lakeshore.write('RANGE 1,%i;'%(_range))
        except Exception,e:
            log("Failed to set heater range",e)
        finally:
            gpib_lock.release()
    
    def set_setpoint_ramp(self, ramp=True, output=1, rate=0.1):
        """Sets the setpoint ramp feature. If turned on, a new setpoint
           is reached by the given ramp rate
           ramp = True or False
           output = 1 or 2
           rate = 0.1 to 100"""
        if ramp:
            ramp = 1 
        else:
            ramp = 0
        try:
            gpib_lock.acquire()
            self.lakeshore.write('RAMP %i,%i,%f;'%(output,ramp,rate))
        except Exception,e:
            log("Failed to set ramp parameter",e)
        finally:
            gpib_lock.release()
        
    
    def get_heater_range(self):
        """Get the heater range, look @ set"""
        try:
            gpib_lock.acquire()
            self.heater_range = self.lakeshore.ask("RANGE?")
        except Exception,e:
            log("Failed to set heater range",e)
        finally:
            gpib_lock.release()
            
        return self.heater_range
    
    def set_pid(self,p=100,i=10,d=0):
        """sets pid parameter and switches to manual pid for loop 1"""
        try:
            gpib_lock.acquire()       
            self.lakeshore.write('CMODE 1,1')
            #log('PID 1,%i,%i,%i'%(p,i,d))
            self.lakeshore.write('PID 1,%i,%i,%i'%(p,i,d))
        except Exception,e:
            log("Failed to set pid",e)
        finally:
            gpib_lock.release() 
    
    def set_display(self,mode=0):
        """Display Setup Command"""        
        command = 'DISPLAY %i'%(mode)
        try:
            gpib_lock.acquire()
            self.lakeshore.write(command)
        except Exception,e:
            log("Failed to set display",e)
        finally:
            gpib_lock.release()
    
    def set_display_field(self,field=1,source=0,unit=0):
        """sets display field"""        
        command = 'DISPFLD %i,%i,%i'%(field,source,unit)
        #log(command)
        try:
            gpib_lock.acquire()
            self.lakeshore.write(command)
        except Exception,e:
            log("Failed to set display field",e)
        finally:
            gpib_lock.release()

    
    # data handling
    def get_data_list(self, erase=True):
        """returns all the gathered data in one bunch
        and erases the list """       
        # get lock first
        self.data_lock.acquire()
        # copy data
        return_data = self.data.copy()

        if erase:    
            self.data["timestamp"] = []
            self.data["temperature1"] = []
            self.data["temperature2"] = []
            self.data["sensor1"] = []
            self.data["sensor2"] = []
        # release lock
        self.data_lock.release()
        return return_data    
    
    def measurement_thread(self, delay=0.05):
        log("Temperature Thread started!")
        while not (self._stop or stop):
            try:
                gpib_lock.acquire()
                temperature1 = float(self.lakeshore.ask('KRDG? A'))            
                temperature2 = float(self.lakeshore.ask('KRDG? B'))
                #sensor1 = 0#float(self.lakeshore.ask('SRDG? A'))            
                #sensor2 = 0#float(self.lakeshore.ask('SRDG? B'))
            except Exception,e:
                log("Temperature Aquire Failed",e)
                temperature1 = 0         
                temperature2 = 0
                #sensor1 = 0
                #sensor2 = 0
            finally:
                gpib_lock.release()

            # append gathered data to internal data dictionary
            
            self.data_lock.acquire()
            self.data["timestamp"].append(time.time())
            self.data["temperature1"].append(temperature1)
            self.data["temperature2"].append(temperature2)
            #self.data["sensor1"].append(sensor1)
            #self.data["sensor2"].append(sensor2)
            self.data_lock.release()
            
            time.sleep(delay)
        # indicate that thread terminated 
        log("Thread #%i finished"%(self.thread_id))
        self.thread_id = None
        
    """calibration_ruo2 = np.array([[1280.23, 300.0], [1280.973, 280.0], [1281.822, 260.0], [1282.802, 240.0], [1283.947, 220.0], [1285.305, 200.0], [1286.083, 190.0], [1286.942, 180.0], [1287.894, 170.0], [1288.958, 160.0], [1290.152, 150.0], [1291.505, 140.0], [1293.052, 130.0], [1294.837, 120.0], [1296.923, 110.0], [1299.396, 100.0], [1300.814, 95.0], [1302.378, 90.0], [1304.113, 85.0], [1306.049, 80.0], [1308.225, 75.0], [1310.69, 70.0], [1313.506, 65.0], [1316.758, 60.0], [1320.558, 55.0], [1325.062, 50.0], [1330.493, 45.0], [1337.179, 40.0], [1345.632, 35.0], [1356.685, 30.0], [1362.129, 28.0], [1368.351, 26.0], [1375.535, 24.0], [1383.93, 22.0], [1393.881, 20.0], [1405.878, 18.0], [1420.651, 16.0], [1439.325, 14.0], [1463.742, 12.0], [1497.156, 10.0], [1519.009, 9.0], [1545.916, 8.0], [1579.928, 7.0], [1624.403, 6.0], [1652.253, 5.5], [1725.066, 4.5], [1753.167, 4.2], [1774.075, 4.0], [1803.124, 3.75], [1836.025, 3.5], [1873.622, 3.25], [1917.031, 3.0], [1956.936, 2.8], [2002.539, 2.6], [2055.19, 2.4], [2116.717, 2.2], [2189.645, 2.0], [2231.454, 1.9], [2277.578, 1.8], [2328.744, 1.7], [2385.85, 1.6], [2416.972, 1.55], [2522.709, 1.4], [2605.77, 1.3], [2701.67, 1.2], [2813.734, 1.1]])
    calibration_probe2 = np.array([[104,300],[104.5,280],[105,260],[106,240],[107,220],[108,200],[108.5,190],[109,180],[110,170],[111,160],[112,150],[113,140],[114,130],[116,120],[118,110],[120,100],[121,95],[122,90],[124,85],[126,80],[128,75],[130,70],[132,65],[135,60],[139,55],[144,50],[149,45],[154,40],[162,35],[174,30],[179,28],[184,26],[194,24],[204,22],[214,20],[229,18],[245,16],[273,14],[304,12],[354,10],[394,9],[444,8],[524,7],[629,6],[704,5.5],[954,4.5],[1054,4.2],[1154,4],[1304,3.75],[1504,3.5],[1704,3.25],[2104,3],[2404,2.8],[2954,2.6],[3504,2.4],[4404,2.2],[5654,2],[6804,1.9],[8004,1.8],[10004,1.7],[12404,1.6],[14004,1.55],[20563.86,1.4],[28062.44,1.3],[40143.44,1.2],[60929.16,1.1]])
    for i in range(len(calibration_ruo2)):
        print str(i+1) + " " + str(np.log10(calibration_probe2[i][0])) + " " + str(calibration_probe2[i][1])    """    
class ITC503:
    def __init__(self, gpib_identifier = "GPIB::24", timeout = 1, term_chars = '\r',
                 delay = 0):

        self.itc = visa.GpibInstrument("GPIB::24", timeout=1, term_chars="\r", delay=0)
        self.itc.ask('C3')
        self.itc.clear()
        
    def get_TSorb(self):
        """The temperature on the Sorption pump / K"""
        return self.itc.ask_for_values('R1')[0]
        
    def get_THe3(self):
        """The temperature on the He3-Pot / K"""
        return self.itc.ask_for_values('R2')[0]
        
    def get_T1K(self):
        """The temperature on the 1K-Pot / K"""
        return self.itc.ask_for_values('R3')[0]

    def TSorbSoll(self,TSoll): 
        '''Solltemperatur der Sorb / K'''
        self.itc.write('$T'+str(TSoll))

    def Local(self):
        '''ITC auf Local stellen'''
        self.itc.write('$C2')

    def start_heating(self, temp = 30.0, power = 5.5):
        """Start heating the cryostat (on the sorb).

        Using the heater on the sorption pump you can heat
        the cryostat. This function automates the process.

        Parameters
        ----------
        temp : float, optional
            The end temperature for the heater on the sorption
            pump in K. The default setting is that used for He3
            condensation
            DEFAULT : 30.0
        power : float, optional
            The power of the heater in procent. Defualt setting
            is that used for He3 condensation
            DEFAULT : 5.5

        """
        self.set_heater(1)
        self.set_heater_manual()
        self.turn_off_auto_pid()
        self.set_Set_Temp(temp)
        self.set_heater_output(power * 2.5)

    def set_auto_temp(self):
        """Let the ITC automatically regulate the temperature via PID."""
        self.set_heater_auto()
        self.turn_on_auto_pid()

    def stop_heating(self):
        self.set_heater_manual()
        self.turn_off_auto_pid()
        self.set_heater_output(0.0)
        self.set_Set_Temp(1.5)

    def stop_auto_temp(self):
        """Set temperature control to manual."""
        self.set_heater_manual()
        self.turn_off_auto_pid()

    def set_heater_manual(self):
        self.itc.write('$A0')

    def set_heater_auto(self):
        self.itc.write('$A1')

    def turn_on_auto_pid(self):
        self.itc.write('$L1')

    def turn_off_auto_pid(self):
        self.itc.write('$L0')

    def set_heater(self, Hn = 1):
        """Set the heater sensor for automatic heating. Default is 1, or the Sorb heater.
        
        Parameters
        ----------
        Hn : int
            Set the heater sensor for automatic control.
            1 - Sorption Pump Sensor
            2 - He3 Pot Sensor
            3 - 1K Pot Sensor

        """
        self.write('$H'+str(Hn))

    def set_heater_output(self, Onnn = 5.5):
        """Set the heater output power as a percentage of the maximum power output"""
        self.itc.write('$O'+str(Onnn))

    def set_Set_Temp(self, Tnnnn):
        """Set a set point temperature. ."""
        self.itc.write('$T'+str(Tnnnn))

    def get_sys_status(self):
        self.x_string = self.itc.ask('X')
        
class GS200:
    """ This class manages the communication with the Yokogawa GS200
    
    Parameters
    ----------
    GPIB_No : integer
        Number of the GPIB port the Yokogawa is attached."""
    def __init__(self, GPIB_No=14):
        #self.yoko=visa.instrument('GPIB0::%i'%GPIB_No, delay=0.05, term_chars='\n')
        self.yoko=visa.instrument('USB0::0x0B21::0x0039::91M818122::0::INSTR', delay=0.05, term_chars='\n', timeout=0.2)
        self.initialize()
   
    def initialize(self):
        """get current set point, set default parameters, ranges etc""" 
        self.yoko.write("*CLS") # clear status
        self.set_function("VOLT")
        self.set_limits(0.1,2)
        self.set_voltage(0.001)
        self.output(True)

    def output(self,state=True):
        """defines the state of the voltage output.
        possible: True=ON | False=OFF"""
        if state:
            _state = "ON"
        else:
            _state = "OFF"
        self.yoko.write(":OUTP %s"%(_state))
    
    def get_errors(self):
        i = 10
        while i > 0:
            try:
                answer = self.yoko.ask(":SYST:ERR?")
                print answer
                if answer[0] == "0":
                    i = 0
            except Exception,e:
                print "Yoko no Status Answer"
                print e
            finally:
                i = i-1
    
    def display_set_text(self, text="GS200"):
        """Displays desired text"""
        self.yoko.write(":SYST:DISP:TEXT \"%s\""%(text))
    def display_main_screen(self):
        """Sets Display back to normal"""
        self.yoko.write(":SYST:DISP:NORM")
   
    
    # programs
    def program_set_interval_time(self, _time=0.1):
        """sets the execution time per step"""
        self.yoko.write(":PROG:INT %f"%(_time))
    def program_set_slope_time(self, _time=0.1):
        """sets the execution time per step"""
        self.yoko.write(":PROG:SLOP %f"%(_time))
    def program_set_repeat(self, state="OFF"):
        self.yoko.write(":PROGram:REPeat %s"%(state))
    def program_edit_start(self):
        self.yoko.write(":PROGram:EDIT:STARt")
    def program_edit_end(self):
        self.yoko.write(":PROGram:EDIT:END")
    def program_set_function(self, func="VOLT"):
        """VOLTage or CURRent"""
        self.yoko.write(":SOURce:FUNCtion %s"%(func))
    def program_set_range(self, voltage=1):
        self.yoko.write(":SOURce:RANGe %f"%(voltage))
    def program_set_level_auto(self, voltage=1):
        self.yoko.write(":SOURce:LEVel:AUTO %f"%(voltage))
    def program_start(self):
        self.yoko.write(":PROGram:RUN")
    def program_hold(self):
        self.yoko.write(":PROGram:HOLD")
    def program_is_end(self):
        try:
            status = self.yoko.ask(":STAT:EVEN?")
            if int(status) & (1 << 7): # check if End of Program is set
                return True
            else:
                return False
        except Exception,e:
            log("Yoko program_is_end",e)
            return False
    def program_goto_ramp(self, voltage=0.0, slope_time=1):
        """ramps voltage to given voltage in given time"""
        self.program_set_interval_time(slope_time) 
        self.program_set_slope_time(slope_time) 
        self.program_set_repeat("OFF")      
           
        # edit program
        self.program_edit_start()
        self.program_set_function("VOLT")
        self.program_set_level_auto(voltage)
        self.program_edit_end()
        self.program_is_end()   # clear status register
        time.sleep(0.1)

        # start sweep
        self.program_start() 
    
    
    def set_function(self,function="VOLT"):
        """sets the function of the device.
        possible: VOLT | CURR"""
        self.yoko.write(":SOUR:FUNC %s"%(function))
    
    def set_range(self, value):
        """set appropriate range and level for target value:
        value has to be either voltage or current"""
        self.yoko.write(":SOUR:RANG %f"%(value))
        #self.yoko.write(":SOUR:LEV:AUTO %f"%(value))
    
    def set_limits(self, current=0.005, voltage=2.000):
        """sets the limits for voltage and current"""
        self.yoko.write(":SOUR:PROT:CURR %f"%(current))
        self.yoko.write(":SOUR:PROT:VOLT %f"%(voltage))
    
    def set_voltage(self, value=0):
        """sets the new level in fixed range"""
        #self.yoko.write(":SOUR:LEV:AUTO %f"%(value))
        self.voltage = value
        self.yoko.write(":SOUR:LEV:AUTO %f"%(value))
    
    def get_voltage(self):
        """returns the last set value"""
        return self.voltage

class YOKO7651:
    """ This class manages the communication with the Yokogawa 7651.
    
    Many functions in the class don't do anything, they where simply copied
    from the class 'GS200' and are needed for good working of the whole programm.
    This function only 'pass' and are collected at the end of the class.
    
    Parameters
    ----------
    GPIB_No : integer
        The number on which GPIB port the Yokogawa is attached.
    """
    def __init__(self, GPIB_No=24):
        self.yoko=visa.instrument('GPIB0::%i'%GPIB_No, delay=0.05, term_chars='\n')
        self.ranges={10e-3:'R2', 100e-3:'R3', 1.0:'R4', 10.0:'R5', 30.0:'R6'}
        self.SetPoint=None
        self.status={'prog set':None, 'prog run':None, 'error':None, 'outp unstable':None, 'outp on':None, 'calib mode': None, 'memory card':None, 'CAL switch':None}
        self.byteorder=['CAL switch', 'memory card', 'calib mode', 'outp on', 'outp unstable', 'error', 'prog run', 'prog set']
        self.voltage = 0.0
        self.initialize()
   
    def initialize(self):
        """get current set point, set default parameters, ranges etc"""        
        self.yoko.write('RC')
        self.yoko.write('o1e')
        self.set_voltage(0.001)
    
    def set_range(self, value):
        """set appropriate range for target value"""
        rangevals=np.array(self.ranges.keys())
        rangecomm=self.ranges[min(rangevals[np.where(rangevals>=float(value))])]
        self.yoko.write('%s'%rangecomm)
        self.yoko.write('E')

    def set_voltage(self, U=1.0e-6):
        """define yoko setpoint U in V"""
        voltage_old = self.voltage
        self.voltage=float(U)
        self.yoko.write('S%f'%float(U))
        if voltage_old !=self.voltage:
            print 'Spannung auf %f gesetzt.'%float(U)
        self.yoko.write('E')
    
    def output(self,state=True):
        """defines the state of the voltage output.
        possible: True=ON | False=OFF"""
        if state:
            self.yoko.write("o1e")
        else:
            self.yoko.write("o1e")
   
    def program_is_end(self):
        try:
            status = self.yoko.ask("OC")
            #print status
            if int(status.split("=")[-1]) & (1 << 1): # program being executed
                # 1 = running
                return False
            else:
                return True
        except Exception,e:
            log("Yoko program_is_end",e)
            return False

    def program_goto_ramp(self, voltage=0.0, slope_time=1):
        """Programms the Yokogawa voltage supply so that it ramps from the current
        value of the voltage to a given in a given time.
        
        Parameters
        ----------
        voltage : float
            The voltage to which the yokogawa shoud ramp.
        slope_time : float
            The time in which the yokogawa should ramp to the 'voltage'.
        """
        
        # defining the range of the yokogawa
        Bias_step=[voltage]
        maxbias=max([abs(i) for i in Bias_step])
        rangevals=np.array(self.ranges.keys())
        rangecomm=self.ranges[min(rangevals[np.where(rangevals>=maxbias)])]
        self.yoko.write('%s'%rangecomm)

        #yoko.yoko.write('S%f'%float(Bias_step[-1])) #setpoint -> start sweep at the same where sweep finishes
        self.yoko.write('E')    #trigger
        self.yoko.write('PRS')  #open programming mode
        self.yoko.write('F1')   #set V:DC source
        self.yoko.write('%s'%rangecomm)
        #create program steps
        for i in Bias_step:     #create program steps
            self.yoko.write('S%f'%float(i)) 
            time.sleep(0.1)
        self.yoko.write('PRE')  #end programming mode
        self.yoko.write('PI%f'%float(slope_time))    #set step interval time
        self.yoko.write('E')
        self.yoko.write('SW%f'%float(slope_time))       #set sweep interval time
        self.yoko.write('E') 
        
        self.yoko.write('M1')   #single
        self.yoko.write('E')
        self.yoko.write('RU2')
        
    # Functions with no real function.
    def set_function(self,function="VOLT"):
        """sets the function of the device.
        possible: VOLT | CURR"""
        pass    
    def set_limits(self, current=0.005, voltage=2.000):
        """sets the limits for voltage and current"""
        pass
    def get_voltage(self):
        """returns the last set value"""
        return self.voltage
    def display_set_text(self, text="GS200"):
        """Displays desired text"""
        pass
    def display_main_screen(self):
        """Sets Display back to normal"""
        pass

class Agilent34410A:
    """ This class manages the communication with the Agilent34410A and fetches
    the data from it.
    
    Parameters
    ----------
    label : String
        So far unused?
    dlay : float
        So far unused?
    addr : string
        The exact USB address of this specific Agilent.
    timeout : float
        So far unused?"""
        
    def __init__(self, addr, label="Agilent", dlay=0, timeout=0.2): #GPIB_No=22, 
        """Agilent 34410A"""
        self.label = label
        self.Agilent=visa.instrument(addr)#, delay=dlay,term_chars='\n')
        
        #self.initializeVOLTDC(2)
        #self.initialize4WIREOHM()
        self.initializeVOLTDCarray(2)
        
        self.data = {}
        self.data_lock = thread.allocate_lock()
        self.data["timestamp"] = []
        self.data["voltage"] = []
        
        self.thread_id = None
        self.start_thread()

    def start_thread(self, delay=0.25):
        if self.thread_id != None:
            self._stop = True                # send stop to thread
            _timeout = time.time()+1        # timeout = 1s
            # check if thread exited or timeout occured
            while self.thread_id != None and time.time() < _timeout:
                pass
        self._stop = False                   # reset terminate signal
        # create new thread and insert id
        self.thread_id = thread.start_new_thread(self.measurement_thread,(delay,))
        log("Thread #%i started"%(self.thread_id))

    def initializeVOLTDC(self, NPLC=2, DISPLAY ="ON"):
        self.Agilent.write('*CLS')
        self.Agilent.write('CONF:VOLT:DC 10')
        self.Agilent.write('VOLT:DC:NPLC '+str(NPLC))
        self.Agilent.write('FUNC "VOLT:DC"')
        self.Agilent.write('VOLT:DC:RANG:AUTO ON')

    
    def initialize4WIREOHM(self, NPLC=2, DISPLAY ="ON"):
        self.Agilent.write('FUNC "FRES"')
        self.Agilent.write('FRES:RANG:AUTO ON') # manual range?
        
    def get(self):
        return float(self.Agilent.ask("READ?"))
    
    def get_errors(self):
        i = 10
        while i > 0:
            try:
                answer = self.yoko.ask(":SYST:ERR?")
                print answer
                if answer[0] == "0":
                    i = 0
            except Exception,e:
                print "Yoko no Status Answer"
                print e
            finally:
                i = i-1
    
    def set_nplc(self, NPLC=10):
        self.Agilent.write('VOLT:DC:NPLC '+str(NPLC))
        
    def initializeVOLTDCarray(self, NPLC=2):
        self.Agilent.write('*CLS')
        self.Agilent.write('CONF:VOLT:DC 10')
        self.Agilent.write('VOLT:DC:NPLC '+str(NPLC))
        self.Agilent.write('FUNC "VOLT:DC"')
        self.Agilent.write('VOLT:DC:RANG:AUTO ON')
        self.Agilent.write('TRIG:SOUR IMM')        
        self.Agilent.write('TRIG:COUN 1')        
        self.Agilent.write('SAMP:COUN 20000')
        
    def send_init(self):
        """Sets Instrument to WAIT FOR TRIGGER"""
        self.Agilent.write("INIT")
    
    def stop_measurements(self):
        """Stops measurements and goes to IDLE-state"""
        self.Agilent.write('ABOR')
    
    def get_memory(self):
        """Returns what is in the memory"""
        answer = self.Agilent.ask("R?")
        return answer

        # data handling
    def get_data_list(self, erase=True):
        """returns all the gathered data in one bunch
        and erases the list """       
        # get lock first
        self.data_lock.acquire()
        # copy data
        return_data = self.data.copy()

        if erase:        
            self.data["timestamp"] = []
            self.data["voltage"] = []
        self.data_lock.release()
        return return_data

    # thread
    def measurement_thread(self, delay=0.05):
        log("Agilent Thread started!")
        last_time = time.time() # reset time variable
        self.send_init()    # starts auto triggering
        while not (self._stop or stop):
            try:               
                voltage = self.get_memory()
                                
                voltages = [float(x) for x in voltage[2+int(voltage[1]):].split(",")]
                times = np.linspace(last_time, time.time(), len(voltages), endpoint=False)
                last_time = time.time()
                
                self.data_lock.acquire()
                self.data["timestamp"].extend(times)
                self.data["voltage"].extend(voltages)
                self.data_lock.release()
            except Exception,e:
                self.send_init()
                log("34410a Measurement Thread",e)
                    
            time.sleep(delay)
        # send abort
        self.stop_measurements()
        
        # indicate that thread terminated 
        log("Thread #%i finished"%(self.thread_id))
        self.thread_id = None



class ZURICH:
    def __init__(self):
        # Open connection to ziServer
        self.daq = zhinst.ziPython.ziDAQServer('localhost', 8005)
        self.daq2 = zhinst.ziPython.ziDAQServer('localhost', 8005)
        # Detect device
        self.device = zhinst.utils.autoDetect(self.daq)
        
        self.time_offset = 0.0
        self.resync()
        
        self.initialize()
        self.femto_reset()
        
        self.data = {}
        self.data_lock = thread.allocate_lock()
        self.data["0"] = {}
        self.data["0"]["x"] = []
        self.data["0"]["y"] = []
        self.data["0"]["auxin0"] = []
        self.data["0"]["auxin1"] = []
        self.data["0"]["dio"] = []
        self.data["0"]["timestamp"] = []
        
        self.data["1"] = {}
        self.data["1"]["x"] = []
        self.data["1"]["y"] = []
        self.data["1"]["timestamp"] = []
        
        self.data["3"] = {}
        self.data["3"]["x"] = []
        self.data["3"]["y"] = []
        self.data["3"]["timestamp"] = []
        
        self.data["4"] = {}
        self.data["4"]["x"] = []
        self.data["4"]["y"] = []
        self.data["4"]["timestamp"] = []
        
        self.data["femto"] = {}
        self.data["femto"]["timestamp"] = []
        self.data["femto"]["channela"] = []
        self.data["femto"]["channelb"] = []
        
        self.thread_id = None
        self.start_thread()

    def start_thread(self, delay=0.1):
        if self.thread_id != None:
            self._stop = True                # send stop to thread
            _timeout = time.time()+1        # timeout = 1s
            # check if thread exited or timeout occured
            while self.thread_id != None and time.time() < _timeout:
                pass
        self._stop = False                   # reset terminate signal
        # create new thread and insert id
        self.thread_id = thread.start_new_thread(self.measurement_thread,(delay,))
        log("Thread #%i started"%(self.thread_id))
    
    def resync(self):
        """calculate timeoffset for time calibration of lockin timebase
        internal time is time from powerup"""
        try:
            sample_time = time.time()
            sample = self.daq2.getSample('/'+self.device+'/demods/0/sample')
            sample_time_2 = time.time()
            backup_offset = self.time_offset
            self.time_offset = (sample_time+sample_time_2)/2 - sample["timestamp"][0]/210e6
            log("LockIn Resync: %f"%(backup_offset-self.time_offset))
        except Exception,e:
            log("Resync failed",e)
            self.time_offset = 0.0
    
    def initialize(self, frequency=222.222, ampl=0.01, order=4, tc=0.1, rate=7):
        general_setting = [
                [["/", self.device, "/sigins/0/diff"],0.0],
                [["/", self.device, "/sigins/1/diff"],0.0],
                #[["/", self.device, "/sigins/0/ac"],1],
                #[["/", self.device, "/sigins/1/ac"],1],

                [["/", self.device, "/demods/0/trigger"],0.0],
                [["/", self.device, "/demods/1/trigger"],0.0],
                [["/", self.device, "/demods/3/trigger"],0.0],
                [["/", self.device, "/demods/4/trigger"],0.0],

                [["/", self.device, "/demods/0/order"],order],
                [["/", self.device, "/demods/1/order"],order],
                [["/", self.device, "/demods/3/order"],order],
                [["/", self.device, "/demods/4/order"],order],

                [["/", self.device, "/sigouts/0/on"],1.0],  # offiv_1403001126_0_0
                #[["/", self.device, "/sigouts/0/range"],0.1],
                #[["/", self.device, "/sigouts/0/amplitudes/6"],ampl],
                #[["/", self.device, "/oscs/0/freq"],frequency],
                [["/", self.device, "/plls/1/enable"],0.0],

                [["/", self.device, "/demods/0/oscselect"],0.0],
                [["/", self.device, "/demods/1/oscselect"],0.0],
                [["/", self.device, "/demods/2/oscselect"],0.0],
                [["/", self.device, "/demods/3/oscselect"],0.0],
                [["/", self.device, "/demods/4/oscselect"],0.0],
                [["/", self.device, "/demods/5/oscselect"],0.0],

                [["/", self.device, "/demods/0/harmonic"],1.0],
                [["/", self.device, "/demods/1/harmonic"],2.0],
                [["/", self.device, "/demods/2/harmonic"],3.0],
                [["/", self.device, "/demods/3/harmonic"],1.0],
                [["/", self.device, "/demods/4/harmonic"],2.0],
                [["/", self.device, "/demods/5/harmonic"],3.0],

                [["/", self.device, "/dios/0/drive"],1]
               ]
        self.daq2.set(general_setting)
        self.set_rate(rate)
        self.set_ac(False)
        self.set_amplitude(ampl)
        self.set_phases()
    
    def set_rate(self, rate=7):
        general_setting = [
                [["/", self.device, "/demods/0/rate"],rate],
                [["/", self.device, "/demods/1/rate"],rate],
                [["/", self.device, "/demods/2/rate"],0.0],
                [["/", self.device, "/demods/3/rate"],rate],
                [["/", self.device, "/demods/4/rate"],rate],
                [["/", self.device, "/demods/5/rate"],0.0],
               ]
        self.daq2.set(general_setting)
        log("LockIn Rate %i"%(rate))
    
    def set_amplitude(self, amplitude=0.01, output=True):
        _range = 1
        if amplitude < 0.1:
            _range = 0.1
            amplitude = amplitude*10
        if amplitude < 0.01:
            _range = 0.01
            amplitude = amplitude*10
        if output:
            output_enabled = 1
        else:
            output_enabled = 0
        general_setting = [
            [["/", self.device, "/sigouts/0/range"],_range],
            [["/", self.device, "/sigouts/0/amplitudes/6"],amplitude],
            [["/", self.device, "/sigouts/0/on"],output_enabled]
            ]
        self.daq2.set(general_setting)
        log("LockIn AC Range %fV, Part %f"%(_range,amplitude))
    
    def set_phases(self, phase_0=0, phase_1=0, phase_3=0, phase_4=0):
        general_setting = [
                [["/", self.device, "/demods/0/PHASESHIFT"],phase_0],
                [["/", self.device, "/demods/1/PHASESHIFT"],phase_1],
                [["/", self.device, "/demods/3/PHASESHIFT"],phase_3],
                [["/", self.device, "/demods/4/PHASESHIFT"],phase_4]
               ]
        self.daq2.set(general_setting)
        log("Phase Correction: %f, %f, %f, %f"%(phase_0,phase_1,phase_3,phase_4))
    
    def set_frequency(self, freq=111.1, tc=0.5, order=4):
        """takes the frequency, order and timeconstant (in s) of the filters"""
        order = max(1, min(order, 8))
        fo = [1.0, 0.644, 0.51, 0.435, 0.386, 0.350, 0.323, 0.301]  # order factors
        tc = tc * fo[order-1]
        general_setting = [
                [["/", self.device, "/demods/0/timeconstant"],tc],
                [["/", self.device, "/demods/1/timeconstant"],tc],
                [["/", self.device, "/demods/3/timeconstant"],tc],
                [["/", self.device, "/demods/4/timeconstant"],tc],
                
                [["/", self.device, "/demods/0/order"],order],
                [["/", self.device, "/demods/1/order"],order],
                [["/", self.device, "/demods/3/order"],order],
                [["/", self.device, "/demods/4/order"],order],

                [["/", self.device, "/oscs/0/freq"],freq],
               ]
        self.daq2.set(general_setting)
        log("Values: TC %f s, Order %i, Frequency %f Hz"%(tc,order,freq))
    
    def set_ac(self, ac_coupling=True):
        """sets autorange and ac"""
        general_setting = [
                [["/", self.device, "/sigins/0/ac"],ac_coupling],
                [["/", self.device, "/sigins/1/ac"],ac_coupling],
               ]
        self.daq2.set(general_setting)
        if ac_coupling:
            log("Lockin AC Coupling ON")
        else:
            log("Lockin AC Coupling OFF")
    
    def get_param(self):
        _range =        self.daq2.getDouble('/'+self.device+'/sigouts/0/range')
        _amplitude =    self.daq2.getDouble('/'+self.device+'/sigouts/0/amplitudes/6')
        sigin_0 =       self.daq2.getDouble('/'+self.device+'/sigins/0/range')
        sigin_1 =       self.daq2.getDouble('/'+self.device+'/sigins/1/range')
        sigout_on =     self.daq2.getDouble('/'+self.device+'/sigouts/0/on')
        freq =          self.daq2.getDouble('/'+self.device+'/oscs/0/freq')
        ac = _range*_amplitude
        return {"ac amplitude": [ac], "sigout on": [sigout_on],"input 0 range": [sigin_0],"input 1 range": [sigin_1],"li freq": [freq]}
        
    

    def measurement_thread(self, delay=0.1):
        """ connects to the server and asks for data """
        log("LockIn Thread started!")        
        self.daq.flush()
        path0 = '/' + self.device + '/demods/*/sample'
        self.daq.subscribe(path0)

        try:
            self.daq.flush()
            while not (self._stop or stop):
                try:
                    dataDict = self.daq.poll(0.05,100,0,True)
                    # acquire lock
                    self.data_lock.acquire()
                    #print "1"
                    if "/"+self.device+"/demods/0/sample" in dataDict:                  
                        self.data["0"]["x"].extend(dataDict["/"+self.device+"/demods/0/sample"]["x"])
                        self.data["0"]["y"].extend(dataDict["/"+self.device+"/demods/0/sample"]["y"])
                        self.data["0"]["auxin0"].extend(dataDict["/"+self.device+"/demods/0/sample"]["auxin0"])
                        self.data["0"]["auxin1"].extend(dataDict["/"+self.device+"/demods/0/sample"]["auxin1"])
                        self.data["0"]["dio"].extend(dataDict["/"+self.device+"/demods/0/sample"]["dio"])
                        self.data["0"]["timestamp"].extend(dataDict["/"+self.device+"/demods/0/sample"]["timestamp"]/210e6+self.time_offset)
                    #print "2"
                    if "/"+self.device+"/demods/1/sample" in dataDict:
                        self.data["1"]["x"].extend(dataDict["/"+self.device+"/demods/1/sample"]["x"])
                        self.data["1"]["y"].extend(dataDict["/"+self.device+"/demods/1/sample"]["y"])
                        self.data["1"]["timestamp"].extend(dataDict["/"+self.device+"/demods/1/sample"]["timestamp"]/210e6+self.time_offset)
                    #print "3"
                    if "/"+self.device+"/demods/3/sample" in dataDict:
                        self.data["3"]["x"].extend(dataDict["/"+self.device+"/demods/3/sample"]["x"])
                        self.data["3"]["y"].extend(dataDict["/"+self.device+"/demods/3/sample"]["y"])
                        self.data["3"]["timestamp"].extend(dataDict["/"+self.device+"/demods/3/sample"]["timestamp"]/210e6+self.time_offset)
                    #print "4"
                    if "/"+self.device+"/demods/4/sample" in dataDict:
                        self.data["4"]["x"].extend(dataDict["/"+self.device+"/demods/4/sample"]["x"])
                        self.data["4"]["y"].extend(dataDict["/"+self.device+"/demods/4/sample"]["y"])
                        self.data["4"]["timestamp"].extend(dataDict["/"+self.device+"/demods/4/sample"]["timestamp"]/210e6+self.time_offset)

                    
                    self.data_lock.release()
                except Exception,e:
                    log("Lockin Poll Failed",e)                
                time.sleep(delay)
        except Exception,e:
            log("Lockin Communication Error in Thread",e)
        finally:
            self.daq.unsubscribe("*")
        # indicate that thread terminated 
        log("Thread #%i finished"%(self.thread_id))
        self.thread_id = None
            
    def get_data_list(self, erase=True, averages=1):
        """returns all the gathered data in one bunch
        and erases the list """
        #if averages < 10:
        #    averages = 10
  
        self.data_lock.acquire()
        return_data = self.data.copy()

        return_data = {}
        
        self.data["femto"]["timestamp"].append(time.time())
        self.data["femto"]["channela"].append(self.ampl_a)
        self.data["femto"]["channelb"].append(self.ampl_b)
     
        min_multiple = int(len(self.data["0"]["x"]) / averages) * averages   
        return_data["0"] = {}
        return_data["0"]["x"] = self.data["0"]["x"][0:min_multiple]
        return_data["0"]["y"] = self.data["0"]["y"][0:min_multiple]
        return_data["0"]["auxin0"] = self.data["0"]["auxin0"][0:min_multiple]
        return_data["0"]["auxin1"] = self.data["0"]["auxin1"][0:min_multiple]
        return_data["0"]["dio"] = self.data["0"]["dio"][0:min_multiple]
        return_data["0"]["timestamp"] = self.data["0"]["timestamp"][0:min_multiple]
        if erase:        
            del(self.data["0"]["x"][0:min_multiple])
            del(self.data["0"]["y"][0:min_multiple])
            del(self.data["0"]["auxin0"][0:min_multiple])
            del(self.data["0"]["auxin1"][0:min_multiple])
            del(self.data["0"]["dio"][0:min_multiple])
            del(self.data["0"]["timestamp"][0:min_multiple])
        
        min_multiple = int(len(self.data["1"]["x"]) / averages) * averages 
        return_data["1"] = {}
        return_data["1"]["x"] = self.data["1"]["x"][0:min_multiple]
        return_data["1"]["y"] = self.data["1"]["y"][0:min_multiple]
        return_data["1"]["timestamp"] = self.data["1"]["timestamp"][0:min_multiple]
        if erase: 
            del(self.data["1"]["x"][0:min_multiple])
            del(self.data["1"]["y"][0:min_multiple])
            del(self.data["1"]["timestamp"][0:min_multiple])
        
        min_multiple = int(len(self.data["3"]["x"]) / averages) * averages 
        return_data["3"] = {}
        return_data["3"]["x"] = self.data["3"]["x"][0:min_multiple]
        return_data["3"]["y"] = self.data["3"]["y"][0:min_multiple]
        return_data["3"]["timestamp"] = self.data["3"]["timestamp"][0:min_multiple]
        if erase: 
            del(self.data["3"]["x"][0:min_multiple])
            del(self.data["3"]["y"][0:min_multiple])
            del(self.data["3"]["timestamp"][0:min_multiple])
        
        min_multiple = int(len(self.data["4"]["x"]) / averages) * averages 
        return_data["4"] = {}
        return_data["4"]["x"] = self.data["4"]["x"][0:min_multiple]
        return_data["4"]["y"] = self.data["4"]["y"][0:min_multiple]
        return_data["4"]["timestamp"] = self.data["4"]["timestamp"][0:min_multiple]
        if erase: 
            del(self.data["4"]["x"][0:min_multiple])
            del(self.data["4"]["y"][0:min_multiple])
            del(self.data["4"]["timestamp"][0:min_multiple])

        return_data["femto"] = {}
        return_data["femto"]["timestamp"] = self.data["femto"]["timestamp"][:]
        return_data["femto"]["channela"] = self.data["femto"]["channela"][:]
        return_data["femto"]["channelb"] = self.data["femto"]["channelb"][:]
        if erase:    
            self.data["femto"]["timestamp"] = []
            self.data["femto"]["channela"] = []
            self.data["femto"]["channelb"] = []
        self.data_lock.release()
        
        return return_data
        
    
    def set_dio(self, data=0):
        settings = [[["/", self.device, "/dios/0/output"],data],]
        self.daq2.set(settings)
    
    def get_dio(self):
        val = self.data["0"]["dio"][-1]
        return val       

    def femto_reset(self):
        self.ampl_a = 0
        self.ampl_b = 0
        self.femto_update()
    
    def femto_set(self, a=0, b=0):
        self.ampl_a = a
        self.ampl_b = b
        self.femto_update()
    
    def femto_get(self):
        return (self.ampl_a, self.ampl_b)
    
    def femto_update(self):
        value = self.ampl_b + (self.ampl_a << 4)
        self.set_dio(value)
        
        
    def femto_increase_amplification(self, channel=0):
        self.data_lock.acquire()        
        if channel == 0:
            self.ampl_a += 1
            if self.ampl_a >= 4:
                self.ampl_a = 3
            
        if channel == 1:
            self.ampl_b += 1
            if self.ampl_b >= 4:
                self.ampl_b = 3  
        self.data_lock.release()
        self.femto_update()
    
    def femto_decrease_amplification(self, channel=0):
        self.data_lock.acquire()
        if channel == 0:
            self.ampl_a -= 1
            if self.ampl_a < 0:
                self.ampl_a = 0
            
        if channel == 1:
            self.ampl_b -= 1
            if self.ampl_b < 0:
                self.ampl_b = 0
        self.data_lock.release()
        self.femto_update()

    


class MOTOR:
    def __init__(self, addr="ASRL3", reduction=3088, encoder=512):
        #self.motor=serial.Serial('COM1',115200,timeout=0) 
        self.motor=visa.SerialInstrument(addr,delay=0.00,term_chars='\r\n',timeout=0.2)
        self.motor.clear()
        self._gearfact=reduction*encoder*4
        self.initialize()
        
        self.data = {}
        self.data_lock = thread.allocate_lock()
        self.data["timestamp"] = []
        self.data["position"] = []
        self.data["current"] = []
        self.data["velocity"] = []
        self.higher_bound = False
        self.lower_bound = False
        self.thread_id = None
        self.start_thread()

    def start_thread(self, delay=0.1):
        if self.thread_id != None:
            self._stop = True                # send stop to thread
            _timeout = time.time()+1        # timeout = 1s
            # check if thread exited or timeout occured
            while self.thread_id != None and time.time() < _timeout:
                pass
        self._stop = False                   # reset terminate signal
        # create new thread and insert id
        self.thread_id = thread.start_new_thread(self.measurement_thread,(delay,))
        log("Thread #%i started"%(self.thread_id))

    def initialize(self, max_rpm=8000):
        """activate motor control"""
        self.motor.write('V0')                # speed = 0 rpm
        self.motor.write('AC500')            # acceleration
        self.motor.write('LCC100')             # max current in mA
        self.motor.write('SP%i'%(max_rpm))    # maximum rpm
        self.motor.write('EN')                # enable movement
        
        self.limit_low = -25
        self.limit_high = 0
        self._mpos = 0
        self._v = 0
        self._current = 0
        self.set_current(150)
        self._gv = self.update_set_velocity()
        log("Motor initialized")
    
    def disable(self):
        """stop motor and deactivate motor control"""
        self.motor.write('V0')
        self._mpos=float(self.get_pos())
        self.motor.write('DI')
    
    def enable(self):
        """enables motor"""
        self.motor.write('EN')
    
    def stop(self):
        """stop the motor (3x)"""
        for i in range(3):
            self.set_velocity(0)

    def get_pos(self):
        """return actual motor position of its encoder
            in encoder steps"""
        return self._mpos

    def get_real_pos(self, counts=None):
        """converts actual position to turns of the screw"""
        if counts==None:
            position = self.get_pos()
        else:
            position = float(counts)
        return float(position/self._gearfact)
    
    #def get_counts(self, turns):
    #    """converts encoder counts to turns of the screw"""
    #    return int(turns*self._gearfact)
  
    def get_velocity(self):
        """return the current velocity"""
        return self._v
    
    def update_set_velocity(self):
        answer = self.motor.ask('GV')   # update speed
        try:
            speed=float(answer.strip())
        except:
            speed=0
            log("Bad Answer!")
            print answer
        return speed
    
    def set_velocity(self,speed):
        """sets the velocity"""
        self.motor.write('V'+str(speed))
        self._gv = speed
    
    def set_home(self, addr=None):
        """sets HOME"""
        if addr == None:
            self.motor.write('HO')
        else:
            self.motor.write('HO'+str(addr))
       
    def get_temperature(self):
        """gets temperature"""
        return float(self.motor.ask("TEM"))
    
    def set_current(self, limit=50):
        """sets the current limit in mA"""
        self.motor.write('LCC%i'%(int(limit))) 
        
    def get_current(self):
        """returns current"""
        return self._current

    def goto_nr(self, destination=0, speed=8000):
        """drives the motor to a defined position (realpos_abs)"""
        #self.motor.ask('SP'+str(speed)) # max speed
        newpos=long(destination)
        self.motor.write('LA'+str(newpos))
        self.motor.write('M')
    
    def set_lower_limit(self, limit=-25):
        self.limit_low = limit
    
    def set_upper_limit(self, limit=0):
        self.limit_high = limit

# data handling
    def get_data_list(self, erase=True):
        """returns all the gathered data in one bunch
        and erases the list """       
        # get lock first
        self.data_lock.acquire()
        # copy data
        return_data = self.data.copy()

        if erase:        
            self.data["timestamp"] = []
            self.data["position"] = []
            self.data["current"] = []
            self.data["velocity"] = []
        self.data_lock.release()
        return return_data

# thread
    def measurement_thread(self, delay=0.05):
        log("Motor Thread started!")
        speed_check_count = 0
        while not (self._stop or stop):
            try:            
                answer = self.motor.ask('GN')   # update speed            
                self._v=float(answer.strip())
            except:
                self._v=-1
                log("Bad Answer Velocity")
                log(answer)
            try:
                answer = self.motor.ask('POS')  # update position
                self._mpos=float(answer.strip())
            except:
                self._mpos=-1
                log("Bad Answer Position")
                log(answer)
            try:
                answer = self.motor.ask("GRC")  # update current
                self._current=float(answer.strip())
            except:
                self._current=-1
                log("Bad Answer Current")
                log(answer)

            # append gathered data to internal data dictionary
            self.data_lock.acquire()
            self.data["timestamp"].append(time.time())
            self.data["position"].append(self.get_real_pos())
            self.data["current"].append(self.get_current())
            self.data["velocity"].append(self.get_velocity())
            self.data_lock.release()
            
            # check if the motor is running
            running = True
            if self._v == 0:
                running = False
            
            # if it's really running check for limits
            if running:
                #print self._mpos
                if self._gv > 0 and self.get_real_pos() >= self.limit_high:       
                    self.stop()
                    self.higher_bound = True
                    log("Emergency Stop of Motor, higher bound!")
                else:
                    self.higher_bound = False
                if  self._gv < 0 and self.get_real_pos() <= self.limit_low:
                    self.stop()
                    self.lower_bound = True
                    log("Emergency Stop of Motor, lower bound!")
                else:
                    self.lower_bound = False
                    
                # check for bad speed values
                try:
                    if abs(self._v) > 10 and abs(self._gv) > 5:
                        v_ratio = abs(self._v)/abs(self._gv)
                        if  v_ratio < 0.8:
                            speed_check_count += 1
                        else:
                            speed_check_count = 0
                        if speed_check_count > 10:
                            log("Motor rpm too low!")
                except Exception,e:
                    log("Motor speed check failed",e)
                    
            time.sleep(delay)
        # indicate that thread terminated 
        log("Thread #%i finished"%(self.thread_id))
        self.thread_id = None
            



device_delay = 10
def motor_starter():
    found = False
    while not found and not stop:
        try:
            global motor
            motor = MOTOR(addr=config.installed_motor)
            log("Found Motor")
            found = True
        except:
            #log("Couldn't Find Motor")
            time.sleep(device_delay)

def lockin_starter():
    found = False
    while not found and not stop:
        try:
            global lockin
            lockin = ZURICH()
            log("Found Lockin")
            found = True
        except:
            #log("Couldn't Find Lockin",e)
            time.sleep(device_delay)

def yoko_starter():
    found = False
    while not found and not stop:
        try:
            global yoko
            if config.installed_yoko == "7651":
                yoko = YOKO7651()
            elif config.installed_yoko == "GS200":
                yoko = GS200()    
            log("Found Yoko")
            found = True
        except Exception,e:
            log("Couldn't Find Yoko",e)
            time.sleep(device_delay)


def magnet_starter():
    found = False
    while not found and not stop:
        try:
            global magnet
            magnet = Magnet(config.magnetZAddresse)
            log("Found Magnet")
            found = True
        except Exception,e:
            #log("Couldn't Find Magnet",e)
            time.sleep(device_delay)

def magnet_starter_2():
    found = False
    while not found and not stop:
        try:
            global magnet_2
            magnet_2 = Magnet(config.magnetXAddresse)
            log("Found Magnet 2")
            found = True
        except Exception,e:
            #log("Couldn't Find Magnet",e)
            time.sleep(device_delay)
            
def lakeshore_starter():
    found = False
    while not found and not stop:
        try:
            global lakeshore
            lakeshore = LAKESHORE()
            log("Found Lakeshore")
            found = True
        except Exception,e:
            log("Couldn't Find Lakeshore",e)
            time.sleep(device_delay)


def agilent_34410a_starter_new():
    found = False
    while not found and not stop:
        try:
            global agilent_new
            agilent_new = Agilent34410A(addr=config.installed_agilent_voltage)

            log("Found Agilent 34410a")
            found = True
        except Exception,e:
            log("Couldn't Find Agilent 34410a",e)
            time.sleep(device_delay)

def agilent_34410a_starter_old():
    found = False
    while not found and not stop:
        try:
            global agilent_old
            agilent_old = Agilent34410A(addr=config.installed_agilent_current)

            log("Found Agilent 34410a Old")
            found = True
        except Exception,e:
            log("Couldn't Find Agilent 34410a Old",e)
            time.sleep(device_delay)

"""def agilent_34401a_starter():
    found = False
    while not found and not stop:
        try:
            global agilent_old
            agilent_old = Agilent34401A()
            log("Found Agilent 34401a")
            found = True
        except:
            log("Couldn't Find Agilent 34401a")
            time.sleep(device_delay)"""


""" Just helps the editor to know, what is behind the labels """
if False: # dont change
    motor = MOTOR()
    lockin = ZURICH() 
    yoko = GS200() 
    magnet = Magnet() 
    magnet_2 = Magnet() 
    lakeshore = LAKESHORE() 
    agilent_new = Agilent34410A() 
    agilent_old = Agilent34410A() 
else:
    motor = None
    lockin = None 
    yoko = None 
    magnet = None 
    magnet_2 = None
    lakeshore = None 
    agilent_new = None 
    agilent_old = None 

thread.start_new_thread(yoko_starter,())
thread.start_new_thread(motor_starter,())
thread.start_new_thread(lockin_starter,())
if config.magnetZ:
    thread.start_new_thread(magnet_starter,())
if config.magnetX:
    thread.start_new_thread(magnet_starter_2,())
thread.start_new_thread(lakeshore_starter,())
thread.start_new_thread(agilent_34410a_starter_new,())
thread.start_new_thread(agilent_34410a_starter_old,())
#thread.start_new_thread(agilent_34401a_starter,())

log("Device Threads Initalized")


if __name__ == "__main__":
    
    while True:
        try:
            #print len(agilent_new.get_data_list())
            print len(agilent_old.get_data_list()["timestamp"])
        except:
            pass
        time.sleep(1)
        pass

