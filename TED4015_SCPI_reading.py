# -*- coding: utf-8 -*-
"""
Created on Tue May 27 10:31:23 2025

@author: Admin
"""

import numpy as np
import pyvisa
import time
from drawnow import drawnow
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
rm.list_resources()

TC =  rm.open_resource('USB::4883::32840::M01213014')
print(TC.query("*IDN?"))

def do_something():
    t = time.time()
    string = str(t-t0) + ',' + TC.query("MEAS:TEMP?")
    print(string)
    file.write(string)
    time.sleep(0.1)
    
filename = "TED4015_reading.txt"
file = open(filename,"w")
t0 = time.time()
try:
    while True:
        do_something()
except KeyboardInterrupt:
    file.close()
    print("\n Temp aquisation ended!")
    pass
