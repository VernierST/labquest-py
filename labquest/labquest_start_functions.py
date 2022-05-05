from labquest import config
from labquest import ngio_start_functions as ngio_start
from labquest import ngio_send_cmd_get_resp as ngio_send


def configure_channels_to_start(period, reset_dig_counter):
    """
    Prior to starting data collection, there are a few steps that need to happen, depending
    on what sensors are connected: Configure analog channel as 5V or 10V, set the mask value, 
    set the digital sampling mode, reset the digital counter, and configure io lines as output, 
    as needed.
    """

    config.sample_period = period
    set_the_sampling_period()

    # Set the analog input value. Configure as a 5V channel or a 10V channel
    if any(config.enabled_analog_channels):
        configure_channels_as_5V_or_10V()

    # Set the mask value. This is a hex value corresponding to the list of enabled channels
    mask_list = get_the_mask_value()
    for hDevice, mask in zip(config.hDevice, mask_list):
        parameters = [0]*14
        command = 0x2C    #SET_SENSOR_CHANNEL_ENABLE_MASK = 0x2C
        config.logger.debug("start() - set the mask value: " + str(mask))
        parameters[0] = mask
        param_bytes = 4
        ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)

    # Configure digital lines for the various digital sensors
    if any(config.enabled_dig_channels):
        set_dig_ch_sampling_mode()
        # reset the counter for photogate and rotary motion
        if reset_dig_counter:
            reset_digital_counter()
        else:
            pass
        # configure io lines as outputs if a dcu is connected
        if config.dcu or config.dcu_pwm:
            set_dig_io_lines_as_outputs()

def set_the_sampling_period():
    """ Set the sampling period for all channels
    """

    for hDevice in config.hDevice:
        # set the measurment period for all channels = -1
        channel = -1
        # note that the period is the desired measurement period in seconds
        ngio_start.set_measurement_period(hDevice, channel, config.sample_period)
        sampling_rate = 1/float(ngio_start.get_measurement_period(hDevice, channel))

    config.logger.info("Measurment period:" + str(config.sample_period) + " seconds/sample") 
    config.logger.info("Sampling rate:" + str(sampling_rate) + " samples/sec")

def configure_channels_as_5V_or_10V():
    """ Configure each active analog channel as a 5V channel or a 10V channel
    """

    for hDevice, device_enabled_chs, device_op_type_list in zip(config.hDevice, config.enabled_analog_channels, 
                                                                config.op_type_list):
        for channel, operation_type in zip(device_enabled_chs, device_op_type_list):
            # If (2 == OperationType) then the sensor is kProbeTypeAnalog10V, else kProbeTypeAnalog5V
            parameters = [0]*14
            if operation_type == 2:
                probe_type = 4    # note that this is a different "probe_type" than the "probe_type_list"
            else:
                probe_type = 0
            command = 0x21     #SET_ANALOG_INPUT = 0x21
            parameters[0] = channel
            parameters[1] = probe_type
            param_bytes = 2
            ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes) 

def get_the_mask_value():
    """ Get the mask value. This is a hex value corresponding to what channels are enabled
    """
    
    mask_list = []

    i = 0
    while i < len(config.hDevice):

        device_mask_list = []
        
        if any(config.enabled_analog_channels):
            device_enabled_chs = config.enabled_analog_channels[i]
            if device_enabled_chs:
                for channel in device_enabled_chs:
                    # mask hex values for enabled channels: ch1 = 0x2, ch2 = 0x4, ch3 = 0x8
                    if channel == 1:
                        mask = 0x2
                    elif channel == 2:
                        mask = 0x4
                    elif channel == 3:
                        mask = 0x8
                    else:
                        mask = 0
                    device_mask_list.append(mask)
        
        # now determine the mask of the digital channels
        if any(config.enabled_dig_channels):
            dig_dict = config.device_dig_channel_dictionary[i]
            for key in dig_dict:
                if key == "dig1":
                    if dig_dict[key] in ('motion', 'rotary_motion', 'rotary_motion_high_res', 
                                        'photogate_count', 'photogate_timing'):
                        mask = 0x20  
                    else:
                        mask = 0    # if dcu is connected it does not add to the mask     
                elif key == "dig2":
                    if dig_dict[key] in ('motion', 'rotary_motion', 'rotary_motion_high_res', 
                                        'photogate_count', 'photogate_timing'):
                        mask = 0x40
                    else:
                        mask = 0
                else:
                    mask = 0
                device_mask_list.append(mask)
                # create mask by summing the hex values for all of the enabled channels    
        mask_sum = sum(device_mask_list)
        mask_list.append(mask_sum)
        
        i += 1
         
    return mask_list
    
def set_dig_ch_sampling_mode():
    """ Call the Set Sampling Mode command for digital channels
    """

    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            parameters = [0]*14
            if key == "dig1":
                dig_channel = 5
            elif key == 'dig2':
                dig_channel = 6
            else:
                break

            if dig_ch_dictionary[key] == 'no_sensor':
                pass
            elif dig_ch_dictionary[key] == 'motion':
                sampling_mode = 3   #define NGIO_SAMPLING_MODE_PERIODIC_MOTION_DETECT 3
            elif dig_ch_dictionary[key] == 'photogate_timing':
                sampling_mode = 1   #define NGIO_SAMPLING_MODE_APERIODIC_EDGE_DETECT 1
            elif dig_ch_dictionary[key] == 'photogate_count': 
                sampling_mode = 2   #define NGIO_SAMPLING_MODE_PERIODIC_PULSE_COUNT 2
            elif dig_ch_dictionary[key] == 'rotary_motion':
                sampling_mode = 4    #define NGIO_SAMPLING_MODE_PERIODIC_ROTATION_COUNTER 4
            elif dig_ch_dictionary[key] == 'rotary_motion_high_res':
                sampling_mode = 5    #define NGIO_SAMPLING_MODE_PERIODIC_ROTATION_COUNTER_X4 5
            elif dig_ch_dictionary[key] in ('dcu', 'dcu_pwm'):
                sampling_mode = 6    #define NGIO_SAMPLING_MODE_CUSTOM 6
            else:
                config.logger.debug("Invalid dig ch dictionary key")
            
            if dig_ch_dictionary[key] != 'no_sensor': 
                command = 0x29    #define NGIO_CMD_ID_SET_SAMPLING_MODE 0x29
                parameters[0] = dig_channel
                parameters[1] = sampling_mode
                param_bytes = 2
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)

def reset_digital_counter():
    """ reset the digital counter to zero
    """
    
    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            parameters = [0]*14
            if key == "dig1":
                dig_channel = 5
            elif key == 'dig2':
                dig_channel = 6
            else:
                break
            
            if dig_ch_dictionary[key] in ('photogate_count', 'rotary_motion', 'rotary_motion_high_res'):
                command = 0x32    #define NGIO_CMD_ID_SET_DIGITAL_COUNTER 0x32
                parameters[0] = dig_channel
                parameters[1] = 0    # resets the counter to 0
                param_bytes = 2
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
            

def set_dig_io_lines_as_outputs():
    """ If connecting a DCU the dig lines get configured as outputs
    """
    
    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            parameters = [0]*14
            if key == "dig1":
                dig_channel = 5
            elif key == 'dig2':
                dig_channel = 6
            else:
                break
            
            if dig_ch_dictionary[key] in ('dcu', 'dcu_pwm'):
                command = 0x39    #define NGIO_CMD_ID_WRITE_IO 0x39
                command_config = 0x37   #define NGIO_CMD_ID_WRITE_IO_CONFIG 0x37
                parameters[0] = dig_channel
                parameters[1] = 15    # dig1..dig4 mask value
                parameters[2:4] = 0,0    #
                param_bytes = 4
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
                ngio_send.send_cmd_get_response(hDevice, command_config, parameters, param_bytes)
                
            if dig_ch_dictionary[key] == 'dcu':   # do not make this extra call if setting up for pwm
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
                
            

def start_measurements():
    """ Send the Start Measurements command
    """

    for hDevice in config.hDevice:
        parameters = [0]*14    # the ngio function is expecting up to 14 values in the parameters
        command = 0x18    #define NGIO_CMD_ID_START_MEASUREMENTS 0x18
        param_bytes = 0
        ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
