# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 16:34:11 2024

@author: Ram/Yash
"""

from ctypes import *
import ctypes as ct
import time as t
from tkinter import *

#spi settings 
SPI_ClockPhase = ct.c_bool(True)
SPI_ClockPolarity = ct.c_bool(False)
SPI_BitDirection = ct.c_bool(True) # MSb first (1)
SPI_CharacterLength = ct.c_bool(False) # 8 bits (0)
SPI_CSType = ct.c_int(1) #(1) after every packet and (2) after every word
SPI_CSPolarity = ct.c_bool(True) #(active low)
DividerHigh =ct.c_byte(0)# high and low for 8000khz data rate 
DividerLow =ct.c_byte(3)

# DAC reigster addresses
NOP             = 0x00
SPICONFIG       = 0x03
DACPWDWN        = 0x09
DACRANGE0       = 0x0A
DACRANGE1       = 0x0B
DACRANGE2       = 0x0C
DACRANGE3       = 0x0D
DAC = [0x10, 0x11, 0x12, 0x13,
       0x14, 0x15, 0x16, 0x17,
       0x18, 0x19, 0x1A, 0x1B,
       0x1C, 0x1D, 0x1E, 0x1F]

#DAC read/write commannd
WRITE           = 0x3FFFFF

#DAC reg defaults
DACPWDWN_default = 0xFFFF


print("---------CONNECTING TO DAC--------- ")
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
dac_handle = u2aDll.u2aOpen (ct.byref(SerialNumber))
print(dac_handle)
print(type(dac_handle))

#sending the SPI settings 
s=u2aDll.u2aSPI_Control (dac_handle,SPI_ClockPhase,SPI_ClockPolarity,SPI_BitDirection,
                SPI_CharacterLength,SPI_CSType,SPI_CSPolarity,DividerHigh,
                DividerLow)
# print(s)

#for 3.3 v enabling the circuit
s=u2aDll.u2aPower_Enable (dac_handle,1,0,0)
#t.sleep(5)

# print("power")
# print(s)
# return dac_handle

def write_dac_reg(dac_handle,addr,msg):
##    data = 0b0<<23 | addr<<16 | msg
##    print('write : ',hex(data & 0xffffff))

    data = (c_uint8*3)()
    data[0] = (0b00000000 | addr)
    data[1] = (msg & 0xFF00)>>8
    data[2] = (msg & 0x00FF)
    print('write: ',hex(data[0]),hex(data[1]),hex(data[2]))
    s=u2aDll.u2aSPI_WriteAndRead (dac_handle,ct.c_byte(3),byref(data))
    return s

class Window:
    def __init__(self, master, dac_handle):
        self.master = master
         
        self.Main = Frame(self.master)

        # TOP SECTION
        self.top = Frame(self.Main)
 
        self.title = Label(self.top, text = "DAC81416 EVM control")
        self.title.grid(row=0, column=0)

        row_1 = Label(self.top, text="Turn DAC ON", width = 10)
        row_1.grid(row=1, column=0)
        self.dac_turn_on_checked = BooleanVar()
        self.turn_on_button = Checkbutton(self.top, text = "",
                                         command = self.turn_dac_on,
                                         variable = self.dac_turn_on_checked)
        self.turn_on_button.grid(row=1, column=1)
     
        self.top.pack(padx = 5, pady = 5)
        # TOP SECTION 
 
        # MIDDLE SECTION
        self.row = 16
        self.col = 4
        self.cells = [[None for i in range(self.col)] for j in range(self.row)]
        self.active_channels = [None for i in range(self.row)]
        self.i_val = [0 for i in range(self.row)]
        
        self.middle = Frame(self.Main) 

        startv = Label(self.middle, text="Start V", width = 10)
        startv.grid(row=0, column=1)

        stepv = Label(self.middle, text="Step V", width = 10)
        stepv.grid(row=0, column=2)

        mode = Label(self.middle, text="OFF/ON", width = 10)
        mode.grid(row=0, column=3)

        stopv = Label(self.middle, text="i", width = 10)
        stopv.grid(row=0, column=4)

        vnow = Label(self.middle, text="V now", width = 10)
        vnow.grid(row=0, column=5)

        for i in range(self.row):
            channel_i = Label(self.middle, text="Channel "+str(i))
            channel_i.grid(row=i+1, column=0)

            #Start V
            self.cells[i][0] = Entry(self.middle, width = 10)
            self.cells[i][0].grid(row = i+1, column = 1)

            #Step V
            self.cells[i][1] = Entry(self.middle, width = 10)
            self.cells[i][1].grid(row = i+1, column = 2)

            #OFF/ON
            self.active_channels[i] = BooleanVar()
            self.cells[i][2] = Checkbutton(self.middle, text = "",
                                             command = self.turn_channel_on,
                                             variable = self.active_channels[i])
            self.cells[i][2].grid(row=i+1, column=3)

            # i
            self.i_val[i] = StringVar()
            self.cells[i][3] = Spinbox(self.middle, from_=0, to=20,
                                       command = self.turn_channel_on,
                                       textvariable = self.i_val[i],
                                       width=5)
            self.cells[i][3].grid(row=i+1, column=4)

            #V now
            vnow_i = Label(self.middle, text="--", width = 20)
            vnow_i.grid(row=i+1, column=5)
 
         
        self.middle.pack(padx = 5, pady = 5)
        # MIDDLE SECTION
 
 
        # BOTTOM SECTION
        self.bottom = Frame(self.Main)
 
##        self.runButton = Button(self.bottom, text = "Run DAC", command = self.run_dac)
##        self.runButton.pack(padx = 5, pady = 5, side = RIGHT)
 
        self.saveButton = Button(self.bottom, text = "Save DAC settings", command = self.save_dac_settings)
        self.saveButton.pack(padx = 5, pady = 5, side = RIGHT)

        self.loadButton = Button(self.bottom, text = "Load DAC settings", command = self.load_dac_settings)
        self.loadButton.pack(padx = 5, pady = 5, side = RIGHT)
 
        self.resetButton = Button(self.bottom, text = "Reset DAC", command = self.reset_dac)
        self.resetButton.pack(padx = 5, pady = 5, side = LEFT)
         
        self.bottom.pack(padx = 5, pady = 5, expand = True, fill = X)
        # BOTTOM SECTION
         
        self.Main.pack(padx = 5, pady = 5, expand = True, fill = X)
 

    def turn_dac_on(self):
        if self.dac_turn_on_checked.get():
            write_dac_reg(dac_handle,SPICONFIG,0x0A86)
        if not self.dac_turn_on_checked.get():
            #write_dac_reg(dac_handle,DACPWDWN,0xFFFF)
            write_dac_reg(dac_handle,SPICONFIG,0x0AA4)

    def turn_channel_on(self):
        data_cycle_bits = 0xff0000
        for i in range(self.row):
            #print(self.active_channels[i].get(),end=' ')
            if self.active_channels[i].get():
                # get vstart, vstep and i_val
                vstart = float(self.cells[i][0].get()) if self.cells[i][0].get()!='' else 0.0
                vstep = float(self.cells[i][1].get()) if self.cells[i][1].get()!='' else 0.0
                i_val = int(self.i_val[i].get())
                v_now = vstart + i_val*vstep if vstart + i_val*vstep <=5.0*(1-1/2**16) else 5.0*(1-1/2**16)
                CODE = int(2**16*v_now/5.0)   # only for DAC RANGE 0
                #print(hex(CODE))
                vnow_i_label = Label(self.middle, text=str(CODE/2**16*5.0), width = 20)
                vnow_i_label.grid(row=i+1, column=5)
                #print(str(v_now))
                
                #write v_now to DAC_i
                dac_i_msg = 0b0<<23 | DAC[i]<<16 | CODE
                write_dac_reg(dac_handle,DAC[i],CODE)
                # 
                data_cycle_bits = data_cycle_bits | 0b1<<i
                
            else:
                vnow_i = Label(self.middle, text="--", width = 10)
                vnow_i.grid(row=i+1, column=5)
                
        #print(bin(data_cycle_bits))
        write_dac_reg(dac_handle,DACPWDWN,~data_cycle_bits)

##    def run_dac(self):
##        pass

    def save_dac_settings(self):
        print('save button clicked')

    def load_dac_settings(self):
        print('load button clicked')

    def reset_dac(self):
        print('reset button clicked')
        
    def save(self):
        file = open("data.txt", "w")
 
        for i in range(self.row):
            for j in range(self.col):
                file.write(self.cells[i][j].get() + ",")
            file.write("\n")
 
        file.close()
 
    def load(self):
        file = open("data.txt", "r")
 
        self.clear()
 
        for i in range(self.row):
            temp = file.readline()
            temp = temp.split(",")
            for j in range(self.col):
                self.cells[i][j].insert(0, temp[j].strip())
                 
    def clear(self):
 
        for i in range(self.row):
            for j in range(self.col):
                self.cells[i][j].delete(0, 'end')
 


##dac_handle = dac_setup()    
root = Tk()
window = Window(root,dac_handle)
root.mainloop()
