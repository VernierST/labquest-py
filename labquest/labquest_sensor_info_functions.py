from labquest import config
from labquest import ngio_sensor_functions as ngio_sensor


def get_sensor_long_name_and_units(device_index, ch):
    """ Return a string that combines the sensor's long name with units
    """
    
    if ch == 'ch1':
            channel = 1
    if ch == 'ch2':
            channel = 2
    if ch == 'ch3':
            channel = 3
    
    hDevice = config.hDevice[device_index]

    if ch in ('ch1', 'ch2', 'ch3'):
        long = ngio_sensor.ddsmem_get_long_name(hDevice, channel)
        active_calpage = ngio_sensor.ddsmem_get_active_cal_page(hDevice, channel)
        active_cal0, active_cal1, active_cal2, active_units = ngio_sensor.ddsmem_get_cal_page(
                hDevice, channel, index=active_calpage)
        
        string_name_with_units = long + active_units

    # this would be the case of ch = 'dig1' or 'dig2'
    else:  
        dig_ch_dictionary = config.device_dig_channel_dictionary[device_index]
        
        for key in dig_ch_dictionary:  
            if key == ch:
                if dig_ch_dictionary[key] == 'motion':
                    string_name_with_units = "Position (m)"
                elif dig_ch_dictionary[key] == 'photogate_count':
                    string_name_with_units = "Count"
                elif dig_ch_dictionary[key] == 'photogate_timing':
                    string_name_with_units = "Gate Time(s)"
                elif dig_ch_dictionary[key] == 'rotary_motion':
                    string_name_with_units = "Angle (degrees)"
                elif dig_ch_dictionary[key] == 'rotary_motion_high_res':
                    string_name_with_units = "Angle (degrees)"
                else:
                    string_name_with_units = "?"
                    config.logger.debug("dig ch value not found. Check the dig ch arguments for spelling and correct ch ")
                break
            else:
                config.logger.debug("dig ch does not appear to be the selected channel")
                string_name_with_units = "?"
    return string_name_with_units

def get_sensor_info(device, ch):
    """ Return analog sensor ddsmem information
    """

    sensor_info = config.device_channel_dictionary[device][ch]
    
    return sensor_info
    