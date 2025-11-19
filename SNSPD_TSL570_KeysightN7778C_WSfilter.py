# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 15:43:57 2025

@author: Yash
"""

from WebSQControl import WebSQControl
import random
import argparse
import pyvisa
rm = pyvisa.ResourceManager()
rm.list_resources()
import numpy as np
import time
import matplotlib.pyplot as plt
import pandas as pd
from WSMethods import *
# from santec import TslInstrument, GetAddress

DWELL_TIME_CONSTANT = 10
MILLISECONDS_TO_SECONDS_CONSTANT = 1000


def santec_connection():
    rm = pyvisa.ResourceManager()
    rm.list_resources()
    tsl =  rm.open_resource("GPIB0::2::INSTR")
    print(tsl.query("*IDN?"))
    # print("TSL-570 connected")
    return tsl

def keysight_connection():
    n7778c = rm.open_resource("TCPIP0::10.21.0.254::inst0::INSTR")
    print(n7778c.query("*IDN?"))
    return n7778c

def set_n7778c_wavelength(n7778c,wavelength):
    k =':sour0:wav {}NM'.format(wavelength)
    n7778c.write(k)
    return None

def set_tsl570_wavelength(tsl570,wavelength):
    k =':sour0:wav {}'.format(wavelength)
    tsl570.write(k)
    return None

def set_n7778c_power(n7778c,power):
    
    k =':sour0:pow '+str(power)+'DBM'
    n7778c.write(k)
    # laser on        :sour0:pow:stat 1
    # laser off       :sour0:pow:stat 0
    # set power unit  :sour0:pow:unit 0 (0 for dBm)
    # :sour0:pow 0
    return None

def plot_n_save(x,y,filename):
    path = "C:\\Users\\Localadmin\\Desktop\\codes\\20Oct2025\\"
    df = pd.DataFrame([x,y])
    df = df.transpose()
    df.to_csv(path+filename+'.csv',index=False,header=['wavelength[nm]', 'Count[Hz]'])
    plt.plot(x,y)
    plt.plot(x[y==np.max(y)], y[y==np.max(y)], marker='o', markersize=10, color='red', label='{}, {}'.format(x[y==np.max(y)],y[y==np.max(y)]))
    plt.xlabel('Wavelength[nm]')
    plt.ylabel('Counts[Hz]')
    plt.legend()
    plt.title(filename)
    plt.show()

def set_WS_filter(ip,stop_center,stop_bw):
    # Define device IP
    
    # Get device info 
    result = requests.get('http://' + ip + '/waveshaper/devinfo').json()
    
    # Set frequency variables from device info
    s = result['startfreq']
    e = result['stopfreq']
    
    # Create data for wsp
    wsFreq = np.linspace(s, e, int((e-s)/0.001 + 1))
    wsAttn = np.zeros(len(wsFreq))+60
    wsPhase = np.zeros(wsFreq.shape)
    wsPort = np.ones(wsFreq.shape)
    c = 299792458
    for i in range(len(stop_center)):
        stop_freq = c/(stop_center[i]*1e-9)*1e-12
        left_edge = stop_freq-stop_bw[i]/2
        right_edge = stop_freq+stop_bw[i]/2
        passband = (left_edge<wsFreq) & (wsFreq<right_edge)
        wsAttn[passband] = 0
    plt.plot(wsFreq,wsAttn)
    plt.show()
    # Upload profile using created data
    r = uploadProfile(ip, wsFreq, wsAttn, wsPhase, wsPort)
    return
    

# Parses arguments, type -h for help message
parser = argparse.ArgumentParser(
    add_help=True,
    description='Example program.')
parser.add_argument('-N', dest='N', type=int, default=10,
                    help='The amount of measurements done.')
parser.add_argument(
    '--ipAddress',
    '-ip',
    dest='tcp_ip_address',
    type=str,
    default='192.168.1.1',
    help='The TCP IP address of the detector')
args = parser.parse_args()

# Number of measurements (default 10)
N = args.N
N=1
# TCP IP Address of your system (default 192.168.1.1)
tcp_ip_address = args.tcp_ip_address
# The control port (default 12000)
control_port = 12000
# The port emitting the photon Counts (default 12345)
counts_port = 12345
websq = WebSQControl(TCP_IP_ADR=tcp_ip_address, CONTROL_PORT=control_port, COUNTS_PORT=counts_port)
# Alternatively, you can use the with clause
# with WebSQControl(TCP_IP_ADR=tcp_ip_address, CONTROL_PORT=control_port, COUNTS_PORT=counts_port) as websq:
#websqconnect
websq.connect()
print("Set integration time to 1 s\n")
websq.set_measurement_periode(1000)   # Time in ms



############################ input ############################################
c = 299792458
wavl_step = 0.001
n7778c_state = 2        #0=off, 1=on, 2=on and sweep
n7778c_sweep = np.round(np.arange(1547.85-0.1,1547.85+0.1,wavl_step),decimals=3)
# n7778c_fix = 1550
n7778c_power = 9        # dBm

tsl570_state = 1        #0=off, 1=on, 2=on and sweep
tsl570_sweep = np.round(np.arange(1550.970-0.1,1550.995,wavl_step),decimals=3)
# tsl570_fix = 1550
tsl570_power = 9        # dBm

ws1_ip = '10.21.1.0'
ws2_ip = '10.21.1.1'
pass_wav = 1550
pass_bw = 0.0125 #THz

detector = 1
suffix = "count_at_1552p5nm_0"
###############################################################################
tsl570 = santec_connection()
n7778c = keysight_connection()
# websq.enable_detectors(state=True)
# time.sleep(1)

if n7778c_state==2 and tsl570_state==0:
    set_WS_filter(ws1_ip,[pass_wav],[pass_bw])
    set_WS_filter(ws2_ip,[pass_wav],[pass_bw])
    
    tsl570.write(":POW:STAT 0")
    n7778c.write(":sour0:pow:stat 1")
    n7778c.write(':sour0:pow '+str(n7778c_power)+'DBM')
    time.sleep(0.5)
    counts = n7778c_sweep*0
    websq.enable_detectors(state=True)
    time.sleep(1)
    for i in range(len(n7778c_sweep)):
        set_n7778c_wavelength(n7778c,n7778c_sweep[i])
        time.sleep(1)
        data = websq.acquire_cnts(1)
        counts[i] = data[0][detector]
        time.sleep(0.1)
        print('n7778c: {}, {}'.format(n7778c_sweep[i], counts[i]))
    filename = "n7778c_power_{}dBm_sweep_{}_{}_{}_tsl570_off_count_{}nm_{}THz_{}".format(n7778c_power,n7778c_sweep[0],n7778c_sweep[-1],wavl_step,pass_wav,pass_bw,suffix)
    filename = "".join(['p' if char == '.' else char for char in filename])
    plot_n_save(n7778c_sweep,counts,filename)
    
elif n7778c_state==0 and tsl570_state==2:
    set_WS_filter(ws1_ip,[pass_wav],[pass_bw])
    set_WS_filter(ws2_ip,[pass_wav],[pass_bw])
    
    tsl570.write(":POW:STAT 1")
    n7778c.write(":sour0:pow:stat 0")
    tsl570.write("SOUR0:POW {}".format(tsl570_power))
    counts = tsl570_sweep*0
    time.sleep(0.5)
    websq.enable_detectors(state=True)
    time.sleep(1)
    for i in range(len(tsl570_sweep)):
        set_tsl570_wavelength(tsl570,tsl570_sweep[i])
        time.sleep(1)
        data = websq.acquire_cnts(1)
        counts[i] = data[0][detector]
        time.sleep(0.1)
        print('tsl570: {}, {}'.format(tsl570_sweep[i], counts[i]))
    filename = "n7778c_off_tsl570_power_{}dBm_sweep_{}_{}_{}_count_{}nm_{}THz_{}".format(tsl570_power,tsl570_sweep[0],tsl570_sweep[-1],wavl_step,pass_wav,pass_bw,suffix)
    filename = "".join(['p' if char == '.' else char for char in filename])
    plot_n_save(tsl570_sweep,counts,filename)
    
    
elif n7778c_state==2 and tsl570_state==1:
    set_WS_filter(ws1_ip,[pass_wav],[pass_bw])
    set_WS_filter(ws2_ip,[pass_wav],[pass_bw])
    
    n7778c.write(":sour0:pow:stat 0")
    set_n7778c_wavelength(n7778c,n7778c_sweep[0])
    tsl570.write(":POW:STAT 1")
    set_tsl570_wavelength(tsl570,tsl570_sweep[0])
    tsl570.write("SOUR0:POW {}".format(tsl570_power))
    for i in range(len(tsl570_sweep)):
        set_tsl570_wavelength(tsl570,tsl570_sweep[i])
        time.sleep(1)
        print('tsl570 : {}'.format(tsl570_sweep[i]))
    print('tsl570 fixed : wavelength={}nm   power={}dBm'.format(tsl570_sweep[-1],tsl570_power))
    time.sleep(2)
    print('sweeping n7778c...')
    n7778c.write(':sour0:pow '+str(n7778c_power)+'DBM')
    n7778c.write(":sour0:pow:stat 1")
    counts = n7778c_sweep*0
    websq.enable_detectors(state=True)
    time.sleep(1)
    for i in range(len(n7778c_sweep)):
        set_n7778c_wavelength(n7778c,n7778c_sweep[i])
        time.sleep(1)
        data = websq.acquire_cnts(1)
        counts[i] = data[0][detector]
        time.sleep(0.1)
        print('n7778c: {}, {}'.format(n7778c_sweep[i], counts[i]))
    filename = "n7778c_power_{}dBm_sweep_{}_{}_{}_tsl570_power_{}dBm_wavelength_{}_count_{}nm_{}THz_{}".format(n7778c_power,n7778c_sweep[0],n7778c_sweep[-1],wavl_step,tsl570_power,tsl570_sweep[-1],pass_wav,pass_bw,suffix)
    filename = "".join(['p' if char == '.' else char for char in filename])
    plot_n_save(n7778c_sweep,counts,filename)


elif n7778c_state==1 and tsl570_state==2:
    set_WS_filter(ws1_ip,[pass_wav],[pass_bw])
    set_WS_filter(ws2_ip,[pass_wav],[pass_bw])
    
    tsl570.write(":POW:STAT 0")
    set_tsl570_wavelength(tsl570, tsl570_sweep[0])
    n7778c.write(':sour0:pow '+str(n7778c_power)+'DBM')
    n7778c.write(":sour0:pow:stat 1")
    for i in range(len(n7778c_sweep)):
        set_n7778c_wavelength(n7778c,n7778c_sweep[i])
        time.sleep(1)
        print('n7778c : {}'.format(n7778c_sweep[i]))
    print('n7778c fixed : wavelength={}nm   power={}dBm'.format(n7778c_sweep[-1],n7778c_power))
    time.sleep(2)
    print('sweeping tsl570...')
    tsl570.write("SOUR0:POW {}".format(tsl570_power))
    tsl570.write(":POW:STAT 1")
    counts = tsl570_sweep*0
    websq.enable_detectors(state=True)
    time.sleep(1)
    for i in range(len(tsl570_sweep)):
        set_tsl570_wavelength(tsl570,tsl570_sweep[i])
        time.sleep(1)
        data = websq.acquire_cnts(1)
        counts[i] = data[0][detector]
        time.sleep(0.1)
        print('tsl570: {}, {}'.format(tsl570_sweep[i], counts[i]))
    filename = "n7778c_power_{}dBm_wavelength_{}_tsl570_power_{}dBm_sweep_{}_{}_{}_count_{}nm_{}THz_{}".format(n7778c_power,n7778c_sweep[-1],tsl570_power,tsl570_sweep[0], tsl570_sweep[-1], wavl_step,pass_wav,pass_bw, suffix)
    filename = "".join(['p' if char == '.' else char for char in filename])
    plot_n_save(tsl570_sweep,counts,filename)

set_WS_filter(ws1_ip,[],[])
set_WS_filter(ws2_ip,[],[])
websq.enable_detectors(state=False)
tsl570.write(":POW:STAT 0")
n7778c.write(":sour0:pow:stat 0")