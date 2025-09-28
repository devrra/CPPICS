# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:45:36 2024

@author: 
"""

import numpy as np
#import pyvisa
import time
# from PyApex import AP2XXX
#from drawnow import drawnow
import matplotlib.pyplot as plt

#import In_nano_and_out_nano as ino

import velox as vx #this should be kept in python -lib
#SipTools needs to in 
import SiPTools  as sip

import os
import json
import pandas as pd

# Importing modules from the santec directory
from santec import TslInstrument, MpmInstrument, SpuDevice, GetAddress, file_saving, StsProcess

DWELL_TIME_CONSTANT = 10
MILLISECONDS_TO_SECONDS_CONSTANT = 1000


def setting_tsl_sweep_params(connected_tsl: TslInstrument, previous_param_data: dict) -> None:
    """
    Set sweep parameters for the TSL instrument.

    Parameters:
        connected_tsl (TslInstrument): Instance of the TSL class.
        previous_param_data (dict): Previous sweep process data, if available.

    Returns:
        None
    """
    if previous_param_data is not None:
        start_wavelength = float(previous_param_data["start_wavelength"])
        stop_wavelength = float(previous_param_data["stop_wavelength"])
        sweep_step = float(previous_param_data["sweep_step"])
        sweep_speed = float(previous_param_data["sweep_speed"])
        power = float(previous_param_data["power"])

        print("Start Wavelength (nm): " + str(start_wavelength))
        print("Stop Wavelength (nm): " + str(stop_wavelength))
        print("Sweep Step (nm): " + str(sweep_step))  # nm, not pm.
        print("Sweep Speed (nm): " + str(sweep_speed))
        print("Output Power (dBm): " + str(power))
    else:
        start_wavelength = float(input("\nInput Start Wavelength (nm): "))
        stop_wavelength = float(input("Input Stop Wavelength (nm): "))
        sweep_step = float(input("Input Sweep Step (pm): ")) / 1000

        if connected_tsl.get_tsl_type_flag():
            sweep_speed = float(input("Input Sweep Speed (nm/sec): "))
        else:
            num = 1
            print('\nSpeed table:')
            for i in connected_tsl.get_sweep_speed_table():
                print(str(num) + "- " + str(i))
                num += 1
            speed = input("Select a sweep speed (nm/sec): ")
            sweep_speed = connected_tsl.get_sweep_speed_table()[int(speed) - 1]

        power = float(input("Input Output Power (dBm): "))
        while power > 10:
            print("Invalid value of Output Power ( <=10 dBm )")
            power = float(input("Input Output Power (dBm): "))

    # Set TSL parameters
    connected_tsl.set_power(power)
    connected_tsl.set_sweep_parameters(start_wavelength, stop_wavelength, sweep_step, sweep_speed)


def prompt_and_get_previous_param_data(file_last_scan_params: str) -> dict | None:
    """
    Prompt user to load previous parameter settings if available.

    Parameters:
        file_last_scan_params (str): Path to the file containing last scan parameters.

    Returns:
        dict: Previous settings loaded from the file, or None if not available.
    """
    if not os.path.exists(file_last_scan_params):
        return None

    # ans = input("\nWould you like to load the most recent parameter settings from {}? [y|n]: "
    #             .format(file_last_scan_params))
    ans = 'y'
    if ans not in "Yy":
        return None

    # Load the json data.
    with open(file_last_scan_params, encoding='utf-8') as json_file:
        previous_settings = json.load(json_file)

    return previous_settings


def prompt_and_get_previous_reference_data() -> dict | None:
    """
    Ask user if they want to use the previous reference data if it exists.

    Returns:
        dict: Previous reference data loaded from the file,
        None: if reference data is not available.
    """
    if not os.path.exists(file_saving.FILE_LAST_SCAN_REFERENCE_DATA):
        return None

    # ans = input("\nWould you like to use the most recent reference data from file '{}'? [y|n]: "
    #             .format(file_saving.FILE_LAST_SCAN_REFERENCE_DATA))
    ans = 'y'

    if ans not in "Yy":
        return None

    # Get the file size.
    int_file_size = int(os.path.getsize(file_saving.FILE_LAST_SCAN_REFERENCE_DATA))
    str_file_size = f"{int_file_size / 1000000:.2f} MB" if int_file_size > 1000000 else f"{int_file_size / 1000:.2f} KB"

    print("Opening " + str_file_size + " file '" + file_saving.FILE_LAST_SCAN_REFERENCE_DATA + "'...")
    with open(file_saving.FILE_LAST_SCAN_REFERENCE_DATA, 'r', encoding='utf-8') as file:
        data = file.read()
        previous_reference = json.loads(data)
    return previous_reference


def save_all_data(ilsts: StsProcess) -> None:
    """
    Save measurement and reference data to files.

    Parameters:
        ilsts (StsProcess): Instance of the ILSTS class.

    Returns:
        None
    """
    print("\n")
    # Saving reference data to file
    file_saving.save_reference_data(ilsts, file_saving.FILE_LAST_SCAN_REFERENCE_DATA)

    print("Saving Reference data csv to file " + file_saving.FILE_REFERENCE_DATA_RESULTS + "...")
    file_saving.save_reference_result_data(ilsts, file_saving.FILE_REFERENCE_DATA_RESULTS)

    print("Saving Raw data to csv file " + file_saving.FILE_RAW_DATA_RESULTS + "...")
    file_saving.save_dut_result_data(ilsts, file_saving.FILE_RAW_DATA_RESULTS)

    print("Saving IL data to csv file " + file_saving.FILE_IL_DATA_RESULTS + "...")
    file_saving.save_measurement_data(ilsts, file_saving.FILE_IL_DATA_RESULTS)


def plot_wavelength_dependent_loss(wavelength: list, il_data: list, title):
    """
    Plot the Wavelength-Dependent Loss results.

    Args:
        wavelength (list): Array of wavelength values.
        il_data (list): Array of Insertion loss values.
    """
    try:
        plt.plot(wavelength, il_data)
        plt.title(title)
        plt.show()
    except Exception as e:
        print(f"Error while displaying graph, {e}")


def plot_power_reading(power_array, power_reading):
    """
    Plot the power sweep results.

    Args:
        power_array (list): Array of power values.
        power_reading (list): Corresponding power readings.
    """
    try:
        print("Displaying power sweep results.")
        plt.plot(power_array, power_reading)
        max_y_axis = max(power_reading)
        min_y_axis = min(power_reading)
        step_y_axis = (max_y_axis - min_y_axis) / 10
        plt.yticks(np.arange(min_y_axis, max_y_axis, step_y_axis))
        plt.show()
    except Exception as e:
        print(f"Error while displaying power sweep results, {e}")


def connection():
    """ Detect and connect to the TSL, MPM and DAQ instruments. """
    tsl: TslInstrument
    mpm: MpmInstrument
    daq: SpuDevice

    device_address = GetAddress()
    device_address.initialize_instruments()

    tsl_instrument = device_address.get_tsl_address()
    mpm_instrument = device_address.get_mpm_address()

    # # tsl = TslInstrument(ip_address="192.168.1.100",interface="LAN")
    # tsl = TslInstrument(instrument="GPIB1::2::INSTR",interface="GPIB")
    # tsl.connect()

    # # mpm = MpmInstrument(ip_address="192.168.1.161",interface="LAN")
    # mpm = MpmInstrument(instrument="GPIB1::16::INSTR",interface="GPIB")
    # mpm.connect()
    1
    tsl = TslInstrument(instrument=tsl_instrument)
    tsl.connect()
    mpm = MpmInstrument(instrument=mpm_instrument)
    mpm.connect()

    if "220" in mpm.idn():
        return tsl, mpm, None

    daq_address = device_address.get_daq_address()
    daq = SpuDevice(device_name=daq_address)
    daq.connect()

    return tsl, mpm, daq


def tsl_power_check(tsl: TslInstrument):
    """ Check and limit TSL power to 5dBm. """
    current_set_power = tsl.power
    power = 0.00
    if current_set_power > 5.00:
        print("\nPower value should not be greater than 5 dBm.")
        power = float(input("Please input Output Power (dBm) again: "))
        while power > 5.00:
            print("\nInvalid value of Output Power ( <=5 dBm )")
            power = float(input("Please input Output Power (dBm): "))

    tsl.set_power(power)


def wavelength_dependent_loss(tsl, mpm, daq, filename):
    """
    Perform the wavelength-dependent loss measurement.

    Args:
        tsl: The tsl instrument.
        mpm: The mpm instrument.
        daq: The daq device.
    """
    # Set the TSL properties
    previous_param_data = prompt_and_get_previous_param_data(file_saving.FILE_LAST_SCAN_PARAMS)
    setting_tsl_sweep_params(tsl, previous_param_data)

    # Initiate and run the ILSTS
    if mpm:
        ilsts = StsProcess(tsl, mpm, daq)

        # Select channels to be measured.
        ilsts.set_selected_channels(previous_param_data)
        if ilsts.mpm_215_selection_check():
            tsl_power_check(tsl)
            ilsts.selected_ranges = [2]
        else:
            ilsts.set_selected_ranges(previous_param_data)

        # Set Sweep parameters to MPM and DAQ
        ilsts.set_parameters()

        # Check for previously saved reference data
        previous_ref_data_array = None
        if previous_param_data:
            previous_ref_data_array = prompt_and_get_previous_reference_data()
        if previous_ref_data_array:
            ilsts.reference_data_array = previous_ref_data_array

        # Saving parameters to file
        if not previous_param_data:
            file_saving.save_sts_parameter_data(tsl, ilsts, file_saving.FILE_LAST_SCAN_PARAMS)

        # Run a reference scan if previously saved reference data not found
        # if len(ilsts.reference_data_array) == 0:
        #     print("\nConnect for Reference measurement and press ENTER")
        #     print("Reference process:")
        #     # IL STS reference scan
        #     ilsts.sts_reference()
        # else:
        #     print("Loading reference data...")
        #     ilsts.sts_reference_from_saved_file()
        print("Loading reference data...")
        ilsts.sts_reference_from_saved_file()

        # Perform the sweep operation
        # ans = "y"
        # while ans in "yY":
        print("\nDUT measurement")
        while True:
            reps = 1#int(input("Input DUT scan repeat count (greater than 0): "))
            if reps > 0:
                break
            print("Invalid repeat count, enter a positive number.\n")
        # input("Connect the DUT and press ENTER")
        for i in range(reps):
            scan_index = i + 1
            print("\nScan {} of {}...".format(str(scan_index), reps))

            # IL STS measurement scan
            ilsts.sts_measurement()

            user_map_display = 'y'#input("\nDo you want to view the graph ?? (y/n): ")
            if user_map_display == "y":
                plot_wavelength_dependent_loss(ilsts.wavelength_table, ilsts.il, filename)

            if reps > 1 and scan_index < reps:
                pass# input(f"\nPress ENTER to continue to Scan {scan_index + 1}...")
            # time.sleep(5)
        ilsts.get_dut_data()  # Get and store DUT scan data

        # ans = input("\nRedo Scan ? (y/n): ")

        # save_all_data(ilsts)
        return ilsts.wavelength_table, ilsts.il


def power_sweep(tsl, mpm):
    """
    Perform a power sweep measurement.

    Args:
        tsl: The tsl device.
        mpm: The powermeter (mpm).
    """
    # MPM setting
    mpm_mod, mpm_chan = input('\nSelect Powermeter Module and Channel (Ex: Module,Channel => 0,1): ').split(',')
    avg_time = float(input('Set Averaging time for the powermeter (0.01~10000.00) [msec]: '))

    mpm.write('AUTO')  # Set automatic gain for the powermeter
    mpm.write(f'AVG {avg_time}')

    # TSL setting
    set_wl = float(input('Set characterization wavelength [nm]: '))
    start_pow = float(input('Input start power [dBm]: '))
    stop_pow = float(input('Input stop power [dBm]: '))
    step_pow = float(input('Input power step [dB]: '))

    tsl.set_wavelength(set_wl)
    tsl.write(f'POW {start_pow}')

    if start_pow > stop_pow:
        step_pow = -step_pow

    # The dwelling time is set 10 times longer than the averaging time of the powermeter
    dwell_time = DWELL_TIME_CONSTANT * avg_time / MILLISECONDS_TO_SECONDS_CONSTANT

    power_reading, power_array = [], []
    actual_pow = start_pow
    while actual_pow != stop_pow + step_pow:
        # print(actual_pow)
        power_array.append(actual_pow)

        # Read power from the MPM
        raw_pow = mpm.query(f'READ? {mpm_mod}')[1].split(',')
        power_reading.append(
            float(raw_pow[int(mpm_chan) - 1]))  # Channels are from 1 to 4 and arrays are from 0 to 3, thus "-1"
        time.sleep(dwell_time)
        actual_pow = round(actual_pow + step_pow, 2)
        tsl.write(f'POW {actual_pow}')

    # Plot results
    plot_power_reading(power_array, power_reading)

    print("\nSaving power sweep data to file " + file_saving.FILE_POWER_SWEEP_RESULTS + "...")
    file_saving.save_power_sweep_results(power_array, power_reading, file_saving.FILE_POWER_SWEEP_RESULTS)

def main():
    tsl, mpm, daq = connection()
    
    with vx.MessageServerInterface() as msgServer:
        ########################### USER INPUTS ###################################
        diemap_path = "C:\\Users\\User\\Desktop\\Single_fiber__Cal_22042025\\DieMaprid_small.txt"
        Wafer_ID = "TCS3_HOTLOT"
        die_list = [14]#[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
        sub_die_list = list(range(1,12+1))#,19,20,21,22,23,24,25,26,27,28] #[1,2,3,4,5,6,7]
        data_output_folder = "D:\\Users\\Yash\\MRR\\"
        ###########################################################################
        
        response = vx.IsAppRegistered('Kernel')
        
        if response < 0 :
            print('Could not register application.')
        # vx.SetCameraLight("Scope", "1" ,"1" ,"0" ,"44" ,"48" ,"0")
        
        ## STS setup
        # tsl, mpm, daq = connection()
        
        # write the no. of subdies
        print(sip.GetSiPToolsVersion())
        
        print(sip.DeleteAllOpticalSubDie())
        print(vx.GoToWaferHome())
        print(vx.AutoAlign())
        print(vx.GoToWaferHome())
        print(vx.MoveScope(0,0,"C","Y",50))
        print(vx.MoveChuckSeparation(50))
        
        ## DieMap Management
        
        dienum = sip.ImportOpticalDieMap(diemap_path)
        # print(sip.TrainOpticalDieMap("A","A",0,1))
        for i in range(int(dienum[0])):
            print(sip.OptimizeSubDiePositions(i+1, 1, "D"))
        
        print(vx.MoveChuckContact(50))
        print(vx.MoveScopeFocus(50))
        
        start = time.time()
        
        # Don't edit below lists
        die_sequence_x = [-1,0,1,2,-2,-1,0,1,2,3,-2,-1,0,1,2,3,-2,-1,0,1,2,3,-1,0,1,2]
        die_sequence_y = [1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,5,5,5,5]
        
        threshold = -60
        
        PCadjusted = False
        
        for i in range(len(die_list)):
            #separate fibers
            # print(vx.StepNextDie(die_sequence_x[die_list[i]-1],die_sequence_y[die_list[i]-1],1))
            print(vx.StepNextDie(die_sequence_x[die_list[i]-1],die_sequence_y[die_list[i]-1]))
            
            for j in range(len(sub_die_list)):
                print(sip.MoveOpticalSubDie(sub_die_list[j]))
                tsl.set_wavelength(1550)
                print(sip.AlignOpticalProbes(PThresh=threshold))
                if not PCadjusted:
                    input('Adjust Polarization Controller.. then Press Enter')
                    PCadjusted = True
                df = pd.read_csv(diemap_path,skiprows=3)
                datafilename = "{}_R{}_{}.csv".format(Wafer_ID,die_list[i],df.iloc[2*sub_die_list[j]-2]['Label'])
                # Perform the sweeps
                print("\nDUT measurement")
                reps = 1
                for _ in range(int(reps)):
                    print("\nScanning : {}".format(datafilename))
                    wavelength, IL =  wavelength_dependent_loss(tsl, mpm, daq, datafilename)
                    df = pd.DataFrame([wavelength, IL])
                    df  = df.transpose()
                    df.to_csv(data_output_folder+datafilename,index=False,header=['wavelength[nm]', 'IL[dB]'])
                time.sleep(1)
            
        end = time.time()
        print(end-start)
        # sip.StopSiPTools()

if __name__ == "__main__":
    main()