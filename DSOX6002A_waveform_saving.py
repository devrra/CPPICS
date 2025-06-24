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


rm = pyvisa.ResourceManager()
rm.list_resources()
DSO =  rm.open_resource('TCPIP0::10.21.2.47::hislip0::INSTR')
print(DSO.query("*IDN?"))

DSO.write(':CHANnel1:COUPling %s' % ('DC'))     # sets channel coupling - 'AC', 'DC'
DSO.write(':CHANnel1:IMPedance %s' % ('FIFTy')) # sets channel impedence - 'FIFTy', 'ONEMeg'
DSO.write(':SAVE:WAVeform:FORMat %s' % ('CSV')) # sets the waveform data format type - 'ASCiixy', 'CSV', 'BINary'
DSO.write(':WAVeform:SOURce %s' % ('CHANnel1')) # 
DSO.write(':WAVeform:FORMat %s' % ('ASCii'))    # sets the data transmission mode for waveform data points - 'WORD', 'BYTE', 'ASCii'

every_time_in_sec  =30
No_of_times = 1
for i in range(No_of_times):
    # DSO.write(':RUN')
    DSO.write(':SINGle')
    # DSO.write(':STOP')
    DSO.write(':SAVE:WAVeform:STARt "%s"' % ('wav1'))
    temp_values = DSO.query_binary_values(':WAVeform:DATA?','s',False)
    binaryBlockData = temp_values[0].decode().split(',')
    time.sleep(every_time_in_sec)
DSO.close()
rm.close()

# end of Untitled
