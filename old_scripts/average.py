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
import matplotlib as mpl



def plot(path = 'Z:\\dweber\\data_z1024\\NX28\\Pad 13',
         comment_string = '#',
         fixed_maximum = -1e-8, # 0=nothing, -1 fix to maximum, >0 set max
         ):
    
    
    si_prefix = ['','m','u','n','p','f']
    
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
            for row in csv_file:
                voltage.append(row[0])
                current.append(row[1])
            data.append([voltage,current])
            
        except Exception,e:
            print e
    
# if maximum should be found    
    if fixed_maximum < 0:
        max_i = 0
        for i in range(len(data)):
            for x in data[i][1]:
                if abs(float(x)) > max_i:
                    max_i = abs(float(x))
        
        
    for i in range(len(data)):  
        _v = [float(x) for x in data[i][0]]
        _i = [float (x) for x in data[i][1]]
        pylab.clf()
        
        
        
        log_i = 0
        for x in _i:
                if abs(float(x)) > log_i:
                    log_i = abs(float(x))
        log_u = 0
        for x in _v:
                if abs(float(x)) > log_u:
                    log_u = abs(float(x))
        
        if fixed_maximum < 0:
            log_i = max_i
        
        if fixed_maximum > 0:
            log_i = fixed_maximum
        
        log_i = int(math.ceil((abs(math.log(log_i,10))/3)))
        log_u = int(math.ceil((abs(math.log(log_u,10))/3)))
        
        multi_i = math.pow(10,3*log_i)
        multi_u = math.pow(10,3*log_u)
    

        
        pylab.plot(pylab.array(_v)*multi_u,pylab.array(_i)*multi_i)
        pylab.xlabel('Voltage (%sV)'%(si_prefix[log_u]))
        pylab.ylabel('Current (%sA)'%(si_prefix[log_i]))
        
        if fixed_maximum < 0:
            pylab.ylim((-max_i*multi_i,max_i*multi_i))
        try:
            filename_args = files[i][0:-4].split('\\')[-1].split('_')
            pylab.title(filename_args[1]+' Pad: '+filename_args[2]+'\n'+'['+filename_args[0]+'] '+ filename_args[3] + ' ' + filename_args[4])
        except Exception,e:
            pylab.title(files[i])
            
        pylab.grid(True)
        if fixed_maximum > 0:
            pylab.ylim((-fixed_maximum*multi_i,fixed_maximum*multi_i))
        try:
            print '%i/%i'%(i+1,len(data))
            pylab.savefig(files[i]+'.png',dpi=150)
        except:
            print 'Couldn\'t save image!'
    
    
    ov_x = 4
    ov_y = 4
    # print overview 4x4
    mpl.rcParams['font.size'] = 5.0
    for i in range(len(data)):  
        _v = [float(x) for x in data[i][0]]
        _i = [float (x) for x in data[i][1]]
        if not i%(ov_x*ov_y):
            pylab.clf()
        pylab.subplot(ov_x,ov_y,i%(ov_x*ov_y)+1)
        pylab.subplots_adjust(hspace=0.7,wspace=0.4)
        
        
        if fixed_maximum == 0:
            log_i = 0
            for x in _i:
                    if abs(float(x)) > log_i:
                        log_i = abs(float(x))
                        
        log_u = 0
        for x in _v:
                if abs(float(x)) > log_u:
                    log_u = abs(float(x))
        
        if fixed_maximum < 0:
            log_i = max_i
        
        if fixed_maximum > 0:
            log_i = fixed_maximum
        
        log_i = int(math.ceil((abs(math.log(log_i,10))/3)))
        log_u = int(math.ceil((abs(math.log(log_u,10))/3)))
        
        multi_i = math.pow(10,3*log_i)
        multi_u = math.pow(10,3*log_u)
        
        pylab.plot(pylab.array(_v)*multi_u,pylab.array(_i)*multi_i)
        pylab.xlabel('Voltage (%sV)'%(si_prefix[log_u]))
        pylab.ylabel('Current (%sA)'%(si_prefix[log_i]))
        
        if fixed_maximum < 0:
            pylab.ylim((-max_i*multi_i,max_i*multi_i))
        if fixed_maximum > 0:
            pylab.ylim((-fixed_maximum*multi_i,fixed_maximum*multi_i))
        
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
    mpl.rcParams['font.size'] = 12.0
    
    
    


def average(path = 'Z:\\dweber\\data_z1024\\NX28\\Pad 13',
            comment_string = '#',
            start = -0.5,
            stop = 0.5,
            step = 0.005
            ):

# add backslash if needed
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
            for row in csv_file:
                voltage.append(row[0])
                current.append(row[1])
            data.append([voltage,current])
            
        except Exception,e:
            print e


    v_array = []
    i = 0
    while True:
        v_array.append(round(start+i*step,6))
        i = i + 1
        if start+i*step > stop:
            break
    
    # create count and current arrays and transpose
    count_array = numpy.zeros(len(v_array))
    i_array = numpy.zeros(len(v_array))
    count_array = [int(x) for x in count_array]
    i_array = [x for x in i_array]
    
    
    
    
    # make sum over values, perhaps interpolate
    for i in range(len(data)):
        for j in range(len(data[i][1])):
            _index = get_index(data[i][0][j],start,stop,step)
            
            # if value fits into defined range
            if _index >= 0:
                
                # if value fits +-1% to a cell
                #if i==1 and j%100==0:
                #    print v_array[_index]+step*0.01 , data[i][0][j] , abs(v_array[_index])+step*0.01<=abs(float(data[i][0][j]))
                #    print v_array[_index]-step*0.01 , data[i][0][j] , abs(v_array[_index])-step*0.01<=abs(float(data[i][0][j]))
                #print str(data[i][0][j])
                if float(v_array[_index])+step*0.01>=float(data[i][0][j]) and float(v_array[_index])-step*0.01<=float(data[i][0][j]):
                    i_array[_index] = i_array[_index]+float(data[i][1][j])   
                    count_array[_index] = count_array[_index] + 1
                
                # if value has to be interpolated
                else:
                    i_array[_index] = i_array[_index]+float(data[i][1][j])   
                    count_array[_index] = count_array[_index] + 1
    
                    
       
    # divide sum by counts of this cell
    for i in range(len(count_array)):
        if count_array[i] != 0:
            i_array[i] = i_array[i]/count_array[i]
        
    j = -1
    for i in range(len(count_array)):
        if count_array[i] == 0:
            j=i
        else:
            break
    
    k = -1
    for i in range(len(count_array),0,-1):
        if count_array[i-1] == 0:
            k=i-1
        else:
            break
    j = j+1
    v_array = v_array[j:k]
    i_array = i_array[j:k]
    
    v_array = [x for x in v_array]
    i_array = [x for x in i_array]
    
    count_array.pop(get_index(0,start,stop,step))
    max_averages = max(count_array)
    
    pylab.clf()
    #pylab.subplot(2, 1, 1)
    pylab.subplots_adjust(top=0.9, bottom=0.1,hspace=0.5)
    pylab.plot(pylab.array(v_array)*1000,pylab.array(i_array)*1000*1000)
    pylab.xlabel('Voltage (mV)')
    pylab.ylabel('Current (uA)')
    pylab.title(path+'\naverage over max. %i'%(max_averages))
    pylab.grid(True)
    pylab.savefig(path+'average')
    #pylab.show()   
    """
    fowler_i = numpy.log(abs(pylab.array(i_array)/pylab.array(v_array)/pylab.array(v_array)))
    fowler_u = 1/pylab.array(v_array)
    
    
    
    #pylab.clf()
    pylab.subplot(2,1,2)
    pylab.xlim((-10,10))
    pylab.ylim((-12,-10))
    pylab.plot(fowler_u,fowler_i)
    pylab.xlabel('Voltage (1/V)')
    pylab.ylabel('Current (ln(I/V^2))')
    pylab.title(path+'\nFN Plot, average over max. %i'%(max_averages))
    pylab.grid(True)
    pylab.savefig(path+'average_fowler.png',dpi=150)
    pylab.savefig(path+'average_fowler.pdf')
    pylab.show()
    #pylab.subplot_tool()
    """
    
    try:
        f = open(path+'average.txt', 'w')
    
        for index in range(len(v_array)):
            f.write(str(v_array[index])+'\t'+str(i_array[index])+'\n')
        f.close();
    except Exception,e:
        print 'Problems at writing data'
        print e
        
    
def get_index(value,_start,_stop,_step):
    value = float(value)
    if value > _stop-_step/2 or value < _start+_step/2:
        return -1
    _steps = value/_step
    _index = round(_steps) + abs(round(_start/_step))

    return int(_index)
    
 
    
    
if __name__ == "__main__":
    _path = 'Z:\\dweber\\data_z1024\\32_cold'
    
    plot(path = _path,
         fixed_maximum = 0)
    """average(path = _path,
            start = -0.9,
            stop = 0.9,
            step = 0.02)"""

    

        








    
