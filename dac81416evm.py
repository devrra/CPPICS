# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 16:34:11 2024

@author: Ram/Yash
"""

#control of USB2any need 32 bit environment
#download 32 bit python and run the code 

from ctypes import *
import ctypes as ct
import time as t
#spi settings 
SPI_ClockPhase = ct.c_bool(True)
SPI_ClockPolarity = ct.c_bool(False)
SPI_BitDirection = ct.c_bool(True) # MSb first (1)
SPI_CharacterLength = ct.c_bool(False) # 8 bits (0)
SPI_CSType = ct.c_int(1) #(1) after every packet and (2) after every word
SPI_CSPolarity = ct.c_bool(True) #(active low)
DividerHigh =ct.c_byte(0)# high and low for 8000khz data rate 
DividerLow =ct.c_byte(3)

# reg address
NOP = 0x00
DEVICEID = 0x01
STATUS = 0x02 
SPICONFIG = 0x03
DACPWDWN = 0x09
DACRANGE0 = 0x0A
DACRANGE1 = 0x0B
DACRANGE2 = 0x0C
DACRANGE3 = 0x0D
DAC0 = 0x10
DAC1 = 0x11
DAC2 = 0x12
DAC3 = 0x13
DAC4 = 0x14
DAC5 = 0x15
DAC6 = 0x16
DAC7 = 0x17
DAC8 = 0x18
DAC9 = 0x19
DAC10 = 0x1A
DAC11 = 0x1B
DAC12 = 0x1C
DAC13 = 0x1D
DAC14 = 0x1E
DAC15 = 0x1F #0001 1111

def setup():
    print("---------SETTING UP--------- ")
    # Load DLL into memory.
    path = "E:\\ram\\test\\USB2ANY.dll"
    u2aDll = ct.WinDLL (path)

    #find no of devices 
    no_of_devices = u2aDll.u2aFindControllers()
    print('no_of_devices:',no_of_devices)

    #find the serial number of the device 
    SerialNumber = ct.c_buffer(255)
    s =u2aDll.u2aGetSerialNumber(0, ct.byref(SerialNumber))
    print('SerialNumber:',s)

    #open the device and make an handle (K)
    K =u2aDll.u2aOpen (ct.byref(SerialNumber))
    print(K)
    print(type(K))

    #sending the SPI settings 
    s=u2aDll.u2aSPI_Control (K,SPI_ClockPhase,SPI_ClockPolarity,SPI_BitDirection,
                    SPI_CharacterLength,SPI_CSType,SPI_CSPolarity,DividerHigh,
                    DividerLow)
    # print(s)

    #for 3.3 v enabling the circuit
    s=u2aDll.u2aPower_Enable (K,1,0,0)
    #t.sleep(5)

    # print("power")
    # print(s)
    return K

def read_dac_reg(dac_handle,reg_addr,n):
    data = (c_unit8*3)()
    data[0] = (0b10000000 | reg_addr)
    data[1] = 0x00
    data[2] = 0x00
    for i in range(n):
        s=u2aDll.u2aSPI_WriteAndRead (dac_handle,ct.c_byte(3),byref(data))
    print('read:',hex(data[0]),hex(data[1]),hex(data[2]))
    return data

def write_dac_reg(dac_handle,reg_addr,cmd):
    data = (c_unit8*3)()
    data[0] = (0b00000000 | reg_addr)
    data[1] = cmd & 0x0F
    data[2] = (cmd & 0xF0)>>4
    print('write:',hex(data[0]),hex(data[1]),hex(data[2]))
    s=u2aDll.u2aSPI_WriteAndRead (dac_handle,ct.c_byte(3),byref(data))
    return s

def dac_on(DAC_HANDLE):
    pass
    
def channel_on(DAC_HANDLE,channel,voltage):
    #get current DACPWDWN status
    #edit 
    #set channel voltage
    
    #turn channel on
    pass
    
    

#dummy_write_to set the registers
m = (c_uint8*3)()
m[0]=0x00
m[1]=0x00
m[2] =0x00
s=u2aDll.u2aSPI_WriteAndRead (K,ct.c_byte(3),byref(m)) 
print(s)
print(hex(m[0]))
print(hex(m[1]))
print(hex(m[2]))
#t.sleep(1)
m = (c_uint8*3)()
m[0]=0x03
m[1]=0x0a
m[2] =0x04
s=u2aDll.u2aSPI_WriteAndRead (K,ct.c_byte(3),byref(m)) 
print(s)
print(hex(m[0]))
print(hex(m[1]))
print(hex(m[2]))
#t.sleep(1)
o = (c_uint8*3)()
o[0]=0x10
o[1]=0x80
o[2] =0x00
s=u2aDll.u2aSPI_WriteAndRead (K,ct.c_byte(3),byref(o)) 
print(s)
print(hex(o[0]))
print(hex(o[1]))
print(hex(o[2]))
#t.sleep(1)
p = (c_uint8*3)()
p[0]=0x09
p[1]=0xff
p[2] =0xfe
s=u2aDll.u2aSPI_WriteAndRead (K,ct.c_byte(3),byref(p)) 
print(s)
print(hex(p[0]))
print(hex(p[1]))
print(hex(p[2]))

#t.sleep(1)

#close the device with handle (K)
s =u2aDll.u2aClose (K)
print(s)
