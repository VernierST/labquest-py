from time import sleep

from labquest import config
from labquest import ngio_stop_functions as ngio_stop
from labquest import ngio_send_cmd_get_resp as ngio_send
from labquest import labquest_read_functions as read


def stop_measurements_clear_buffer():
    """ Stop data collection and clear both the NGIO buffer and config.buffer
    """

    # Stop the measurements
    for hDevice in config.hDevice:
        parameters = [0]*14
        command = 0x19   #STOP MEASUREMENTS = 19
        param_bytes = 0
        ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)       

    # Clear the NGIO measurement buffer by reading any values remaining
    sleep(1)
    read.clear_the_lq_measurement_buffer()

    # Clear the buffer
    config.buffer = []

def close():
    """ Close any LabQuest handles, call NGIO Uninit, and reset the variables in the config file
    """

    # if no devices, no device handle, or no sensors then do not try to close
    if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
        pass
    else: 
        # Close the device
        for hDevice in config.hDevice:
            closed = ngio_stop.device_close(hDevice) 

    # Call NGIO_Uninit() once to 'undo' NGIO_Init()
    ngio_stop.ngio_uninit()  

    # clear all the variables in the config.py file   
    config.logger = None 
    config.buffer = []   
    config.rotary_buffer =[]
    config.dll = None   
    config.hLib = None   
    config.hDevice = []    
    config.device_type = None    
    config.enabled_analog_channels = []  
    config.enabled_dig_channels = []    
    config.enabled_all_channels = []    
    config.motion = False    
    config.photogate = False   
    config.photogate_timing = False
    config.rotary_motion = False  
    config.rotary_motion_high_res = False 
    config.dcu = False  
    config.dcu_pwm = False
    config.sample_period = None
    config.op_type_list = []   
    config.probe_type_list = []
    config.sensor_cal_list = []   
    config.device_dig_channel_dictionary = []   
    config.device_channel_dictionary = []


