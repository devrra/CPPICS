# -*- coding: utf-8 -*-
"""
Created on Mon May  5 19:59:30 2025

@author: Admin
"""

import numpy as np
import pyvisa
import time
from PyApex import AP2XXX
from drawnow import drawnow
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
rm.list_resources()

# OSA interfacing
# OSA = rm.open_resource('GPIB0::3::INSTR')
# print(OSA.query("*IDN?"))


#start of the OSA
c = 299792458 # Speed of light
 #'OCSA'
wl_start =1546.00
wl_stop  =1552.00
#NbPoints = 208510
MyAP2XXX = AP2XXX("10.21.1.186") #OSA2
# MyAP2XXX = AP2XXX("10.21.1.86") #OSA1

MyOSA = MyAP2XXX.OSA()
MyOSA.SetScaleXUnit("nm")
MyOSA.SetScaleYUnit("log") 
MyOSA.SetStartWavelength(wl_start)
MyOSA.SetXResolution(0.00004)
MyOSA.SetStopWavelength(wl_stop)
#MyOCSA.SetNbPoints(208510)
print(MyOSA.GetStartWavelength())
print(MyOSA.GetStopWavelength())
print(MyOSA.GetNPoints())

def saveosadatatoOSA(MyOSA,filename,path,*args, **kwargs):
    t0 = time.time()
    MyOSA.Run("single")
    t1 = time.time()
    print("Single sweep in OSA Total :", t1-t0)
    full_path =path+filename
    print(full_path)
    t0 = time.time()
    #print(full_path)
    MyOSA.SaveToFile(full_path, TraceNumber=1, Type="txt")
    t1 = time.time()
    print("Saving in osa sweep in OSA Total :", t1-t0)
    return

OSA_FILE_PATH ="D:\\Userfiles\\Yash\\MLL\\"

for i in range(100):  
    MyOSA.Run()
    filename = "OSA_data_MLL_stab_locked_20GHz_{}".format(i)
    saveosadatatoOSA(MyOSA,filename,OSA_FILE_PATH)
    time.sleep(1)