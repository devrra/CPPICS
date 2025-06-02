# -*- coding: utf-8 -*-
"""
Created on Mon May 19 15:30:24 2025

@author: User
"""

import requests
import json
import numpy as np
from WSMethods import *
import matplotlib.pyplot as plt


# Define device IP
ip = '10.21.0.71'

# Get device info 
result = requests.get('http://' + ip + '/waveshaper/devinfo').json()

# Set frequency variables from device info
s = result['startfreq']
e = result['stopfreq']

# Create data for wsp
wsFreq = np.linspace(s, e, int((e-s)/0.001 + 1))
wsAttn = 50*np.power(np.sin(2*np.pi/0.5*(wsFreq-193)),2)
wsPhase = np.zeros(wsFreq.shape)
wsPort = np.ones(wsFreq.shape)

##-----------------------------------------------------------------------------
# 3 passbands centered at 1550 seprated by 100GHz
wsAttn = np.zeros(len(wsFreq))+60
c = 299792458

pump1_wave = 1550.00-1.6
pump1_freq = c/(pump1_wave*1e-9)*1e-12
pump1_band = 0.03 # in THz
pump1_left = pump1_freq-pump1_band/2
pump1_right = pump1_freq+pump1_band/2

sig_wave = 1550.00
sig_freq = c/(sig_wave*1e-9)*1e-12
sig_band = 0.03 # in THz
sig_left = sig_freq-sig_band/2
sig_right = sig_freq+sig_band/2

pump2_wave = 1550.00+1.6
pump2_freq = c/(pump2_wave*1e-9)*1e-12
pump2_band = 0.03 # in THz
pump2_left = pump2_freq-pump1_band/2
pump2_right = pump2_freq+pump1_band/2

pump1_pass = (pump1_left<wsFreq) & (wsFreq<pump1_right)
sig_pass = (sig_left<wsFreq) & (wsFreq<sig_right)
pump2_pass = (pump2_left<wsFreq) & (wsFreq<pump2_right)


wsAttn[pump1_pass] =0
wsAttn[sig_pass] =0
wsAttn[pump2_pass] =0

##-----------------------------------------------------------------------------
plt.plot(wsFreq,wsAttn)
plt.show()
# Upload profile using created data
r = uploadProfile(ip, wsFreq, wsAttn, wsPhase, wsPort)