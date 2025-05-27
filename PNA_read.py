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

PNA =  rm.open_resource('TCPIP0::10.21.2.47::hislip0::INSTR')
print(PNA.query("*IDN?"))


maxf = []
maxdb = []
fig2=plt.figure()
fig1=plt.figure() 

def makeFig_F():
    #plt.scatter(v,i) # I think you meant this
    #plt.clf()
    
   
    fig1=plt.plot(maxf)
    
plt.ion() # enable interactivity

def makeFig_db():
    #plt.scatter(v,i) # I think you meant this
    #plt.clf()
    
   
    fig2=plt.plot(maxdb)
    
plt.ion() # enable interactivity



every_time_in_sec  =30
No_of_times =60
for i in range(No_of_times):    
    PNA.write("SENS1:SWE:MODE SING")
    #x =PNA.query("*OPC?");
    
    x= PNA.query("CALC:MEAS:X?")
    y= PNA.query("CALC1:MEAS:DATA:FDATa?")
    f = list(map(float, (x.split(","))))
    re = list(map(float, (y.split(","))))
    
    
    #data_array = np.array([np.array(f),np.array(re)])
    
    data = np.column_stack((f, re))
    max_index = np.argmax(data[:,1])
    
    maxf.append(data[max_index,0])
    maxdb.append(data[max_index,1])
    print("Index of maximum frequency:", i,data[max_index,0],data[max_index,1])
    filepath = f"E:\\Yash\\PNA_test.txt"
    #np.savetxt(filepath, IV_curve, fmt='%.10f', delimiter='\t')
    max_data = np.column_stack((maxf, maxdb))
    #drawnow(makeFig_F)
    #time.sleep(10)
    #drawnow(makeFig_db)
    
    
    with open(filepath,'a') as f:
        np.savetxt(f, max_data, fmt='%.10f', delimiter='\t')
    
    f = open(filepath, "a")
    #filepath = r"E:\ram\pawan\18th_may_24_DC_Meas\C2\PD5\dark_current_PD5.txt";
    	
    PNA.write("SENS:SWE:MODE CONT")
    #np.savetxt(filepath, max_data, fmt='%.10f', delimiter='\t')
    time.sleep(every_time_in_sec )
    