# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 20:24:26 2013
All rights reserved by David Weber
@author: David Weber
"""

import ctypes

# driver for luci interface has to be in the same directory or give the path
luci = ctypes.cdll.LoadLibrary("LUCI_10.dll")

def init():
    """I think this has to be called first"""
    luci.EnumerateUsbDevices()

def write_bytes(index,low,high):
    """Writes low and high byte to port (25:10)"""
    return luci.WriteData(index,low,high)

def list_adapters():
    """Prints a list of found interfaces"""
    chr_buffer = ctypes.c_char_p('1234567901234567890123456789012345678901234567890')
    for i in range(256):
        if luci.GetProductString(i, chr_buffer, 49)==0:
            temp = ctypes.c_int(0)
            luci.ReadAdapterID(i, ctypes.byref(temp));
            print "%i: %s, ID=%i"%(i,chr_buffer.value,temp.value)

def get_status_pin5(index):
    """Returns status of input 5"""
    status = ctypes.c_int(0)
    luci.GetStatusPin5(index, ctypes.byref(status))
    if status:
        return True
    else:
        return False

def get_status_pin6(index):
    """Returns status of input 6"""
    status = ctypes.c_int(0)
    luci.GetStatusPin6(index, ctypes.byref(status))
    if status:
        return True
    else:
        return False
        
def get_status_pin7(index):
    """Returns status of input 7"""
    status = ctypes.c_int(0)
    luci.GetStatusPin7(index, ctypes.byref(status))
    if status:
        return True
    else:
        return False
    

#data low (17:10)
#data high (25:18)
 

#class FEMTO:          
#    """Connect AUX1 to Pin10, AUX2 to Pin11, AUX3 to Pin12, AUX4 to Pin14"""
#    def __init__(self, lockin, name="UNDEFINED"):
#        self.lockin = lockin
#        self.name = name
#    
#    def reset(self):
#        for i in range(4):
#            self.lockin.set_aux_output(i+1,0)
#    
#    def set_amplification(self, exponent, highspeed=False):
#        """sets the amplification level of variable gain current amplifier.
#        low noise: 10^3-10^9
#        high speed: 10^5-10^11"""
#        
#        backup_exponent = exponent
#        
#        if highspeed:
#            if exponent < 5:
#                exponent = 5
#            if exponent > 11:
#                exponent = 11                
#            exponent = exponent - 5
#            mode = "Highspeed"
#        else:
#            if exponent < 3:
#                exponent = 3
#            if exponent > 9:
#                exponent = 9
#            exponent = exponent - 3
#            mode = "Low Noise"
#        
#        log("Set Amplification of %s to 10^%i and %s"%(self.name,backup_exponent,mode))
#
#        self.lockin.set_aux_output(1,((exponent>>0)&1)*5)
#        self.lockin.set_aux_output(2,((exponent>>1)&1)*5)
#        self.lockin.set_aux_output(3,((exponent>>2)&1)*5)
#        if highspeed:
#            self.lockin.set_aux_output(4,0)
#        else:
#            self.lockin.set_aux_output(4,5)
            
            