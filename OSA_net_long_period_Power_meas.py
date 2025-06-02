# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 09:28:17 2025

@author: User
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
wl_start =1559.384
wl_stop  =1562.113
#NbPoints = 208510
# MyAP2XXX = AP2XXX("169.254.61.72")
MyAP2XXX = AP2XXX("10.21.0.167")
MyOSA = MyAP2XXX.OSA()
MyOSA.SetScaleXUnit("nm")
MyOSA.SetScaleYUnit("log") 
MyOSA.SetStartWavelength(wl_start)
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

OSA_FILE_PATH ="D:\\Userfiles\\ram\\03_03_24\\"

Lambda = []
Power = []
t = []

# fig, axs = plt.subplots(2)
# def makeFig():
#     fig.suptitle('Vertically stacked subplots')
#     axs[0].plot(t, Power)
#     axs[1].plot(t, Lambda) 
    
# tx=time.time()

delay_meas = 2

for i in range(1000):  
    MyOSA.Run()
    data = MyOSA.FindPeak(TraceNumber=1, ThresholdValue=25.0, Axis=2, Find="max")
    Lambda.append(data[0])
    Power.append(data[1])
    t.append(delay_meas*i)
    print(i, Lambda[-1], Power[-1])
    # drawnow(makeFig_Power)
    # drawnow(makeFig)
    time.sleep(delay_meas)


    

file = open('Pritel_20GHz_EDFA_on_OSA1.txt', 'w')
for i in range(len(t)):
    data = "{}\t{}\t{}\t{}\n".format(i,t[i],Lambda[i],Power[i])
    file.write(data)
file.close()   