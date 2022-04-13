from time import sleep
import math

from labquest import config
from labquest import ngio_read_functions as ngio_read


def get_all_measurements():
    """ Get measurements from all configured channels (analog and digital)
    """

    all_measurements = []

    if any(config.enabled_analog_channels):
        analog_measurements = get_analog_measurements()
        if analog_measurements is None:
            pass
        else:
            all_measurements.extend(analog_measurements)
    
    if any(config.enabled_dig_channels):
        if config.motion:
            motion_measurements = get_motion_measurements()
            if motion_measurements is None:
                pass
            else:
                all_measurements.extend(motion_measurements)

        if config.rotary_motion or config.rotary_motion_high_res:
            rotary_measurements = get_rotary_measurements()
            if rotary_measurements is None:
                pass
            else:
                all_measurements.extend(rotary_measurements)

        if config.photogate:
            photogate_measurements = get_photogate_measurements()
            if photogate_measurements is None:
                pass
            else:
                all_measurements.extend(photogate_measurements)
        
    return all_measurements

def get_analog_measurements():
    """
    Get a single analog sensor(s) measurement. This may be from the buffer, or as a new reading.
    """

    # Are there data in the buffer? If so, read the buffer, not the sensor
    if config.buffer:
        config.logger.debug("data in the buffer = " + str(config.buffer))
        measurements = pull_value_from_buffer()
        return measurements     

    # The buffer is empty, so first check that there are measurements available
    config.buffer = [] 
    
    num_measurements_available = number_measurements_available(config.sample_period)
    config.logger.debug("number of measurements available: " +str(num_measurements_available))
    if 0 in num_measurements_available:
        config.logger.debug("Timed Out - no measurements available to read")
        measurements = []
    else:
        max_num_measurements_available = max(num_measurements_available)
        # Get the measurements list. The list contains one value for each channel in 
        # proper sensor units. Excess data are placed in the buffer.
        measurements = read_and_calibrate_data(max_num_measurements_available)
    
    return measurements

def get_multi_pt_measurements(num_measurements_to_read):
    """ Get a packet of analog sensor measurements.
    """

    # make sure there is at least one available, then ask to read all measurements
    num_measurements_available = number_measurements_available_multipt(config.sample_period, num_measurements_to_read)
    config.logger.debug("num msrmnts available = " + str(num_measurements_available))
    if 0 in num_measurements_available:
        config.logger.debug("Timed Out - no measurements available to read")
        measurements = []
    else:
        measurements = read_and_calibrate_multi_pt_data(num_measurements_to_read)

    return measurements


def pull_value_from_buffer():
    """ Pull a single analog sensor reading for each sensor out of the buffer.
    """

    measurements = []

    i = 0
    for i in range(len(config.buffer)):
        pop_values = config.buffer[i].pop(0)
        measurements.append(pop_values)
    # if this was the last value in the buffer, clear the list so that it is not a list of empty lists
    if not config.buffer[0]:
        config.buffer = []
    
    return measurements 

def pull_value_from_rotary_buffer():
    """ Pull a single rotary motion sensor reading for each sensor out of the buffer.
    """

    measurements = []

    i = 0
    for i in range(len(config.rotary_buffer)):
        pop_values = config.rotary_buffer[i].pop(0)
        measurements.append(pop_values)
    # if this was the last value in the buffer, clear the list so that it is not a list of empty lists
    if not config.rotary_buffer[0]:
        config.rotary_buffer = []
    
    return measurements 

def number_measurements_available(sample_period):
    """ Return a list of how many analog sensor measurements are availabe for each active channel.
    """

    num_measurements_list = []
    
    for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
        for channel in device_enabled_chs:
            x = 0 
            # Perform a total of 30 iterations (3x the sample period), waiting for data.
            while x < 30: 
                num_measurements_available = ngio_read.get_num_measurements_available(hDevice, channel)  
                if num_measurements_available >= 1: 
                    config.logger.debug("ch = " + str(channel) + " num_measurements " + str(num_measurements_available))
                    break
                # after each iteration, if no data has been found, sleep for 1/10 the sample period then try again.
                sleep(sample_period/10)   
                x+=1
            num_measurements_list.append(num_measurements_available)
    
    return num_measurements_list  

def number_measurements_available_multipt(sample_period, num_msrmnts):
    """ Return a list of how many analog sensor measurements are availabe for each active channel.
    """

    num_measurements_list = []

    sleep(sample_period * num_msrmnts)
    
    for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
        for channel in device_enabled_chs:
            x = 0 
            # Perform a total of 30 iterations (3x the sample period), waiting for data.
            while x < 30: 
                num_measurements_available = ngio_read.get_num_measurements_available(hDevice, channel)  
                if num_measurements_available >= num_msrmnts: 
                    config.logger.debug("ch = " + str(channel) + " num_measurements " + str(num_measurements_available))
                    break
                # after each iteration, if no data has been found, sleep for 1/10 the sample period then try again.
                sleep(sample_period/10)   
                x+=1
            num_measurements_list.append(num_measurements_available)
    
    return num_measurements_list 


def read_and_calibrate_data(max_num_measurements_available):
    """ For each active analog channel, get the raw measurement (this may be a single value or multiple
    if sampling fast), convert to a voltage, and then apply the calibration to convert to 
    proper sensor units. One value for each sensor is returned with any extra values sent to the buffer.
    """

    measurements = []
    calibrated_values = []

    for hDevice, device_enabled_chs, device_probe_types, device_calibrations in zip(
            config.hDevice, config.enabled_analog_channels, config.probe_type_list, config.sensor_cal_list):
        
        for channel, probe_type, calibration_values in zip(
                device_enabled_chs, device_probe_types, device_calibrations):
            # get the raw measurement(s) from the channel. There may be one value or many values
            num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
                    hDevice, channel, max_num_measurements_available) 
        
            for value in values:
                config.logger.debug("raw value to convert to voltage = " + str(value))
                voltage = ngio_read.convert_to_voltage(hDevice, channel, value, probe_type)
                config.logger.debug("voltage = " + str(voltage))
                calibrated_value = apply_calibration(calibration_values, voltage)
                calibrated_values.append(calibrated_value)
                
            # The calibrated_values list may be one value, or multiple (if fast sampling)
            # Pull the first value off the calibrated_values list
            pop_values = calibrated_values.pop(0)
            # Build a list of each channel's first value (this builds the return list)
            measurements.append(pop_values)
            # If, after popping off the first value, there are still data, put them in the buffer
            if calibrated_values:
                config.buffer.append(calibrated_values)
            # clear the calibrated_values list for the next channel
            calibrated_values = []    

    return measurements

def read_and_calibrate_multi_pt_data(max_num_measurements_available):
    """ For each active channel, get the raw measurements, convert to voltage, and then 
    apply the calibration to convert to proper sensor units. The number of data points
    asked for are returned.
    """

    measurements = []
    calibrated_values = []

    for hDevice, device_enabled_chs, device_probe_types, device_calibrations in zip(
            config.hDevice, config.enabled_analog_channels, config.probe_type_list, config.sensor_cal_list):
        
        for channel, probe_type, calibration_values in zip(
                device_enabled_chs, device_probe_types, device_calibrations):
            # get the raw measurement(s) from the channel. There may be one value or many values
            num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
                    hDevice, channel, max_num_measurements_available) 
        
            for value in values:
                config.logger.debug("raw value to convert to voltage = " + str(value))
                voltage = ngio_read.convert_to_voltage(hDevice, channel, value, probe_type)
                config.logger.debug("voltage = " + str(voltage))
                calibrated_value = apply_calibration(calibration_values, voltage)
                calibrated_values.append(calibrated_value)
                
            measurements.append(calibrated_values)
            # clear the calibrated_values list for the next channel
            calibrated_values = []    

    return measurements

def apply_calibration(calibration_values, voltage):
    """ Use the equation and calibration values (stored in the sensor_cal_list) to convert the
    sensor's reading in voltage to proper sensor units.
    """

    # pull out each sensor's calibration information. This is a dictionary with values of
    # {"equation":, "cal0":, "cal1":, "cal2":, "units":}
    equation = calibration_values["equation"]
    config.logger.debug("calibration equation = " + str(equation))
    K0 = calibration_values["cal0"]
    K1 = calibration_values["cal1"]
    K2 = calibration_values["cal2"]
    active_calpage = calibration_values["active_calpage"]
    # an equation of 1 signifies a linear calibration:
    if equation == 1:
        calibrated_value = voltage*K1 + K0
    # equation 2 is a quadratic used for wide range temp probe:  
    elif equation == 2:
        calibrated_value = K0 + (K1*voltage) + K2*(voltage**2)
    # equation 3 is a power function used by the ethanol sensor:
    elif equation == 3:
        calibrated_value = (voltage**K1)*K0
    # equation 4: ISE sensors are calibrated using a modified power 
    # relationship between the voltage level and the displayed values.
    elif equation == 4:
        calibrated_value = K0*K1**voltage
    # equation 5: Logarithmic. The Colorimeter uses this equation.
    elif equation == 5:
        calibrated_value = K0+K1*(math.log(voltage))
    # equation 12: Steinhart-Hart equation for temp sensors
    elif equation == 12:
        if voltage == 0:
            calibrated_value = float('NaN')
        else:
            R = 15000/(5/voltage-1)
            T = 1/(K0+(K1*math.log(R))+(K2*math.log(R)*math.log(R)*math.log(R)))-273.15
            if active_calpage == 0:    # Celsius
                calibrated_value = T
            elif active_calpage == 1:    # Fahrenheit
                calibrated_value = T*1.8 + 32
            else:
                calibrated_value = T + 273    # Kelvin
    
    return calibrated_value 


def get_motion_measurements():
    """
    The motion detector requires two timing values to compute distance. Get the two 
    values and convert to distance.
    """

    num_measurements_needed = 2
    num_measurements_available = number_measurements_available_digital(config.sample_period, num_measurements_needed)
    config.logger.debug("num msrmnts available = " + str(num_measurements_available))
    if not any(num_measurements_available):
        config.logger.debug("Timed Out - no motion measurements available to read")
        return 
    else:
        max_num_measurements_available = max(num_measurements_available)

    # Get the measurements list. The list contains one value for each channel
    #distance_measurements = self.read_and_calibrate_motion_data(max_num_measurements_available)
    distance_measurements = read_and_calibrate_motion_data(max_num_measurements_available)
    
    return distance_measurements

def get_rotary_measurements():
    """
    Get a single rotary measurement. If more than one is returned it will be stored in the
    buffer to be accessed with the next read.
    """

    # Are there data in the buffer? If so, read the buffer, not the sensor
    if config.rotary_buffer:
        config.logger.debug("data in the buffer = " + str(config.buffer))
        measurements = pull_value_from_rotary_buffer()
        return measurements     

    # The buffer is empty, so first check that there are measurements available
    config.rotary_buffer = [] 
    
    num_measurements_needed = 1
    num_measurements_available = number_measurements_available_digital(config.sample_period, num_measurements_needed)
    if not any(num_measurements_available):
        config.logger.debug("Timed Out - no rotary measurements available to read")
        measurements = []
    else:
        max_num_measurements_available = max(num_measurements_available)
        # Get the measurements list. The list contains one value for each channel in 
        # proper sensor units. Excess data are placed in the buffer.
        measurements = read_rotary_data(max_num_measurements_available)
    
    return measurements

def get_photogate_measurements():
    """ This is simple counting values (timing values are a separate function - see the
    'labquest_photogate_timing.py' file for more info on timing). 
    Counting is similar to regular analog sensors in that a single count value is returned at a 
    requested sampling period. 
    """
    
    num_measurements_needed = 1
    num_measurements_available = number_measurements_available_digital(config.sample_period, num_measurements_needed)
    if not any(num_measurements_available):
        config.logger.debug("Timed Out - no photogate measurements available to read")
        measurements = []
    else:
        max_num_measurements_available = max(num_measurements_available)
        measurements, timing_values = read_photogate_data(max_num_measurements_available)
    
    return measurements

def number_measurements_available_digital(sample_period, num_msrmnts_needed):
    """ Return a list of how many measurements are availabe for each active channel.
    """

    num_measurements_list = []

    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            if key == "dig1":
                dig_channel = 5
            elif key == 'dig2':
                dig_channel = 6
            else:
                break
            
            if dig_ch_dictionary[key] in ('motion', 'photogate_count', 'photogate_timing', 
                                           'rotary_motion', 'rotary_motion_high_res'):
                x = 0 
                # Perform a total of 30 iterations (3x the sample period), waiting for data. The only exception
                # is photogate timing. In this case, there is no sample period. Instead, 1/3 the 'timeout' is used
                # as the sample period.
                while x < 30:
                    num_measurements_available = ngio_read.get_num_measurements_available(hDevice, dig_channel)  
                    config.logger.debug("num msrmnts available = " + str(num_measurements_available))
                    # motion needs 2 samples, photogate timing is determined by the user, the others need 1
                    if num_measurements_available >= num_msrmnts_needed: 
                        break
                    # after each iteration, if no data has been found, sleep for 1/10 the sample period then try again.
                    sleep(sample_period/10)   

                    x+=1
                num_measurements_list.append(num_measurements_available)
    
    return num_measurements_list
     

def read_and_calibrate_motion_data(max_num_measurements_available):
    """ For each active channel, get two timing values. Use these 2 timestamps
    to calculate distance. Unlike analog data collection, there is no buffer for storing
    extra values. This should not be an issue because motion detector requires slower 
    sampling. 
    """

    distance_values = []

    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            if key == "dig1":
                dig_channel = 5
            elif key == 'dig2':
                dig_channel = 6
            else:
                break
            
            if dig_ch_dictionary[key] == 'motion':

                # get the raw measurement(s) from the channel. There may be one value or many values
                num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
                    hDevice, dig_channel, max_num_measurements_available) 
                for value, time_stamp in zip(values, time_stamps):
                    if value == 0:
                        time1 = time_stamp
                    elif value == 1:
                        time2 = time_stamp
                        
                # calculate distance from microseconds: 
                # time/1000 = time for one way trip in ms
                # distance = v * time = 0.343 m/ms * t (this assumes 20 degrees C)
                t = (time2-time1)/1000
                v = 340/1000
                # The total distance is round trip (out and back). 
                # Divide by 2 to get distance from object to motion detector. 
                distance = v*t/2
                distance_cm = distance*100  
                
                distance_values.append(distance_cm)

    return distance_values

def read_rotary_data(max_num_measurements_available):
    """ For each active channel, get angle measurements (this may be a single value or multiple
    if sampling fast). One value for each sensor is returned with any extra values sent to the buffer.
    """

    angle_values = []
    rotary_values = []

    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            if key == "dig1":
                dig_channel = 5
            elif key == 'dig2':
                dig_channel = 6
            else:
                break
            
            if dig_ch_dictionary[key] in ('rotary_motion', 'rotary_motion_high_res'):

                num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
                    hDevice, dig_channel, max_num_measurements_available) 
                
                # The calibrated_values list may be one value, or multiple (if fast sampling)
                # Pull the first value off the calibrated_values list
                for value in values:
                    if dig_ch_dictionary[key] == 'rotary_motion':
                        rotary_value = value
                    else:    # this would then be the rotary_motion_high_res case
                        rotary_value = value/4
                    rotary_values.append(rotary_value)

                pop_values = rotary_values.pop(0)
                # Build a list of each channel's first value (this builds the return list)
                angle_values.append(pop_values)
                # If, after popping off the first value, there are still data, put them in the buffer
                if rotary_values:
                    config.rotary_buffer.append(rotary_values)
                # clear the rotary_values list for the next channel
                rotary_values = []   

    return angle_values

def read_photogate_data(max_num_measurements_available):
    """ For each active channel, get the count value and timestamp measurement.
    """

    count_values = []
    timing_values = []

    for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
        for key in dig_ch_dictionary:
            if key == "dig1":
                dig_channel = 5
            elif key == 'dig2':
                dig_channel = 6
            else:
                break
            
            if dig_ch_dictionary[key] in  ('photogate_count', 'photogate_timing'):

                num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
                    hDevice, dig_channel, max_num_measurements_available) 
        
                for value in values:
                    photogate_value = value
                count_values.append(photogate_value)

                for time in time_stamps:
                    timing_values.append(time) 

    return count_values, timing_values


def clear_the_lq_measurement_buffer():
    """ This function empties the measurement buffers. This should happen once measurements have been
    stopped, and before starting measurements again. 
    """
    
    sleep(1)    # wait a second and then read the ngio buffer to clear it

    if any(config.enabled_analog_channels):
        for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
            for channel in device_enabled_chs:
                num_measurements_available = ngio_read.get_num_measurements_available(hDevice, channel)  
                if num_measurements_available >= 1: 
                    num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
                            hDevice, channel, num_measurements_available)    

    
    if config.motion or config.rotary_motion or config.rotary_motion_high_res:
        for hDevice, dig_ch_dictionary in zip(config.hDevice, config.device_dig_channel_dictionary):
            for key in dig_ch_dictionary:
                if key == "dig1":
                    dig_channel = 5
                elif key == 'dig2':
                    dig_channel = 6
                else:
                    break
                
                if dig_ch_dictionary[key] in ('motion', 'rotary_motion', 'rotary_motion_high_res'):
                    num_measurements_available = ngio_read.get_num_measurements_available(hDevice, dig_channel)
                    if num_measurements_available >= 1:
                        num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
                            hDevice, dig_channel, num_measurements_available) 