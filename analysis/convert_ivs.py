# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 20:24:49 2014

@author: David Weber
"""

import os
import scipy, numpy as np



rref = 104000.0
iv_path = r"C:\Users\David Weber\Desktop\Pb216"

iv_files = os.listdir(iv_path)
for iv_file in iv_files:
    if iv_file.split(".")[-1] == "txt" and iv_file[0:3] != "out":
        print iv_file
        iv_filename = os.path.join(iv_path,iv_file)
        
        iv_data = scipy.loadtxt(iv_filename,unpack=True,skiprows=3)
        
        v = iv_data[1]
        i = [x/rref for x in iv_data[2]]
        
        iv_output = os.path.join(iv_path,"out_"+iv_file)
        scipy.savetxt(iv_output, np.transpose([v,i]), fmt="%10.10f", delimiter="\t")
        