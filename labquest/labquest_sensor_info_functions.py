from labquest import config
from labquest import ngio_sensor_functions as ngio_sensor


def get_sensor_long_name_and_units():
    """ Return 1D list of strings that combines long name with units
    """

    long_name_and_units = []

    if any(config.enabled_analog_channels):
        for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
            for channel in device_enabled_chs:
                long = ngio_sensor.ddsmem_get_long_name(hDevice, channel)
                active_calpage = ngio_sensor.ddsmem_get_active_cal_page(hDevice, channel)
                active_cal0, active_cal1, active_cal2, active_units = ngio_sensor.ddsmem_get_cal_page(
                        hDevice, channel, index=active_calpage)
                
                string_name_with_units = long + active_units

                # build a list of the ngio_sensor's equation and calibration values for this device
                long_name_and_units.append(string_name_with_units)

    if any(config.enabled_dig_channels):    
        for dig_ch_dictionary in config.device_dig_channel_dictionary:
            for key in dig_ch_dictionary:  
            
                if dig_ch_dictionary[key] == 'motion':
                    string_name_with_units = "Position (cm)"
                elif dig_ch_dictionary[key] == 'photogate_count':
                    string_name_with_units = "Count"
                elif dig_ch_dictionary[key] == 'photogate_timing':
                    string_name_with_units = "Gate Time(s)"
                elif dig_ch_dictionary[key] == 'rotary_motion':
                    string_name_with_units = "Angle (degrees)"
                elif dig_ch_dictionary[key] == 'rotary_motion_high_res':
                    string_name_with_units = "Angle (degrees)"
                else:
                    string_name_with_units = ""
                if dig_ch_dictionary[key] not in ('dcu', 'dcu_pwm'):
                    long_name_and_units.append(string_name_with_units)

    return long_name_and_units

def get_sensor_info(device, channel):
    """ Return analog sensor ddsmem information
    """

    if channel == 1:
        sensor_info = config.device_channel_dictionary[device]["ch1"]
    elif channel == 2:
        sensor_info = config.device_channel_dictionary[device]["ch2"]
    else:
        sensor_info = config.device_channel_dictionary[device]["ch3"]

    return sensor_info
    