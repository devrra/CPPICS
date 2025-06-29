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
import csv

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
    
# plt.ion() # enable interactivity


rm = pyvisa.ResourceManager()
rm.list_resources()
DSO =  rm.open_resource('TCPIP0::10.21.1.97::INSTR')
print(DSO.query("*IDN?"))

DSO.write(':CHANnel1:COUPling %s' % ('DC'))     # sets channel coupling - 'AC', 'DC'
DSO.write(':CHANnel1:IMPedance %s' % ('ONEMeg')) # sets channel impedence - 'FIFTy', 'ONEMeg'
DSO.write(':SAVE:WAVeform:FORMat %s' % ('ASCiixy')) # sets the waveform data format type - 'ASCiixy', 'CSV', 'BINary'
DSO.write(':WAVeform:SOURce %s' % ('CHANnel1')) # 
DSO.write(':WAVeform:FORMat %s' % ('ASCii'))    # sets the data transmission mode for waveform data points - 'WORD', 'BYTE', 'ASCii'

every_time_in_sec  =2
No_of_times = 1
for i in range(No_of_times):
    # DSO.write(':RUN')
    DSO.write(':SINGle')
    # DSO.write(':STOP')
    # DSO.write(':SAVE:WAVeform:STARt "%s"' % ('wav1'))
    preamble  = DSO.query(':WAVeform:PREamble?')
    preamble = preamble.split(',')
    num_pts = int(preamble[2])
    xincrement = float(preamble[4])
    xorigin = float(preamble[5])
    xreference = int(preamble[6])
    yincrement = float(preamble[7])
    yorigin = float(preamble[8])
    yreference = int(preamble[9])
    
    data  = DSO.query(':WAVeform:DATa?')
    data = data.split(',')
    for i in range(1,len(data)):
        data[i] = float(data[i])
    data = np.array(data[1:])
    
    t = xorigin + np.arange(len(data))*xincrement
    # v = (data - yreference)*yincrement + yorigin
    
    plt.plot(t,data*1000)
    plt.show()
    
    filename = 'output_{}.csv'.format(i)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write each row to the CSV file
        for j in range(len(data)):
            writer.writerow([t[j],data[j]*1000])
    
    time.sleep(every_time_in_sec)
   
DSO.close()
rm.close()
