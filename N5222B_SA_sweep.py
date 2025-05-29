# NOTE: the default pyvisa import works well for Python 3.6+
# if you are working with python version lower than 3.6, use 'import visa' instead of import pyvisa as visa

import numpy as np
import pyvisa
import time
from drawnow import drawnow
import matplotlib.pyplot as plt
from PyApex import AP2XXX

# import pyvisa as visa
# import time
# start of Untitled

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

rm = pyvisa.ResourceManager()
rm.list_resources()
PNA =  rm.open_resource('TCPIP0::10.21.0.163::hislip0::INSTR')
print(PNA.query("*IDN?"))
MyAP2XXX = AP2XXX("10.21.0.60")
MyOSA = MyAP2XXX.OSA()
MyOSA.SetScaleXUnit("nm")
MyOSA.SetScaleYUnit("log") 


# PNA -------------------------------------------------------------------------
PNA.write(':CALCulate1:MEASure1:DEFine "%s"' % ('Spectrum Analyzer b3'))
# Params
center_freq = 1000000000.0
freq_span = 500000000.0
rbw = 10.0
npoints = 1001
# Setting up
PNA.write(':SENSe:FREQuency:CENTer %G' % (center_freq))
PNA.write(':SENSe:FREQuency:SPAN %G' % (freq_span))
PNA.write(':SENSe:SA:BANDwidth:RESolution %G' % (rbw))
PNA.write(':SENSe:SWEep:POINts %d' % (npoints))
PNA.write('*WAI')
# Sweep and acquire
PNA.write(':SENSe1:SWEep:MODE %s' % ('SING'))
time.sleep(15 )
x= PNA.query("CALC:MEAS:X?")
y= PNA.query("CALC1:MEAS:DATA:FDATa?")
freq = np.array(list(map(float, (x.split(",")))))
power = np.array(list(map(float, (y.split(",")))))
PNA.write(':SENSe1:SWEep:MODE %s' % ('CONT'))
plt.plot(freq,power)
# save data
data = np.column_stack((freq, power))
filepath = "D:\\Yash\\MLL_PNA_data\\SA_data_MLL_unlocked_centrefreq1GHz_span500MHz_rbw10Hz.txt"
with open(filepath,'a') as f:
    np.savetxt(f, data, fmt='%.10f', delimiter='\t')


# Params
center_freq = freq[power==max(power)][0]
freq_span = 10000.0
rbw = 10.0
npoints = 1001
# Setting up
PNA.write(':SENSe:FREQuency:CENTer %G' % (center_freq))
PNA.write(':SENSe:FREQuency:SPAN %G' % (freq_span))
PNA.write(':SENSe:SA:BANDwidth:RESolution %G' % (rbw))
PNA.write(':SENSe:SWEep:POINts %d' % (npoints))
PNA.write('*WAI')
# Sweep and acquire
PNA.write(':SENSe1:SWEep:MODE %s' % ('SING'))
time.sleep(15 )
x= PNA.query("CALC:MEAS:X?")
y= PNA.query("CALC1:MEAS:DATA:FDATa?")
freq = np.array(list(map(float, (x.split(",")))))
power = np.array(list(map(float, (y.split(",")))))
PNA.write(':SENSe1:SWEep:MODE %s' % ('CONT'))
plt.plot(freq,power)
# save data
data = np.column_stack((freq, power))
filepath = "D:\\Yash\\MLL_PNA_data\\SA_data_MLL_unlocked_centrefreq1GHz_span10KHz_rbw10Hz.txt"
with open(filepath,'a') as f:
    np.savetxt(f, data, fmt='%.10f', delimiter='\t')
# PNA.close()
# rm.close()

# OSA -------------------------------------------------------------------------
# Params
c = 299792458 # Speed of light
wl_start =1546.0
wl_stop  =1552.0
# resolution = 0.04/1000

# setting up 0.04
MyOSA.SetStartWavelength(wl_start)
MyOSA.SetStopWavelength(wl_stop)
MyOSA.SetXResolution(0.04/1000) # nm
path = "D:\\Userfiles\\Yash\\MLL\\"
filename = "OSA_data_MLL_unlocked_resolution_0p04pm"
saveosadatatoOSA(MyOSA,filename,path)

# setting up 0.8
MyOSA.SetStartWavelength(wl_start)
MyOSA.SetStopWavelength(wl_stop)
MyOSA.SetXResolution(0.8/1000) # nm
path = "D:\\Userfiles\\Yash\\MLL\\"
filename = "OSA_data_MLL_unlocked_resolution_0p8pm"
saveosadatatoOSA(MyOSA,filename,path)