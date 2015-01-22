# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 12:23:15 2012
All rights reserved by David Weber
@author: David Weber
"""

import time

import os
import inspect
import numpy as np

# config file
from configobj import ConfigObj
# beeping
import winsound
#import tables



def interpolate(x=[],xp=[],fp=[],scale_y=1.0):
    """interpolates using np.interp() with some extras"""
    min_index = min(len(xp),len(fp))-1
    
    xp = np.array(xp)
    fp = np.array(fp)/scale_y
    
    interp_array = np.interp(x,xp[0:min_index],fp[0:min_index])
    return interp_array


def interp_breaking_trace(t_start=0,t_end=1,data={},steps=0.1):
    """Sets diagram to a Opening/Closing Trace"""
    #return_dict = {}
    try:
        #x_list = np.arange(t_start,t_end,steps)
        for k,v in data.items():
            #temp_data = interpolate(x_list, data["agilent_voltage_timestamp"], data["agilent_voltage_voltage"])
            #voltage_list = interpolate(x_list, data["agilent_voltage_timestamp"], data["agilent_voltage_voltage"])
            pass
    except Exception,e:
        log("Interpolating Failed",e)       


def round_to_digits(x, digits=1):
    """ Rounds the value 'x' to the in 'digits' specified numbers of digits."""
    if x > 1e-6:
        return round(x, -int(np.floor(np.log10(abs(x)))) + (digits - 1))
    else:
        return round(x, digits)

def export_html(parent, path="C:\wamp\www\\", data_list=None):
    from PyQt4.QtCore import QPoint
    form_objects = inspect.getmembers(parent)
    
    f = open(path+"index.html","w")
    f.write("<html><head><title>Andreev Measurement</title>")
    f.write("<style type=\"text/css\">\n")
    
    # background
    f.write("body {background-color: #BBBBBB}\n")   
    
    
    # inputs
    for element in form_objects:
        try:
            if element[1].__class__.__name__ == 'QLineEdit':
                f.write("form #%s {position: absolute; top: %ipx; left: %ipx; width: %ipx; height: %ipx}\n"%(
                    element[1].objectName(),element[1].mapToGlobal(QPoint(0,0)).y(),element[1].mapToGlobal(QPoint(0,0)).x(),int(element[1].width()),int(element[1].height())))
            if element[1].__class__.__name__ == 'CurveWidget':
                f.write("form #%s {position: absolute; top: %ipx; left: %ipx; width: %ipx; height: %ipx}\n"%(
                    element[1].objectName(),element[1].mapToGlobal(QPoint(0,0)).y(),element[1].mapToGlobal(QPoint(0,0)).x(),int(element[1].width()),int(element[1].height())))
        except Exception,e:
            print e
            print str(element[1].__class__.__name__)
            f.write("dada!")
            pass
    
    f.write("</style>\n")
    f.write("</head>")
    
    
    f.write("<body>\n")
    f.write("<form>\n")
    
    for element in form_objects:
        try:
            if element[1].__class__.__name__ == 'QLineEdit':
                f.write("<div id=\"%s\"><input type=\"text\" name=\"%s\" value=\"%s\" style=\"width: %ipx;\"/></div>\n"%(
                    str(element[1].objectName()),str(element[1].objectName()),str(element[1].text()),element[1].width()))
            if element[1].__class__.__name__ == 'CurveWidget':
                element[1].plot.save_widget(path+str(element[1].objectName())+".png")
                f.write("<img src="+str(element[1].objectName())+".png\" />\n")
        except Exception,e:
            log("Failed Writing Objects HTML",e)
        
    f.write("</form></body></html>")
    f.flush()
    
    try:
        f = open(path+"messung.html","w")
        f.write("<html><head><title>Andreev Measurement</title>")
        f.write("<meta http-equiv=\"refresh\" content=\"15\" >\n")
        f.write("\n")
        f.write("</head><body>\n")
        f.write("<img src=\"http://134.34.143.54/cw1.png\" />\n")
        f.write("<img src=\"http://134.34.143.54/cw2.png\" />\n")
        f.write("<img src=\"http://134.34.143.54/cw3.png\" />\n")
        f.write("<img src=\"http://134.34.143.54/cw4.png\" />\n")
        f.write("<img src=\"http://134.34.143.54/cw5.png\" />\n")
        f.write("<img src=\"http://134.34.143.54/cw6.png\" />\n")
        f.write("<img src=\"http://134.34.143.54/helium/curvewidget.png\" />\n")
        f.write("\n")
        if not data_list == None:
            pass
        f.write("\n")
        f.write("</body></html>")
        f.flush()
        f.close()
    except Exception,e:
        log("Failed to write messung.html",e)
    finally:
        f.close()



def voltage_ramp(_min=-1,_max=1,_step=0.1,_circular=True):
    """Returns a voltage ramp which has 0-max-0-min-0 shape.
    If min/max cannot be devided by step, 
    it will be added if error > _treshold"""
    
    treshold = 0.1
    
    data = []
    
    if _circular:
        value = 0
        while True:
            data.append(round(value,10))
            # if next step issnt fitting to range
            if value > _max-_step:
                # if last step is more than 10% away of endpoint
                if value < _max-_step*treshold:
                    data.append(_max)
                break
            value = value+_step
        
        while True:
            data.append(round(value,10))
            # if next step issnt fitting to range
            if value < _min+_step:
                # if last step is more than 10% away of endpoint
                if value > _min+_step*treshold:
                    data.append(_min)
                break
            value = value-_step
        
        while True:
            data.append(round(value,10))
            # if next step issnt fitting to range
            if value >= -_step:
                # if last step is more than 10% away of endpoint
                if value < -_step*treshold:
                    data.append(0)
                break
            value = value+_step
    else:
        value = _min
        while True:
            data.append(round(value,10))
            # if next step issnt fitting to range
            if value > _max-_step:
                # if last step is more than 10% away of endpoint
                if value < _max-_step*treshold:
                    data.append(_max)
                break
            value = value+_step
    
    return data

def app_init(main):
    main.ui.editOffsetAux0_0.setText("asdf")


def write_config(form):
    config = ConfigObj()
    config.filename = r"C:\Users\David Weber\Desktop\andreev\config.ini"
    
    form_objects = inspect.getmembers(form)
    config['QLineEdit'] = {}
    config['QTabWidget'] = {}
    config['QComboBox'] = {}
    config['QCheckBox'] = {}
    config['QTextEdit'] = {}
    for element in form_objects:
        try:
            if element[1].__class__.__name__ == 'QLineEdit':
                config['QLineEdit'][str(element[1].objectName())] = element[1].text()
             
            if element[1].__class__.__name__ == 'QTabWidget':
                config['QTabWidget'][str(element[1].objectName())] = element[1].currentIndex()
            
            if element[1].__class__.__name__ == 'QComboBox':
                config['QComboBox'][str(element[1].objectName())] = element[1].currentIndex()
            
            if element[1].__class__.__name__ == 'QCheckBox':
                config['QCheckBox'][str(element[1].objectName())] = element[1].isChecked()
                
            if element[1].__class__.__name__ == 'QTextEdit':
                config['QTextEdit'][str(element[1].objectName())] = element[1].toPlainText()
        except Exception,e:
            print e
    
    config.write()

def read_config(form):
    config = ConfigObj(r"C:\Users\David Weber\Desktop\andreev\config.ini")
    
    form_objects = inspect.getmembers(form)
    for element in form_objects:
        try:
            if element[1].__class__.__name__ == 'QLineEdit':
                element[1].setText(str(config['QLineEdit'][str(element[1].objectName())]))
             
            if element[1].__class__.__name__ == 'QTabWidget':
                element[1].setCurrentIndex(int(config['QTabWidget'][str(element[1].objectName())]))
            
            if element[1].__class__.__name__ == 'QComboBox':
                element[1].setCurrentIndex(int(config['QComboBox'][str(element[1].objectName())]))
                
            if element[1].__class__.__name__ == 'QCheckBox':
                element[1].setChecked(config['QCheckBox'][str(element[1].objectName())] == "True")
                
            if element[1].__class__.__name__ == 'QTextEdit':
                element[1].setPlainText(str(config['QTextEdit'][str(element[1].objectName())]))
        except Exception,e:
            print 'Couldn''t find item!',e
    
    config.write()


old_logs = []
logfile = None
def set_logfile(filename):
    """This function opens a global logfile
    
    Parameters
    ----------
    filename : string
        The name of the logfile.
    """
    global logfile
    logfile = open(filename,"a")

def close_logfile():
    """ This function closes the logfile opened with set_logfile"""
    global logfile
    try:
        if not logfile == None:
            logfile.flush()
            logfile.close()
    except Exception,e:
        log("No Logfile to close!",e)
    logfile = None
    
def save_data(filename, saving_data):
    """This function writes the data into the file.
    
    The function is mainly called by the different measurement functions in
    run_andreev.py.
    
    Parameters
    ----------
    filename : file handle
        The file handle of the file in which the data should be written.
    saving_data : float array
        Thw whole data for writing into a file.
    """
    try:
        if not filename == None:
            for i in range(len(saving_data[0])):  # for all new data rows
                line = ""
                for j in range(len(saving_data)): # for all columns
                    line = line + "%15.15f\t"%(saving_data[j][i])
                line = line + "\n"
                filename.write(line)
    except Exception,e:
        #print "%i %i %i %i"%(len(saving_data),len(saving_data[0]),len(saving_data[1]),len(saving_data[2]))
        log("Error while saving data.",e)
        

    
def log(message, exception=None, force=False):
    """ This function manage the log an prints onto the output and write it 
    into the log file.
    
    Before making a new log entry the function checks if there was the same 
    message in the last 10 seconds. If this is the case the message no new
    log entry is made. If it is a important message you can force ist with 
    the parameter 'force'.
    When the message did not appeared in the last 10 seconds a neew log entry
    is build, which may contain an exception. This log entry is printed on
    the standard output and, if there is an log file, into the log file.
    
    Parameters
    ----------
    message : string
        The message which should be printed and written into the log file.
    exception : exception, optional
        If an exception was the problem, which is reported, this parameter 
        contain the exception.
    force : logical, optional
        This parameter forces the function to display the message, even if it
        was displayed as the last message."""
        
    # time to do not show same log again
    cold_time = 10
    # delete old apperances
    i = 0
    while True:
        if i >= len(old_logs)-1:
            break
        if old_logs[i][1] <= time.time()-cold_time:
            del old_logs[i]
        else:
            i += 1    
    
    # check for older appearance
    was_before = False
    for msg in old_logs:
        if msg[0] == message:
            was_before = True       
    if force:
        was_before = False
    # if not yet, show message, create new log entry    
    if not was_before:    
        if exception == None:
            print time.ctime(time.time()) + ': ' + message
            if not logfile == None:
                logfile.write(time.ctime(time.time()) + ': ' + message + '\n')
        else:
            print time.ctime(time.time()) + ': ' + message + ',' , exception
            if not logfile == None:
                logfile.write(time.ctime(time.time()) + ': ' + message + ', ' + str(exception) +'\n')
        old_logs.append([message,time.time()])


def find_min(L, value):
    iterations = 0
    maxindex = len(L) - 1
    if len(L) == 0 or L[0] >= value:
        return 0
    if L[-1] <= value:
        #log("Last value is larger than wanted value!")
        return maxindex

    index = 0
    while index <= maxindex:
        center = index + ((maxindex - index)/2)
        if L[center] <= value and L[center+1] > value:
            return center   
        elif L[center] > value:
            maxindex = center - 1
        else:
            index = center + 1
        iterations += 1
    return 0
  
    
def beep():
    try:
        winsound.Beep(1000,300)
    except Exception,e:
        log("Beep",e)

def ensure_dir(f):
    """This function checks if a special directory exists and when not build it.
    
    Parameters
    ----------
    f : string
        The whole path to the directory.
    """
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)        
        


def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
    
def average_chunks(l,n):
    """averages list l with help of function chunks(l,n) to mostly
    equal steps of length n"""
    my_list = list(chunks(l,n))

    averaged_values = []        
    for x in my_list:
        averaged_values.append(np.average(x))
    
    return averaged_values