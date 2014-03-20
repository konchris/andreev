# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 19:13:57 2013

@author: David Weber
"""

import threading
import time

class measurement_thread(threading.Thread):
    def __init__(self, filename, delay=1.0): 
        threading.Thread.__init__(self) 
        self.filename = filename
        self.delay = delay
        
        self.save = {}
        self.quantity = {}
    
    def add_quantity(self, function, label):
        self.quantity[label] = function
        self.save[label] = []
    
    def get_last_values(self):
        return_values = {}
        for quantity,v in self.quantity.items():
            return_values[quantity] = self.save[quantity][-1]
        return return_values
            
 
    def run(self): 
        while True:
            for quantity,function in self.quantity.items():
                self.save[quantity].append(function())
            
            time.sleep(self.delay)
            print self.save
            print self.get_last_values()

test = measurement_thread("test")
test.add_quantity(time.time, "time")
test.run()