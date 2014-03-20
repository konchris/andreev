# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 20:54:53 2012

@author: David
AVERAGING of several .cvs
"""

import os
import csv
import numpy
import math
import pylab
import scipy
import matplotlib
import fit


def plot(path = 'Z:\\dweber\\data_z1024\\NX28\\Pad 13',
         comment_string = '#',
         fixed_maximum = 0, # 0=nothing, -1 fix to maximum, >0 set max
         ):
    
    print path
    
# add backslash if needed+021.,µ nbvcx
    if path[-1] != '\\':
        path = path+'\\'
# get all the files in directory
    file_list = os.listdir(path)
    if path[-1] != '\\':
        path = path+'\\'
    files = []
    for i in range(len(file_list)):
        if file_list[i][-4:] == '.csv':
            files.append(path+file_list[i])
# sort them
    files.sort()
    
# extract data
    data = []
    for i in range(len(files)):
        print files[i]
        f = open(files[i], "rU")
        row_list = f.readlines()
        
        # delete comment lines
        j=0
        while j < len(row_list):
            row = row_list[0]
            if row[0] == comment_string:
                row_list.pop(0)
            else:
                break
            j = j + 1
        
        # use csv reader to get csv data
        csv_file = csv.reader(row_list, delimiter='\t', quotechar=comment_string)#, lineterminator = '\n')
        try:
            voltage = []
            current = []
            first = []
            second = []
            for row in csv_file:
                voltage.append(row[0])
                current.append(row[1])
                first.append(row[2])
                
                try:
                    second.append(row[3])
                except:
                    second.append(0)

                
            data.append([voltage,current,first,second])

            
        except Exception,e:
            print e
        
    
# if maximum should be found    
    if fixed_maximum < 0:
        max_i = 0
        for i in range(len(data)):
            for x in data[i][1]:
                if abs(float(x)) > max_i:
                    max_i = abs(float(x))
                    
           
        
# real plotting   

    # For numerical differentiation see this flag:
    numerical_diff = False 
     
    for i in range(len(data)):  
        _v = [float(x) for x in data[i][0]]
        _i = [float (x) for x in data[i][1]]
        _s = [float (x) for x in data[i][2]]
        if numerical_diff:
            _ds = [float (x) for x in data[i][0]]
        else:
            _ds = [float (x) for x in data[i][3]]
        pylab.clf()
        
        #pylab.rcParams.update({'text.usetex': True}) 
        
        pylab.subplots_adjust(hspace=0.6,wspace=0.5)

#-------- FIRST ------------------
        pylab.subplot(2,2,1)
        pylab.title("Current")


        (voltage,voltage_prefix) = get_si_scaling(_v)
        (current,current_prefix) = get_si_scaling(_i)
        try:
            pylab.plot(voltage,current)
            pylab.xlabel('Voltage (%sV)'%(voltage_prefix))
            pylab.ylabel('Current (%sA)'%(current_prefix))
            pylab.grid(True)
        except:
            pass
    
 
#------- SECOND ----------------
        pylab.subplot(2,2,2)
        pylab.title("Fowler-Nordheim")
        
        pylab.grid(True)
        
        _v2 = _v[:]
        _i2 = _i[:]

        j=0
        while j < len(_v2):
            try:
                _v2[j] = 1/_v2[j]
            except:  
                _v2.pop(j)
                _i2.pop(j)
                j=j-1
            j=j+1
                
        _v2 = numpy.array(_v2)
        _i2 = numpy.array([abs(x) for x in _i2])
        #p = numpy.polyfit(_v2,_i2,3)
        #fn_p = numpy.polyval(p,_v2)

        
        _i2 = numpy.log(abs(_i2*_v2*_v2))
        
        j = -1
        for k in range(len(_v2)-1):
            if ((_v2[k] < 0) and (_v2[k+1] > 0)) or ((_v2[k] > 0) and (_v2[k+1] < 0)):
                j=k
        if j != -1:
            try:
                pylab.plot(_v2[0:j],_i2[0:j],_v2[j+1:],_i2[j+1:])
            except:
                pass
        else:
            try:
                pylab.plot(_v2,_i2)
            except:
                pass
        pylab.xlabel('Voltage (1/V)')
        pylab.ylabel(r'Current ($\ln\frac{I}{V^2}$)')
        pylab.xlim(-20,20)
        
#-------- THIRD ---------------
        pylab.subplot(2,2,3)
        pylab.title("Conductance")
        pylab.grid(True)
        
        _v3 = _v[:]
        _i3 = _i[:]
        if numerical_diff:
            _s3 = _v3[:]
        else:
            _s3 = _s[:]
       
        _v3 = numpy.array(_v3)
        _i3 = numpy.array(_i3)
        _s3 = numpy.array(_s3)

        
       
        
        if numerical_diff:
            for k in range(len(_v3)-1):
                try:
                    value = (_i3[k]-_i3[k+1])/(_v3[k]-_v3[k+1])
                    _s3[k] = value
                except:
                    print "strange"
                    _s3[k] = 0
   
            j = 0
            while True:
                if math.isnan(_s3[j]) or math.isinf(_s3[j]):
                    _v3 = numpy.delete(_v3,[j])
                    _s3 = numpy.delete(_s3,[j])
                else:
                    j=j+1
                if j >= len(_s3):
                    break
        
            _v3 = numpy.delete(_v3,[len(_v3)-1])
            _s3 = numpy.delete(_s3,[len(_s3)-1])
        
      
                                    
        (voltage,voltage_prefix) = get_si_scaling(_v3)
        (conductance,conductance_prefix) = get_si_scaling(_s3)
        try:
            pylab.plot(voltage,conductance)
        except:
            pass
        pylab.xlabel('Voltage (%sV)'%(voltage_prefix))
        pylab.ylabel('Conductance (%sS)'%(conductance_prefix))

#-------- FOURTH --------------
        pylab.subplot(2,2,4)
        pylab.title("$\mathrm{d}^2I/\mathrm{d}U^2$")      
        pylab.grid(True)
                                    
        (voltage,voltage_prefix) = get_si_scaling(_v)
        (ds,ds_prefix) = get_si_scaling(_ds)
        try:
            pylab.plot(voltage,ds)
        except:
            pass
        pylab.xlabel('Voltage (%sV)'%(voltage_prefix))
        pylab.ylabel('$\mathrm{d}^2I/\mathrm{d}U^2$ (%sS/V)'%(ds_prefix))     
            
        try:
            filename_args = files[i][0:-4].split('\\')[-1].split('_')
            pylab.suptitle(filename_args[1]+' Pad: '+filename_args[2]+'\n'+'['+filename_args[0]+'] '+ filename_args[3] + ' ' + filename_args[4])
        except Exception,e:
            pylab.title(files[i])
        try:
            print '%i/%i'%(i+1,len(data))
            pylab.savefig(files[i]+'.png',dpi=150)
        except:
            print 'Couldn\'t save image!'
            print files[i]+'.png'


    
    
    ov_x = 4
    ov_y = 4
    # print overview 4x4
    matplotlib.rcParams['font.size'] = 5.0
    for i in range(len(data)):  
        _v = [float(x) for x in data[i][0]]
        _i = [float (x) for x in data[i][1]]
        if not i%(ov_x*ov_y):
            pylab.clf()
        pylab.subplot(ov_x,ov_y,i%(ov_x*ov_y)+1)
        pylab.subplots_adjust(hspace=0.7,wspace=0.4)
        
        
        
        (voltage,voltage_prefix) = get_si_scaling(_v)
        (current,current_prefix) = get_si_scaling(_i)
        try:
            pylab.plot(voltage,current)
        except:
            pass
        pylab.xlabel('Voltage (%sV)'%(voltage_prefix))
        pylab.ylabel('Current (%sA)'%(current_prefix))
        
        
        try:
            filename_args = files[i][0:-4].split('\\')[-1].split('_')
            pylab.title(filename_args[1]+' Pad: '+filename_args[2]+'\n'+'['+filename_args[0]+'] '+ filename_args[3] + ' ' + filename_args[4])
        except Exception,e:
            pylab.title(files[i])
            
        pylab.grid(True)
        if i%(ov_x*ov_y) == ov_x*ov_y-1 or i>=len(data)-1:
            try:
                print path+'overview_%i'%(i/(ov_x*ov_y)+1)+'.png'
                pylab.savefig(path+'overview_%i'%(i/(ov_x*ov_y)+1)+'.png',dpi=300)
                pylab.savefig(path+'overview_%i'%(i/(ov_x*ov_y)+1)+'.pdf',dpi=300)
            except:
                print 'Couldn\'t save image!'
    matplotlib.rcParams['font.size'] = 12.0
    
def get_si_scaling(data):
    """Scales the given data to a prefix of the SI Unit system.
    It returns the data devided by the prefix and the prefix as string"""
    si_prefix = ['','k','M','G','T','P','a','f','p','n',r'$\mu$','m']
    
    data_max = pylab.array([abs(x) for x in data]).max()
    
    if data_max == 0:
        log = 0
    else:
        try:
            log = int(math.floor((math.log(data_max,10)-0)/3))
        except Exception,e:
            print "si exception" + str(e)
            log = 0
        
    if log >= len(si_prefix) or log <= -len(si_prefix):
        log = 0
    multi = math.pow(10,-3*log)
    
    data = [x*multi for x in data]
    prefix = si_prefix[log]
    return (data,prefix)

    
if __name__ == "__main__":
        
    try:
        plot(path = 'Z:\\dweber\\data_z1024\\NX66',
         fixed_maximum = 0)
    except:
        pass


    

        








    
