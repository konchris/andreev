# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 17:21:30 2013

@author: David Weber
"""
import struct   # ascii to single/double
#import serial

class YOKO7651:
    def __init__(self, GPIB_No=24):
        self.yoko=visa.instrument('GPIB0::%i'%GPIB_No, delay=0.05, term_chars='\n')
        self.ranges={10e-3:'R2', 100e-3:'R3', 1.0:'R4', 10.0:'R5', 30.0:'R6'}
        self.SetPoint=None
        self.status={'prog set':None, 'prog run':None, 'error':None, 'outp unstable':None, 'outp on':None, 'calib mode': None, 'memory card':None, 'CAL switch':None}
        self.byteorder=['CAL switch', 'memory card', 'calib mode', 'outp on', 'outp unstable', 'error', 'prog run', 'prog set']
   
    def initialize(self):
        """get current set point, set default parameters, ranges etc"""        
        self.yoko.write('RC')
        self.yoko.write('o1e')
    
    def set_range(self, value):
        """set appropriate range for target value"""
        rangevals=np.array(self.ranges.keys())
        rangecomm=self.ranges[min(rangevals[np.where(rangevals>=float(value))])]
        self.yoko.write('%s'%rangecomm)
        self.yoko.write('E')

    def set(self, U=1.0e-6):
        """define yoko setpoint U in V"""
        self.SetPoint=float(U)
        self.yoko.write('S%f'%float(U))
        print 'S%f'%float(U)
        self.yoko.write('E')
        
class Agilent34401A:
    def __init__(self,addr=23):
        self.agilent=visa.instrument("GPIB::%i"%(addr),timeout=2)
        self.get_errors()
        #self.reset()
        self.setup_dc()
        self.set_nplc(1)
        
        self.data = {}

        self.data_lock = thread.allocate_lock()
        #self.data_lock.acquire()
        self.data["timestamp"] = []
        self.data["voltage"] = []
        thread.start_new_thread(self.measurement_thread,(0.01,))
        
    def reset(self):
        self.agilent.write("*RST")
        print 'RESET: '+self.agilent.ask("*IDN?")
    
    def clear_device(self):
        self.agilent.write("CLEAR 722")
    
    def setup_dc(self,range=10,resolution=1e-4):
        """Sets range and resolution (including PLC somehow)"""
        self.agilent.write("CONF:VOLT:DC %f,%f"%(range,resolution))
        self.agilent.write('VOLT:DC:RANG:AUTO ON')
        
    def set_nplc(self,nplc=1):
        """Sets Integration time to defined NPLC"""
        self.agilent.write("VOLT:DC:NPLC %f"%(nplc))
        
    def set_trigger(self, source="IMM", delay=0.1, count=1, trg_count=1):
        """Setup for Trigger-Source and -Delay of Measurement.
        Number of Measurements per Trigger
        [count = INF = -1 sets trigger-counts to infinite. To get back to
        Ready-State send *device-clear*-command]
        Possible Values: 
            BUS|IMMediate|EXTernal
            0-3600 seconds"""
        if trg_count == -1:
            str_trg_count = "INF"
        else:
            str_trg_count = str(trg_count)
        self.agilent.write("TRIG:SOUR %s"%(source))
        #print "TRIG:SOUR %s"%(source)
        self.agilent.write("TRIG:DEL %f"%(delay))
        #print "TRIG:DEL %f"%(delay)
        self.agilent.write("TRIG:COUN %s"%str_trg_count)
        #print "TRIG:COUN %s"%str_trg_count
        self.agilent.write("SAMP:COUN %i"%(count))
        #print "SAMP:COUN %i"%(count)
    
    def send_trigger(self):
        """Sends Bus Trigger"""
        self.agilent.write("*TRG")
        
    def wait_for_trigger(self):
        """Sets instrument to triggered Mode"""
        self.agilent.write("INIT")
    
    def get_measurements(self):
        """Fetches measurements of instrument"""
        answer = self.agilent.ask("FETC?")
        try:
            values = [float(x) for x in answer.split(',')]
            return values
        except Exception,e:
            log("Returned Measurement not readable:",e)
            log(answer)
            return [0]
    
    def measurement(self):
        try:        
            return float(self.agilent.ask("READ?"))
        except Exception,e:
            log("Measurement Error Agilent",e)
            return 0
        
    def get_errors(self):
        try:
            i = 0
            answer = self.agilent.ask("SYST:ERR?")
            while answer[1] != "0" and i < 100:
                log(answer)
                answer = self.agilent.ask("SYST:ERR?")
                i = i + 1 
        except Exception,e:
            print e
            
    def set_text(self, text=""):
        self.agilent.write(":DISP:TEXT \"%s\""%(text))
        
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
        while not stop:
            voltage = self.measurement()
            # append gathered data to internal data dictionary
            self.data_lock.acquire()
            self.data["timestamp"].append(time.time())
            self.data["voltage"].append(voltage)
            self.data_lock.release()
                    
            time.sleep(delay)
            
class Agilent34401A_DEP:
    def __init__(self,addr=24):
        self.agilent=visa.instrument("GPIB::%i"%(addr),timeout=1000)
    
    def write(self,command):
        try:
            print command
            self.agilent.write(command)
            self.get_errors()
        except Exception,e:
            print "Writing to Agilent MM failed"
            print e
    
    def ask(self,command):
        try:
            if command != "SYST:ERR?":
                print command
            return self.agilent.ask(command)
        except Exception,e:
            print "Writing to Agilent MM failed"
            print e
        
    def reset(self):
        self.agilent.write("*RST")
        print 'RESET: '+self.agilent.ask("*IDN?")
    
    def clear_device(self):
        self.agilent.write("CLEAR 722")
    
    def setup_dc(self,range=3,resolution=1e-5):
        """Sets range and resolution (including PLC somehow)"""
        self.write("CONF:VOLT:DC %f,%f"%(range,resolution))
        
    def set_nplc(self,nplc=1):
        """Sets Integration time to defined NPLC"""
        self.write("VOLT:DC:NPLC %f"%(nplc))
        
    def set_trigger(self, source="IMM", delay=0, count=1):
        """Setup for Trigger-Source and -Delay of Measurement.
        Number of Measurements per Trigger
        [ATTENTION: Sets trigger-counts to infinite. To get back to
        Ready-State send *device-clear*-command]
        Possible Values: 
            BUS|IMMediate|EXTernal
            0-3600 seconds"""
        self.write("TRIG:SOUR %s"%(source))
        self.write("TRIG:DEL %f"%(delay))
        self.write("SAMP:COUN %i"%(count))
        self.write("TRIG:COUN 1")
    
    def wait_for_trigger(self):
        """Sets instrument to triggered Mode"""
        self.write("INIT")
    
    def send_trigger(self):
        """Sends Bus Trigger"""
        self.write("*TRG")
    
    def get_measurements(self):
        """Fetches measurements of instrument"""
        answer = self.ask("FETC?")
        try:
            values = [float(x) for x in answer.split(',')]
            return values
        except Exception,e:
            log("Returned Measurement not readable:",e)
            log(answer)
            return [0]
    
    def measurement(self):
        try:        
            return float(self.ask("READ?"))
        except Exception,e:
            print e
            return 0
        
    def get_errors(self):
        i = 0
        try:
            answer = self.ask("SYST:ERR?")
            while answer[1] != "0" and i < 100:
                print answer
                answer = self.ask("SYST:ERR?")
                i = i + 1 
        except Exception,e:
            print e


class LAKESHORE:
    def __init__(self,addr=12):
        self.lakeshore=visa.instrument("GPIB::%i"%(addr))

    def initialize(self):
        """Initializes the device by reading all the values"""
        self.reset()
        self.get_temperature()
        self.get_setpoint()
        self.get_heater_range()
        
    
    def reset(self):
        """Sends Reset-Command"""
        self.lakeshore.write('*RST')
        print 'RESET: '+self.yoko.ask("*IDN?")
    
    def clear(self):
        """Clears the interface"""
        self.lakeshore.write('*CLS')
    
    def get_temperature(self):
        """Asks for the temperature of sample"""
        self.temperature = self.lakeshore.ask('KRDG? A')
        return self.temperature
    
    def get_setpoint(self):
        """Gets the setpoint"""
        self.setpoint = self.lakeshore.ask('SETP? 1');
        return self.setpoint;
    
    def set_setpoint(self, temperature=4):
        """Sets the new setpoint"""
        self.setpoint = self.lakeshore.write('SETP 1,%f'%(temperature))
        
    def set_heater_range(self, range=0):
        """Set the heater range to specified value:
                0 = off
                1 = low
                2 = med
                3 = high"""
        self.heater_range = range
        self.lakeshore.write('RANGE %i;'%(range))
    
    def get_heater_range(self):
        """Get the heater range, look @ set"""
        self.heater_range = self.lakeshore.ask("RANGE?")
        print self.lakeshore.ask("RANGE?")
        return self.heater_range
        


class PRIZMATIX:
    def __init__(self):
        #self.prizmatix=COM('COM1',stopbits=1,term_chars='\n',term_char_read='\r',baudrate=115200)       
        self.prizmatix = serial.Serial('COM1', 115200, timeout=1)


    def get_system_version(self):
        self.prizmatix.write('$V%')
        answer = self.prizmatix.readline()
        return answer
    
    def reset(self):
        self.prizmatix.write('$R%')
        answer = self.prizmatix.readline()
        if answer == 'R':
            return True
        else:
            return False
    
    def set_power_channel(self,channel=1,power=0):
        self.prizmatix.write('$C%i,%i,%%'%(channel,power))
        answer = self.prizmatix.readline()
        if answer == 'C':
            return True
        else:
            return False
        
    def get_powers(self):
        self.prizmatix.write('$A%')
        answer = self.prizmatix.readline()
        temp = answer[1:-2].split(',')
        result = [int(x) for x in temp]
        return result
    
    def close(self):
        self.prizmatix.close()


class TPG261:
    def __init__(self):
        self.tpg=serial.Serial('COM1',9600,timeout=0) 
        self.frequency(1)   # set continous mode 1 Hz
        time.sleep(1.1)             # wait to receive first data
        self.pressure = 0           # reset pressure
        self.get_pressure()         # get pressure

    def get_pressure(self):
        """Don't call more frequently than refresh rate!
        For higher frequencies use higher refresh rate"""
        answer = self.tpg.readlines()
        try:
            if len(answer[-1]) > 28:
                #print answer[-1]
                answer_split = answer[-1].split(',')
                _p = float(answer_split[1])
                self.pressure = _p
            else:
                if len(answer[-2])> 28:
                    answer_split = answer[-2].split(',')
                    _p = float(answer_split[1])
                    self.pressure = _p
        except Exception,e:
            log("Communication with Pressure Gauge failed",e)
        return self.pressure 
    
    def frequency(self,mode=1):
        """Sets the refresh frequency:
            0 = 10 Hz
            1 = 1 Hz
            2 = 0.017 Hz (1 min)"""
        self.tpg.write("COM,%i\n"%(mode))


class Keithley2000:
    def __init__(self, GPIB_No=17, dlay=0.01):
        """calls the KEITHLEY 2000 multimeter via the specified GPIB number
           NOTE: 
        """
        self.K2000=visa.instrument("GPIB::%i"%GPIB_No,delay=dlay,term_chars='\n')        
        self.GPIB=GPIB_No

    def initialize_VDC(self):
        """Initialize to DC-Voltage measurement.
        No Argumentes required"""
        try:
            self.K2000.write('*RST')   
            self.K2000.write('FORM:DATA SREAL') # double
            #self.K2000.write('FORM:DATA DREAL') # double
            #self.K2000.write('FORM:DATA ASCii') # ascii
            self.K2000.write('FORM:ELEM READ')  # only bare data
            self.K2000.write('SENS:FUNC "VOLT:DC"') # voltage dc
            self.K2000.write('SENS:VOLT:DC:RANG:AUTO ON')   # autorange
            self.K2000.write('SENS:VOLT:DC:REF:STAT OFF')   # no offset corr.
            self.K2000.write('SENS:VOLT:DC:DIG 7')  # 4.5 digits
            self.K2000.write('SENS:VOLT:DC:NPLC 5')
            self.set_filter(filter='OFF', type='REP', count=1)
            self.K2000.write('INIT:CONT ON')    # initiate continuos
        except:
            print('ERROR: Failed to initialize Keithley 2000 Multimeter')
            return False
        return True

    def read_value(self):
        """returns the last instrument reading"""
        raw=self.K2000.ask('DATA?')
        try:
            if raw[0] == "#" and raw[1] == "0":
                value = struct.unpack("f",raw[2:6]) # single
                #value = struct.unpack("d",raw[2:10]) # double
            else:
                value = [0.0]
        except:
            print "Reading Error!"
            print len(raw)
            return 0.0
        return value[0]

    def set_range(self, range='AUTO'):
        """Set upper Voltage limit of Keithley 2000 Multimeter (max 1000 V)
           set range to 'AUTO' to enable AUTO range"""
        if range=='AUTO':
            self.K2000.write('SENS:VOLT:DC:RANG:AUTO ON')
        else:
            self.K2000.write('SENS:VOLT:DC:RANG %s'%str(range))

    def set_rate(self, NPLC=0.1):
        """Set integration rate in line cycles (PLC);
           0.01 to 10 (for 50Hz mains frequency)"""
        self.K2000.write('SENS:VOLT:DC:NPLC %s'%str(NPLC))

    def set_filter(self, filter='OFF', type='REP', count=10):
        """Sets the filter:
            filter = ON|OFF
            type = MOV|REP"""
        self.K2000.write('SENS:VOLT:DC:AVER:TCON %s'%str(type))
        self.K2000.write('SENS:VOLT:DC:AVER:COUN %s'%str(count))
        self.K2000.write('SENS:VOLT:DC:AVER:STAT %s'%str(filter))
        

class AGILENT:
    def __init__(self,addr=17):
        self.agilent=visa.instrument("GPIB::%i"%(addr))

    def initialize(self):
        """get current set point, set default parameters, ranges etc"""
        self.reset()
    
    def command(self,cmd):
        self.agilent.write(cmd)
    
    def get_errors(self):
        #asks for last error
        return self.agilent.ask(':SYST:ERR?')
    
    
    
#configuartions of channels and variables
    
    def get_start(self):
        """Returns the start value of VAR1"""
        result=self.agilent.ask(':PAGE:MEAS:VAR1:START?;')
        self.Start=float(result)
        return self.Start

    def set_start(self, U=0):
        """Set new start value of VAR1"""
        self.Start = U
        self.agilent.write(':PAGE:MEAS:VAR1:START %f;'%(U))
        
        
    def get_stop(self):
        """Returns the stop value of VAR1"""
        result=self.agilent.ask(':PAGE:MEAS:VAR1:STOP?')
        self.Stop=float(result)
        return self.Stop    
    
    def set_stop(self, U=1):
        #Set new stop value of VAR1
        self.Stop = U
        self.agilent.write(':PAGE:MEAS:VAR1:STOP %f;'%(U))
    
    
    def get_step(self):
        """Returns the step value of VAR1"""
        result=self.agilent.ask(':PAGE:MEAS:VAR1:STEP?;')
        self.Step=float(result)
        return self.Step    
    
    def set_step(self, U=0.01):
        """Set new step value of VAR1"""
        self.Step = U
        self.agilent.write(':PAGE:MEAS:VAR1:STEP %f;'%(U))
    
    def set_sampling_value(self, value=0,smu=1):
        """Sets a value for SMU in sampling mode"""
        self.agilent.write(':PAGE:MEAS:SAMP:CONS:SMU%i %f;'%(smu,value))

    def set_sweep_smu_cons_compliance(self, channel=2,compliance=0.001):
        """Sets a new compliance value"""
        self.agilent.write(':PAGE:MEAS:CONS:SMU%i:COMP %f;'%(channel,compliance))
    
    def set_sweep_smu_var1_compliance(self,compliance=0.001):
        """Sets a new compliance value"""
        self.agilent.write(':PAGE:MEAS:VAR1:COMP %f;'%(compliance))
        
    def set_smu(self, channel=1,function='CONS', 
                output_mode='V', current_name='I1', 
                voltage_name='V1'):
        """ sets SM-Units to desired values
            valid modes are:
            function = VAR1,VAR2,VARD,CONS
            output_mode = V,I,VPUL,IPUL,COMM"""
        
        self.agilent.write(':PAGE:CHAN:SMU%s:MODE %s;'%(channel,output_mode))
        self.agilent.write(':PAGE:CHAN:SMU%s:FUNC %s;'%(channel,function))
        self.agilent.write(':PAGE:CHAN:SMU%s:INAM \'%s\';'%(channel,current_name))
        self.agilent.write(':PAGE:CHAN:SMU%s:VNAM \'%s\';'%(channel,voltage_name))
    
    def set_vmu(self, channel=1,function='DVOL',
                voltage_name='Vdiff')  :
        self.agilent.write(':PAGE:CHAN:VMU%s:MODE %s;'%(channel,function))
        self.agilent.write(':PAGE:CHAN:VMU%s:VNAM \'%s\';'%(channel,voltage_name))
        
    def clear_meas_list(self):
        #clears the table in the agilent
        self.agilent.write(':PAGE:DISP:LIST:DEL:ALL;')
      
    def add_meas_to_list(self, name):
        # maximum is 6 variables in the data list
        self.agilent.write(':PAGE:DISP:LIST:SEL \'%s\';'%(name))
        
    def set_axis_min(self, axis='X',minimum=-1):
        """Sets minimum value of X,Y1,Y2 axis"""
        self.agilent.write(':PAGE:DISP:GRAP:%s:MIN %f'%(axis,minimum))
    
    def set_axis_max(self, axis='X',maximum=-1):
        """Sets maximum value of X,Y1,Y2 axis"""
        self.agilent.write(':PAGE:DISP:GRAP:%s:MAX %f'%(axis,maximum))
    
    def set_axis_name(self, axis='X',name='Vsourc'):
        """Sets name of X,Y1,Y2 axis"""
        self.agilent.write(':PAGE:DISP:GRAP:%s:NAME \'%s\''%(axis,name))
        
        
    
    def set_measurement_type(self,mode='SING'):
        """starts measurement depending on mode
        SINGle|DOUBle"""
        self.agilent.write(':PAGE:MEAS:VAR1:MODE %s;'%(mode)) 
        
    def start_measurement(self,mode='SING'):
        """starts measurement depending on mode
        SING|APP|REP"""
        #self.agilent.write('*ESE 0x01')
        self.agilent.ask('*ESR?')
        self.agilent.write(':PAGE:SCON:%s;'%(mode))
        self.agilent.write('*OPC;')
    
    def wait_for_end(self,timeout=10000,delay=1):
        """(multiply) asks the agilent, if it finished.
        timeout defines the number
        delay defines the time between questions in s"""
        i = 0
        while i < timeout:
            answer = self.agilent.ask('*ESR?')
            if int(answer) & 1:
                break
            print '.',
            time.sleep(delay)
            i = i+1
        print 'Finished!'          
        
        
    def set_meas_mode(self,mode='SWE'):
        """ sets the working mode of agilent
             SWEep, SAMPling, QSCV (quasi static capacity..)"""
        self.agilent.write(':PAGE:CHAN:MODE %s;'%(mode))
    
    def set_integ_time_long(self,powercycles=16):
        self.agilent.write(':PAGE:MEAS:MSET:ITIM:LONG %d;'%(powercycles))
    
    def set_integ_time_short(self,microseconds=640e-6):
        self.agilent.write(':PAGE:MEAS:MSET:ITIM:SHOR %e;'%(microseconds))
    
    def set_delay_time(self, delay=0.1):
        self.agilent.write(':PAGE:MEAS:DEL %f;'%(delay))
    
    def set_hold_time(self, holdtime=1):
        self.agilent.write(':PAGE:MEAS:HTIM %f;'%(holdtime))
    
    def set_sampling_hold_time(self, holdtime=0.2):
        self.agilent.write(':PAGE:MEAS:SAMP:HTIM %f;'%(holdtime))
    
    def set_sampling_interval(self, interval=0.1):
        self.agilent.write(':PAGE:MEAS:SAMP:IINT %f;'%(interval))
    
    def set_sampling_points(self, points=50):
        self.agilent.write(':PAGE:MEAS:SAMP:POIN %i;'%(points))
    
    def set_sampling_time_auto(self):
        self.agilent.write(':PAGE:MEAS:SAMP:PER:AUTO ON;')
    
    def set_integ_time(self,integ_time=1):
        """possible values: 0=SHOR|1=MED|2=LONG"""
        if integ_time==0:
            self.agilent.write(':PAGE:MEAS:MSET:ITIM SHOR;')
        elif integ_time==1:
            self.agilent.write(':PAGE:MEAS:MSET:ITIM MED;')
        elif integ_time==2:
            self.agilent.write(':PAGE:MEAS:MSET:ITIM LONG;')        
        
    def get_data(self, name='I3'):
        #gets data of measurement   
        result = self.agilent.ask(':FORM:BORD NORM;DATA ASC;:DATA? \'%s\';'%(name))
        return str.split(result,',')
        
    def reset(self):
        """sends the reset signal via gpib"""
        self.agilent.write('*RST')
        
    def disable_mmu(self):
        #disables unused measurement units
        self.agilent.write(':PAGE:CHAN:SMU3:DIS;')
        self.agilent.write(':PAGE:CHAN:SMU4:DIS;')
        self.agilent.write(':PAGE:CHAN:VSU1:DIS;')
        self.agilent.write(':PAGE:CHAN:VSU2:DIS;')
        
        

class LS336:
    def __init__(self, addr=7, term_chars='\n'):
        """Lakeshore 336 Temperature Sensor"""
        self.lakeshore=visa.instrument("GPIB::%i"%(addr))
        self.range = [0,0,0,0]
        self.setpoint = [0,0,0,0]
        self.temperature = [0,0,0,0]

    
    def get_setpoint(self, channel=1):
        """returns the setpoint of given channel"""
        self.setpoint[channel] = self.lakeshore.ask("SETP? %i"%(channel))
        return float(self.setpoint[channel])

    def set_setpoint(self, channel=1,setpoint=2):
        """defines setpoint of channel"""
        self.lakeshore.write("SETP %i,%f"%(channel,setpoint))
        print "SETP %i,%f"%(channel,setpoint)
        self.setpoint[channel] = self.get_setpoint(channel)
        return self.setpoint[channel]
        
    def get_heater_range(self, channel=1):
        self.range[channel] = self.lakeshore.ask("RANGE? %i"%(channel))
        return int(self.range[channel])
        
    def set_heater_range(self, channel=1,_range=0):
        self.lakeshore.write("RANGE %i,%i"%(channel,_range))
        self.range[channel] = self.get_heater_range(channel)
        
    def get_temperature(self, channel="A"):
        """Gets Kelvin temperature reading"""
        return float(self.lakeshore.ask("KRDG? %s"%(channel)))
    
    def get_heater_power(self, channel=1):
        """Returns heater power in percent"""
        return float(self.lakeshore.ask("HTR? %i"%(channel)))
    
    def set_alarm(self):#, channel="B",state=1,high_setpoint=4.8,low_setpoint=0,deadband=0.3,latch=0,audible=1,visible=1):
        """Sets the alarm to state given. Mainly for magnet shut down."""
        channel="B"
        state=1
        high_setpoint=4.8
        low_setpoint=0
        deadband=0.3
        latch=0
        audible=0
        visible=1
        self.lakeshore.write("ALARM %s,%i,%f,%f,%f,%i,%i,%i"%(channel,state,high_setpoint,low_setpoint,deadband,latch,audible,visible))
        self.lakeshore.write("RELAY 1,2,B,1")
    
    def unset_alarm(self):
        """Sets the alarm to state given. Mainly for magnet shut down."""
        channel="B"
        state=0
        high_setpoint=4.8
        low_setpoint=0
        deadband=0.3
        latch=0
        audible=1
        visible=1
        self.lakeshore.write("ALARM %s,%i,%f,%f,%f,%i,%i,%i"%(channel,state,high_setpoint,low_setpoint,deadband,latch,audible,visible))
        self.lakeshore.write("RELAY 1,2,B,1")
        
    
    def ask(self,text):
        print self.lakeshore.ask(text)


class SR830:
    def __init__(self, GPIB_No=10):
        """Stanford Research SR830 Lockin-Amplifier"""
        self.lockin=visa.instrument('GPIB0::%i'%GPIB_No, delay=0.1, term_chars='\n')
        self.sensvec=[2e-9,5e-9,1e-8,2e-8,5e-8,1e-7,2e-7,5e-7,1e-6,2e-6,5e-6,1e-5,2e-5,5e-5,1e-4,2e-4,5e-4,1e-3,2e-3,5e-3,1e-2,2e-2,5e-2,1e-1,2e-1,5e-1,1]
        self.tcvec=[10e-6,30e-6,100e-6,300e-6,1e-3,3e-3,10e-3,30e-3,100e-3,300e-3,1,3,10,30,100,300,1e3,3e3,1e4,3e4]
        self.resvec=['HR','N','LN']
        
        self.clear_buffer()         # to avoid errors by old commands
        
        for i in range(4):          # sets all aux outputs to 0V
            self.set_aux_output(i+1,0)
        
        self.sens=self.get_sens()
        self.offs=self.get_offs(1)
        self.exp=self.get_exp(1)
        self.phase=None
        self.reading=self.read()
    
    def get_status(self,bit=4):
        """Queries the Serial Poll Status Byte with given Bit.
        Returns True, if Bit was set.
        0 SCN No Scan in progress
        1 IFC No command execution in progress
        2 ERR Enabled Bit in error status byte is set
        3 LIA Enabled Bit in LIA is set
        4 MAV Interface Output Buffer is NON-EMPTY (standard)
        5 ESB Enabled Bit in standard status byte is set
        6 SRQ Service Request occured
        7 --- Unused"""
        answer = self.lockin.ask("*STB? %i"%(bit))
        if answer == "1":
            return True
        if answer == "0":
            return False
        print "Statusbit %i: "%(bit)+answer
        return False
    
    def clear_buffer(self):
        answer = self.get_status(bit=4)
        while answer:
            self.lockin.read()
            answer = self.get_status(bit=4)
    

    def get_freq(self):
        """read frequency"""
        self.freq=self.lockin.ask('freq?')
        return self.freq
   
    def set_freq(self, frequency):
        """set frequency in Hertz, from 0.001Hz to 102000Hz"""
        self.lockin.write('FREQ'+str(frequency))    
    
    def get_ac(self):
        """read ac wobble voltage"""
        self.ac=float(self.lockin.ask('slvl?'))
        return self.ac

    def set_ac(self, Uwobble):
        """set ac wobble voltage in Volts, from 0.004V to 5.000V"""
        self.lockin.write('SLVL'+str(Uwobble))

    def get_sens(self):
        """return the sensitivity setting of the lockin"""
        answer=self.lockin.ask('sens?') 
        sensno=int(answer)
        self.sens=float(self.sensvec[sensno])
        return self.sens
    
    def get_sens_index(self):
        """return the sensitivity setting of the lockin"""
        answer=self.lockin.ask('sens?')
        sensno=int(answer)
        return sensno

    def set_sens(self, sensitivity):
        """set sensitivity value of SR830 lockin in V
           allowed values are 0 .. 26 corresponding to
           2e-9, 5e-9, 1e-8, 2e-8, 5e-8 .. 1e-1, 2e-1, 5e-1, 1 V"""
        self.lockin.write('SENS'+str(self.sensvec.index(float(sensitivity))))
        self.get_sens()

    def get_tc(self):
        """return the time constant setting of the lockin in seconds"""
        tcno=int(self.lockin.ask('oflt?'))
        self.tc=self.tcvec[tcno]
        return self.tc
    
    def get_tc_index(self):
        """return the time constant setting of the lockin in seconds"""
        tcno=int(self.lockin.ask('oflt?'))
        return tcno

    def set_tc(self, timeconstant):
        """set time constant to a value of 10mus....30ks"""
        self.lockin.write('OFLT'+str(self.tcvec.index(float(timeconstant))))
        self.get_tc()

    def get_reserve(self):
        """return the reserve mode: high reserve(i=0), normal (i=1) or Low Noise (i=2)"""
        resno=int(self.lockin.ask('rmod?'))
        self.res=self.resvec[resno]
        return self.res

    def set_reserve(self, reserve):
        """set reserve=High reserve='HR',Normal='N' or Low Noise='LN'"""
        self.lockin.write('RMOD'+str(self.resvec.index(reserve)))
        self.get_reserve()
                
    def get_offs(self, signal):
        """return the offset in the current signal"""
        offant = self.lockin.ask('oexp?'+str(signal))
        offantsplit=[float(i) for i in offant.split(',')]
        self.offs=offantsplit[0]
        return self.offs

    def get_exp(self, signal):
        """return expansion of lockin signal "signal no" (1-4)"""
        offant = self.lockin.ask('oexp?'+str(signal))
        offantsplit =[float(i) for i in offant.split(',')]
        self.exp=int(10**offantsplit[1])
        return self.exp

    def set_expoffs(self, channel, offset, expansion):
        """set channel (1=X, 2=Y, 3=R), offset (-105%<x<105%) and expansion (0=1, 1=10, 2=100)"""
        self.lockin.write('oexp'+str(channel)+','+str(offset)+','+str(expansion))

    def auto_offs(self, expansion=0):
        """auto-offset und expandiere output auf "expasion=X (0=1, 1=10, 2=100)
           NOTE: the current reading will be taken as offset"""
        self.lockin.write('oexp1,0,0')
        self.lockin.write('aoff1')
        fo=self.lockin.ask('oexp?1')
        a=fo.split(',')
        self.lockin.write('oexp1,'+a[0]+','+str(expansion))    
        print a[0],expansion

    def autophase(self):
        """perform "autophase" """
        self.lockin.write('aphs')
    
    def update(self):
        """reads X, theta, offset and epansion, performs autophase"""
        self.autophase()
        self.get_sens()
        self.get_offs(1)
        self.get_exp(1)
        self.read()        

    def read(self):
        """returns current x value of lockin"""
        list=self.lockin.ask("SNAP?1,4") #records values: 1=x, 2=y, 3=R, 4=theta, 5,6,7,8=Aux In 1,2,3,4, 9=Ref.frequency, 10=CH1 display, 11=CH2 Display
        values=list.split(',')
        self.reading=float(values[0])
        self.phase=float(values[1])
        return self.reading
    
    def get_values(self, _1=1,_2=2,_3=4,_4=9,_5=10,_6=11):
        """returns current x value of lockin
            1=x, 2=y, 
            3=R, 4=theta, 
            5,6,7,8=Aux In 1,2,3,4, 
            9=Ref.frequency, 
            10=CH1 display, 11=CH2 Display"""
        list=self.lockin.ask("SNAP?%i,%i,%i,%i,%i,%i"%(_1,_2,_3,_4,_5,_6)) #records values: 1=x, 2=y, 3=R, 4=theta, 5,6,7,8=Aux In 1,2,3,4, 9=Ref.frequency, 10=CH1 display, 11=CH2 Display
        values=[float(x) for x in list.split(',')]
        return values
    
    def get_phase(self):
        """returns current phase"""
        list=self.lockin.ask("SNAP?1,3,4") #records values: 1=x, 2=y, 3=R, 4=theta, 5,6,7,8=Aux In 1,2,3,4, 9=Ref.frequency, 10=CH1 display, 11=CH2 Display
        values=list.split(',')
        self.phase=values[2]
        return self.phase

    def nthharmonic(self, nnn):
        """set nth harmonic, with nnn=1,2,3,..."""
        self.lockin.write('HARM'+str(nnn))
        self.nthharm=self.lockin.ask('harm?')
        return self.nthharm
    
    def set_aux_output(self, port, value):
        """Sets desired port 1,2,3,4 to given voltage value"""
        self.lockin.write('AUXV %i,%f'%(port,value))
    
    def get_aux_input(self, port):
        """Gets the value of an aux input port 1,2,3,4"""
        answer = self.lockin.ask('OAUX? %i'%(port))
        return float(answer)    


class ni_daq:
    def __init__(self):
        self.data = []
        for i in xrange(4):
            self.data.append([])
        self.stop = False
        thread.start_new_thread(self.periodic,())
    
    def stop(self):
        self.stop = True
    
    def periodic(self, interval=0.1, clock_rate=50000):
        """Keeps running DAQ-Thread and fetches Data at given rate"""
        task = self.AnalogInputTask()
        task.create_voltage_channel('Dev1/ai0', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier
        task.create_voltage_channel('Dev1/ai4', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier
        task.create_voltage_channel('Dev1/ai5', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier

        task.configure_timing_sample_clock(rate = clock_rate)
        task.set_buffer_size(100000)
        
        task.start()         
        self.last_timestamp = time.time()
        while not self.stop:
            # get acquired data
            data = task.read(None,fill_mode='group_by_channel',timeout=100)
            #print repr(data)
            # gather data for time interpolation
            ts_backup = self.last_timestamp
            self.last_timestamp = time.time()
            sample_count = len(data[0])
            try:
                #data.append(np.linspace(ts_backup,self.last_timestamp,sample_count))
                data = np.concatenate((data,[np.linspace(ts_backup,self.last_timestamp,sample_count)]))
                #print "merged:"
                #print data                
                
                #data.expand(np.linspace(ts_backup,self.last_timestamp,sample_count))
            except Exception,e:
                print e
            for i in xrange(len(self.data)):
                self.data[i] += list(data[i])
            #print self.data
            time.sleep(interval)
            
            #[1,2,3].append([4,5]) --> [1,2,3,[4,5]]
            #[1,2,3] + [4,5] == [1,2,3,4,5]
            
            #print np.average(data,1)
            print len(self.data[0])
        
        del task
    """        while not self.stop:
            # get acquired data
            data = np.array(task.read(None,fill_mode='group_by_channel',timeout=100))
            # gather data for time interpolation
            ts_backup = self.last_timestamp
            self.last_timestamp = time.time()
            sample_count = len(data[0])
            # interpolate time for data
            #data = data.expand(np.linspace(ts_backup,self.last_timestamp,sample_count).transpose())
            try:
                print "raw data:"
                print data
                print "timestamps:"
                print np.linspace(ts_backup,self.last_timestamp,sample_count)
                
                #data = data.append(np.linspace(ts_backup,self.last_timestamp,sample_count))
                np.concatenate((data,np.linspace(ts_backup,self.last_timestamp,sample_count)))
                print "merged:"
                print data                
                
                #data.expand(np.linspace(ts_backup,self.last_timestamp,sample_count))
            except Exception,e:
                print e"""            
        
        
   
    def get_value(self, samples=1000, clock_rate = 100000.0):
        
        task = self.AnalogInputTask()
        task.create_voltage_channel('Dev1/ai0', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier
        task.create_voltage_channel('Dev1/ai4', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier
        task.create_voltage_channel('Dev1/ai5', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier

        task.configure_timing_sample_clock(rate = clock_rate)
        #task.register_every_n_samples_event(self.print_data,100,0,None)
        task.set_buffer_size(100000)
        
        task.start()   
        
        time.sleep(3)
        try:
            data2 = task.read(None,fill_mode='group_by_channel',timeout=100)
            print data2
        except:
            print "noeoeoeoe"
        finally:
            pass
            
        print task.get_samples_per_channel_available()
        task
        return_values = np.average(data2,1)
        
        del task
        #print np.average(data2,1)
        #print np.average(data3,1)
        #return 0
        return return_values
    
    def print_data(self, task, event_type, samples, cb_data):
         data = task.read(samples,fill_mode='group_by_channel',timeout=100)
         
         #print "print_data:"
         print np.average(data,1)
         return 0

    def get_values(self, samples=1, clock_rate = 100000.0):
        
        task = AnalogInputTask()
        task.create_voltage_channel('Dev1/ai1', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier
        task.create_voltage_channel('Dev1/ai2', terminal = 'diff', min_val=-10, max_val=10)    # voltage amplifier 
        task.create_voltage_channel('Dev1/ai3', terminal = 'diff', min_val=-10, max_val=10)    # yokogawa 
        task.configure_timing_sample_clock(rate = clock_rate, samples_per_channel=samples)
        task.start()        
        data = task.read(samples, fill_mode='group_by_channel',timeout=100)

        
        del task
        #print data

        #import pylab as pl
        #pl.autoscale(axis='y')
        #pl.plot(data[channel])
        #pl.show()
        
        return data
            

    def show_fft(self, samples=1000, channel=0, clock_rate = 2000.0):
        import pylab as pl
    
        task = self.AnalogInputTask()
        task.create_voltage_channel('Dev1/ai1', terminal = 'rse', min_val=-10, max_val=10)    # current amplifier

        task.configure_timing_sample_clock(rate = clock_rate)
        task.start()        
        data = task.read(samples, fill_mode='group_by_channel',timeout=1000)
        del task

        myfft = np.fft.fftshift(np.fft.fft(data[channel]))
        freq = np.fft.fftshift(np.fft.fftfreq(len(data[0]),1.0/clock_rate))
        
        pl.xlim((0,clock_rate/2))  
        pl.autoscale(axis='y')
        pl.ylim(ymin=0)
        pl.plot(freq,myfft)
        pl.show()


class Neocera:
    def __init__(self, GPIB_No=9):
        self.nc=visa.instrument('GPIB0::%i'%GPIB_No, delay=0.1, term_chars='\n')
        self.temperature1 = 0
        self.temperature2 = 0
    
    def get_temperature(self,channel=2):
        """Asks for a temperature measurement"""
        answer = self.nc.ask('QSAMP?%i;'%channel)
        try:
            temp = float(answer[0:-2])
        except Exception,e:
            log("Couldn't retrieve T",e)
            temp = 0
            
        if channel == 1:
            self.temperature1 = temp
        else:
            self.temperature2 = temp
        return temp
    
    def send_calibration(self):
        """sends a calibration table to neocera. please delete an existing table before.
        be sure not to send an termination ";" after every subcommand!"""
        #calibration_probe2 = np.array([[104,300],[104.5,280],[105,260],[106,240],[107,220],[108,200],[108.5,190],[109,180],[110,170],[111,160],[112,150],[113,140],[114,130],[116,120],[118,110],[120,100],[121,95],[122,90],[124,85],[126,80],[128,75],[130,70],[132,65],[135,60],[139,55],[144,50],[149,45],[154,40],[162,35],[174,30],[179,28],[184,26],[194,24],[204,22],[214,20],[229,18],[245,16],[273,14],[304,12],[354,10],[394,9],[444,8],[524,7],[629,6],[704,5.5],[954,4.5],[1054,4.2],[1154,4],[1304,3.75],[1504,3.5],[1704,3.25],[2104,3],[2404,2.8],[2954,2.6],[3504,2.4],[4404,2.2],[5654,2],[6804,1.9],[8004,1.8],[10004,1.7],[12404,1.6],[14004,1.55],[20563.86,1.4],[28062.44,1.3],[40143.44,1.2],[60929.16,1.1]])
        calibration_ruo2 = np.array([[1280.23, 300.0], [1280.973, 280.0], [1281.822, 260.0], [1282.802, 240.0], [1283.947, 220.0], [1285.305, 200.0], [1286.083, 190.0], [1286.942, 180.0], [1287.894, 170.0], [1288.958, 160.0], [1290.152, 150.0], [1291.505, 140.0], [1293.052, 130.0], [1294.837, 120.0], [1296.923, 110.0], [1299.396, 100.0], [1300.814, 95.0], [1302.378, 90.0], [1304.113, 85.0], [1306.049, 80.0], [1308.225, 75.0], [1310.69, 70.0], [1313.506, 65.0], [1316.758, 60.0], [1320.558, 55.0], [1325.062, 50.0], [1330.493, 45.0], [1337.179, 40.0], [1345.632, 35.0], [1356.685, 30.0], [1362.129, 28.0], [1368.351, 26.0], [1375.535, 24.0], [1383.93, 22.0], [1393.881, 20.0], [1405.878, 18.0], [1420.651, 16.0], [1439.325, 14.0], [1463.742, 12.0], [1497.156, 10.0], [1519.009, 9.0], [1545.916, 8.0], [1579.928, 7.0], [1624.403, 6.0], [1652.253, 5.5], [1725.066, 4.5], [1753.167, 4.2], [1774.075, 4.0], [1803.124, 3.75], [1836.025, 3.5], [1873.622, 3.25], [1917.031, 3.0], [1956.936, 2.8], [2002.539, 2.6], [2055.19, 2.4], [2116.717, 2.2], [2189.645, 2.0], [2231.454, 1.9], [2277.578, 1.8], [2328.744, 1.7], [2385.85, 1.6], [2416.972, 1.55], [2522.709, 1.4], [2605.77, 1.3], [2701.67, 1.2], [2813.734, 1.1]])
        
        j = 0
        # 1,91571
        #command = 'SCALT2,1,AB100,-1.0,' # works, you have to set the first two parameters manually
        command = 'SCALT2,1,RuO2,-1.0,' # works, you have to set the first two parameters manually
        values = calibration_ruo2
        for i in range(len(values)):
            command += '%.1f,%.1f,'%(float(values[i][1]), float(values[i][0]))
            j += 1
            if j > 10:
                self.nc.write(command)
                print command
                command = ""
                j = 0
                time.sleep(3)
    
        if j > 0: # write last tuples
            self.nc.write(command+'$;')
        else: # or finish
            self.nc.write("$;")
class FEMTO_GAIN:
    def __init__(self, interface=None):

        self.data = {}
        self.data_lock = thread.allocate_lock()
        self.data["timestamp"] = []
        self.data["channela"] = []
        self.data["channelb"] = []
        thread.start_new_thread(self.femto_thread,(0.1,))        
        
        self.interface = interface
        self.reset()

    def reset(self):
        self.ampl_a = 0
        self.ampl_b = 0
        self.update()
    
    def set(self, a=0, b=0):
        self.ampl_a = a
        self.ampl_b = b
    
    def get(self):
        return (self.ampl_a, self.ampl_b)
    
    def update(self):
        value = self.ampl_a + (self.ampl_b << 4)
        self.interface.set_dio(value)
        
        
    def increase_amplification(self, channel=0):
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
        self.update()
    
    def decrease_amplification(self, channel=0):
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
        self.update()

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
            self.data["channela"] = []
            self.data["channelb"] = []
        # release lock
        self.data_lock.release()
        return return_data    
    
    def femto_thread(self, delay=0.05):
        log("Femto Thread started!")
        
        while not stop:
            self.data_lock.acquire()
            self.data["timestamp"].append(time.time())
            self.data["channela"].append(self.ampl_a)
            self.data["channelb"].append(self.ampl_b)
            self.data_lock.release()
            
            time.sleep(delay)
            
            
class FEMTO_LUCY:          
    """Has to be used with luci.py (femto interface)"""
    def __init__(self, index, name="UNDEFINED"):
        self.index = index
        self.name = name
        self.amplification = 1
        luci.init()
        self.config(3,True,True)
    
    def get_adapters(self):
        luci.list_adapters()
    
    def config_i_amplifier(self, exponent, low_noise=True, dc=True):
        """sets the amplification level of variable gain current amplifier.
        low noise: 10^3-10^9
        high speed: 10^5-10^11"""
        if dc:
            coupling = "DC"
        else:
            coupling = "AC"
        
        if low_noise:
            if exponent < 3:
                exponent = 3
            if exponent > 9:
                exponent = 9
            backup_exponent = exponent
            exponent = exponent - 3
            mode = "Low Noise"
        else:
            if exponent < 5:
                exponent = 5
            if exponent > 11:
                exponent = 11   
            backup_exponent = exponent
            exponent = exponent - 5
            mode = "Highspeed"

        log("Set Amplification of %s to 10^%i,%s,%s"%(self.name,backup_exponent,mode,coupling))
        self.amplification = backup_exponent
        
        low_byte = exponent & 7        
        if dc:
            low_byte = low_byte | 8
        if low_noise:
            low_byte = low_byte | 16
        luci.write_bytes(self.index,low_byte,0)
    
    def get_exponent(self):
        return self.amplification
        
    def overloaded(self):
        return luci.get_status_pin5(self.index)
        
#try:
#    sr830_first=SR830(10)   
#    log("SR830 LockIn First")
#except Exception,e:
#    log("SR830 LockIn not found!",e)
#    sr830_first=None   
#try:    
#    sr830_second=SR830(10)
#    log("SR830 LockIn Second")
#except Exception,e:
#    log("SR830 LockIn not found!",e)
#    sr830_second=None  
#try:
#    neocera=Neocera()
#    log("Neocera Found")
#except Exception,e:
#    log("Neocera not found!",e)
#    neocera=None    
#try:
#    daq = ni_daq()
#    log("NI DAQ found")
#except Exception,e:
#    log("NI DAQ not found!",e)
#    daq=None 

#try:
#    agilent_new = Agilent34401A(22)
#    log("Agilent34401A-Mode!")
#    log("Agilent34410A found")
#except Exception,e:
#    log("Agilent34410A not found!",e)
#    agilent_new=None 
#try:
#    agilent_old = Agilent34401A(23)
#    log("Agilent34401A found")
#except Exception,e:
#    log("Agilent34401A not found!",e)
#    agilent_old=None


"""    
try:
    lockin=ZURICH()
    log("LockIn Found")
except Exception,e:
    log("LockIn not found!",e)
    lockin=None 

try:
    femto=FEMTO_GAIN(lockin)
    log("Femto Started")
except Exception,e:
    log("Femto Failed!",e)
    femto=None 
     

try:
    yoko=GS200(14)
    log("Yokogawa Voltage Source found")
except Exception,e:
    log("Yokogawa Voltage Source not found!",e)
    yoko=None
    

try:
    magnet=Magnet(26)
    log("Magnet found")
except Exception,e:
    log("Magnet not found!",e)
    magnet=None   
 

try:
    lakeshore=LAKESHORE(12)
    log("Lakeshore found")
except Exception,e:
    log("Lakeshore not found!",e)
    lakeshore=None
"""

"""

try:
    levelmeter=ILM210()
    log("Levelmeter Port Found")
except Exception,e:
    log("Levelmeter not found!",e)
    levelmeter=None 
    """