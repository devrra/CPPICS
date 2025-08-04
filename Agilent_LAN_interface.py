# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 11:09:13 2025

@author: Admin
"""
import time
import socket

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('169.254.4.61', 5025))
# print(s)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.settimeout(2)
id_query = '*IDN?\n'
s.send(id_query.encode('utf-8'))
id_rcv = s.recv(1000)
print('ID: ' + id_rcv.decode('utf-8'))

def do_something():
    t = time.time()
    vmeas_query = 'MEAS:VOLT?\n'
    s.send(vmeas_query.encode('utf-8'))
    vmeas_rcv = s.recv(1000)
    vmeas_rcv_decoded = vmeas_rcv.decode('utf-8')
    # print(vmeas_rcv_decoded)
    string = str(t-t0) + ',' + vmeas_rcv_decoded
    print(string)
    file.write(string)
    time.sleep(0.1)

filename = "AgilentDMM_Vreading.txt"
file = open(filename,"w")
t0 = time.time()
try:
    while True:
        do_something()
except KeyboardInterrupt:
    file.close()
    s.close()
    print("\n Voltage aquisation ended!")
    pass






    
