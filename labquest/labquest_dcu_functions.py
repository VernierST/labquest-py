from labquest import config
from labquest import ngio_send_cmd_get_resp as ngio_send

def set_io_line(*values):
    """Set the DCU line with Send Command Get Response - Write IO
    """

    i = 0
    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            parameters = [0]*14    # the ngio function is expecting up to 14 values in the parameters
            if key == "dig1":
                dig_channel = 5
            else:   # key == 'dig2':
                dig_channel = 6
            
            if dig_ch_dictionary[key] == 'dcu':
                
                command = 0x39    #define NGIO_CMD_ID_WRITE_IO 0x39
                # paraemters are configured for 14 values like (dig_channel,15,0,0,0,0,0,0,0,0,0,0,0,0)
                parameters[0] = dig_channel
                parameters[1] = 15    # this is the line1-line4 dig mask
                parameters[2] = values[i]    # output
                param_bytes = 3
                #parameters = (dig_channel, 15, values[i], 0,0,0,0,0,0,0,0,0,0,0)
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
                i += 1

def dcu_all_lines_off():
    """ Send parameters to set all dig lines off
    """

    i = 0
    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            parameters = [0]*14    # the ngio function is expecting up to 14 values in the parameters
            if key == "dig1":
                dig_channel = 5
            else:   # key == 'dig2':
                dig_channel = 6
            
            if dig_ch_dictionary[key] == 'dcu':
                
                command = 0x39    #define NGIO_CMD_ID_WRITE_IO 0x39
                # paraemters are configured for 14 values like (dig_channel,15,0,0,0,0,0,0,0,0,0,0,0,0)
                parameters[0] = dig_channel
                parameters[1] = 15    # this is the line1-line4 dig mask
                parameters[2] = 0    # output
                param_bytes = 3
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
                i += 1

def set_pwm(frequency_Hz, duty_cycle):
    """ Frequency range of 2.5 Hz (0.4 sec period) to 1,000,000 Hz (1 microsecond period)
    """
    # convert frequency to period (seconds)
    period = 1/frequency_Hz
    # convert period (seconds) to period (nanoseconds) and make sure it is unsigned int
    period = abs(int(period*1e+9))
    # convert duty cycle (0-100) to numerator (keeping denominator at 10,000)
    denominator = 10000
    numerator = abs(int((duty_cycle/100)*denominator))
    
    i = 0
    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            parameters = [0]*14    # the ngio function is expecting up to 14 values in the parameters
            if key == "dig1":
                dig_channel = 5
            else:
                dig_channel = 6   # pwm only works on dig1
                
            if dig_ch_dictionary[key] == 'dcu_pwm':
                if dig_channel == 6:
                    config.logger.error("Error - PWM output is only available from dig1, not dig2")
                command = 0x40    ##define NGIO_CMD_ID_SET_PWM_CONFIG 0x40
                parameters[0] = dig_channel
                parameters[1] = 1    # this is for the pwm state: running = 1, off = 0
                parameters[2:6] = int32_to_int8(period)
                #period_bytes = int32_to_int8(period)
                parameters[6:10] = int32_to_int8(numerator)
                #numerator_bytes = int32_to_int8(numerator)
                parameters[10:14] = int32_to_int8(denominator)
                #denominator_bytes = int32_to_int8(denominator)
                #parameters = (dig_channel, pwm_state) + period_bytes + numerator_bytes + denominator_bytes   # pwm state, period, numerator, denominator
                param_bytes = 14
                config.logger.debug("set_pwm: params " + str(parameters))
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
                i += 1

def int32_to_int8(n):
    """ convert the int32 value to four int8 values
    """
    mask = (1 << 8) - 1
    return tuple([(n >> k) & mask for k in range(0, 32, 8)])

def stop_pwm():
    """ send parameters to stop the pwm signal
    """
    i = 0
    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            parameters = [0]*14    # the ngio function is expecting up to 14 values in the parameters
            if key == "dig1" and dig_ch_dictionary[key] == 'dcu_pwm':
                dig_channel = 5
                command = 0x40    ##define NGIO_CMD_ID_SET_PWM_CONFIG 0x40
                parameters[0] = dig_channel
                parameters[1] = 0    # this is for the pwm state: running = 1, off = 0
                param_bytes = 2
                ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
                i += 1

            