import time

from labquest import config
from labquest import ngio_open_functions as ngio_open
from labquest import ngio_send_cmd_get_resp as ngio_send

def open_labquest_devices():
    """ Find connected LQ devices and open the handle (hDevice)
    """
    
    # Determine what LabQuest device(s) are connected
    config.device_type, device_type_name = search_for_a_labquest_device()
    if not config.device_type: 
        return "no_device"
    else:
        config.logger.info("Found device type: " + str(device_type_name))
    
    # Get the device handle(s) and save as 'hDevice' in the config file
    config.hDevice, number_found_devices = get_device_handle_and_num_devices()
    if not config.hDevice:
        config.logger.info("No device handle (hDevice)")
        return "no_device"
    else:
        config.logger.info("Number devices found: " + str(number_found_devices))
        config.logger.info("Number of device handles opened: " + str(len(config.hDevice)))

    # If a LQ Mini is connnected, set the LabQuest LED to green
    if config.device_type == 12:
        set_lq_mini_led_green(config.hDevice)
    # the labquest devices with built-in app (lq2, lq3) require this next call to take control of the app
    else:
        for hDevice in config.hDevice:
            ngio_open.acquire_exclusive_ownership(hDevice)

    return device_type_name


def search_for_a_labquest_device():
    """ Search for a connected LabQuest device and return the device_type
    and the device_type_name.
    """

    # OriginalLQ = 5, Mini = 12, LQ2 = 14, LQStream = 17, LQ3 = 19
    find_device_type = [5,12,14,17,19]  
    device_type_name_list = ["Original LQ", "LQ Mini", "LQ2", "LQ Stream", "LQ3"]
    
    i = 0 
    for device_type in find_device_type:
        device_list_signature = ngio_open.search_for_device(device_type)
        # Check the device list signature to determine if a device has been found
        if device_list_signature != 0:
            device_type_name = device_type_name_list[i]
            break
        else:
            device_type = 0
            device_type_name = ""
        i += 1

    return device_type, device_type_name 

def get_device_handle_and_num_devices():
    """ Determine how many of the device types are connected. For each of these connected
    devices, get a device handle (hDevice).
    """

    config.logger.info("attempting to open device...")
    device_handle_list = []
    index = 0
    open_a_device = True
    while open_a_device:    
        # Get the Device List Handle (hDeviceList) and the number of devices connected.
        hDeviceList, number_of_devices = ngio_open.open_device_list_snapshot()       
        # Get a device name for each found device
        device_name = ngio_open.snapshot_get_nth_entry(hDeviceList, index)
        # Close device list snapshot
        ngio_open.close_device_list_snapshot(hDeviceList)
        # Get the Device Handle (hDevice)
        hDevice = ngio_open.device_open(device_name)

        if hDevice != 0:
            device_handle_list.append(hDevice)
        else:
            device_handle_list = []
            number_of_devices = 0
            break
        
        index += 1
        # Determine if another device is available to be opened
        open_a_device = number_of_devices  > index  
    
    return device_handle_list, number_of_devices

def set_lq_mini_led_green(hDevice):
    """ The LQ Mini has an LED. Turn this green to signify a proper connection
    """

    i = 0
    while i < len(hDevice):
        # if there is a second device, pause for a sec so the user can determine which is dev1
        if i > 0:
            time.sleep(2)
        parameters = [0]*14
        command = 0x1D   # SET_LED_STATE = 1D
        parameters[0] = 0
        parameters[1] = 0x80   # NGIO_LED_COLOR_GREEN 0x80
        parameters[2] = 8
        param_bytes = 3
        ngio_send.send_cmd_get_response(hDevice[i], command, parameters, param_bytes)
        config.logger.info("Green LED turned on: Device " + str(i))
        i+=1