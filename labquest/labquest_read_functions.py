from time import sleep
import math

from labquest import config
from labquest import ngio_read_functions as ngio_read
from labquest import ngio_sensor_functions as ngio_sensor
from labquest import labquest_buffer_functions as buffer
buf = buffer.lq_buffer()

def get_measurement(device_index, ch):
    """ Get measurement from the specified channel (analog and digital)
    """

    if ch == 'ch1':
            channel = 1
    if ch == 'ch2':
            channel = 2
    if ch == 'ch3':
            channel = 3
    if ch == 'dig1':
            channel = 5
    if ch == 'dig2':
            channel = 6
    
    if ch in ('ch1', 'ch2', 'ch3'):
        analog_measurement = get_analog_measurement(device_index, channel)
        return analog_measurement

    if ch in ('dig1', 'dig2'):
        dig_measurement = get_digital_measurement(device_index, ch, channel)
        return dig_measurement

def get_analog_measurement(device_index, ch):
    """ Get a single analog sensor measurement. This may be from the buffer, or as a new reading.
    """
    
    # Are there data in the buffer? If so, read the buffer, not the sensor
    buffer_is_empty = buf.buffer_is_empty(device_index, ch)
    if not buffer_is_empty:
        measurement = buf.buffer_get(device_index, ch)
        return measurement 

    # The buffer is empty, so get data
    num_measurements_available = number_measurements_available(config.sample_period, device_index, ch)
    config.logger.debug("number of measurements available " +str(ch) +": " +str(num_measurements_available))
    if num_measurements_available == 0:
        config.logger.debug("Timed Out - no measurements available to read")
        measurement = None
    else:
        measurement = read_and_calibrate_data(num_measurements_available, device_index, ch)
    
    return measurement

def get_digital_measurement(device_index, ch, channel):
    """ Get a single digital sensor measurement. This may be from the buffer, or as a new reading.
    """

    # Are there data in the buffer? If so, read the buffer, not the sensor
    buffer_is_empty = buf.buffer_is_empty(device_index, channel)
    if not buffer_is_empty:
        measurement = buf.buffer_get(device_index, channel)
        return measurement 

    # The buffer is empty, so get data. First get the key:value, such as 'motion', 'rotary_motion', etc..
    dig_ch_dictionary = config.device_dig_channel_dictionary[device_index]
    for key in dig_ch_dictionary:  
        if key == ch:
            key_value = dig_ch_dictionary[key]
            if key_value == 'motion':
                num_measurements_needed = 2
            else:
                num_measurements_needed =1
    # make sure there are data available
    num_measurements_available = number_measurements_available(
        config.sample_period, device_index, channel, num_measurements_needed)
    config.logger.debug("number of measurements available ch" +str(channel) +": " +str(num_measurements_available))
    # data (for some reason) is not available
    if num_measurements_available == 0:
        config.logger.debug("Timed Out - no measurements available to read")
        measurement = None
    # there are data. Read and calibrate
    else:
        measurement = read_and_calibrate_digital_data(num_measurements_available, device_index, channel, key_value)
    
    return measurement

def get_multi_pt_measurements(device_index, ch, num_measurements_to_read):
    """ Get a packet of analog sensor measurements from the specified channel.
    """

    if ch == 'ch1':
            channel = 1
    if ch == 'ch2':
            channel = 2
    if ch == 'ch3':
            channel = 3

    # make sure there is at least one available, then ask to read all measurements
    num_measurements_available = number_measurements_available_multipt(
            config.sample_period, device_index, channel, num_measurements_to_read)
    config.logger.debug("multi-pt num msrmnts available = " + str(num_measurements_available))
    if num_measurements_available == 0:
        config.logger.debug("Timed Out - no measurements available to read")
        measurements = []
    else:
        measurements = read_and_calibrate_multi_pt_data(device_index, channel, num_measurements_to_read)

    return measurements

def number_measurements_available(sample_period, device_index, channel, num_msrmnts_needed=1):
    """ Return a value for how many analog sensor measurements are availabe for the channel.
    """
    
    hDevice = config.hDevice[device_index]

    x = 0 
    # Perform a total of 30 iterations (3x the sample period), waiting for data.
    while x < 30: 
        num_measurements_available = ngio_read.get_num_measurements_available(hDevice, channel)  
        if num_measurements_available >= num_msrmnts_needed: 
            break
        # after each iteration, if no data has been found, sleep for 1/10 the sample period then try again.
        sleep(sample_period/10)   
        x+=1
    
    return num_measurements_available  

def number_measurements_available_multipt(sample_period, device_index, channel, num_msrmnts):
    """ Return a value of how many analog sensor measurements are availabe for the channel.
    """

    hDevice = config.hDevice[device_index]

    sleep(sample_period * num_msrmnts)
    
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
            
    return num_measurements_available

def read_and_calibrate_data(num_measurements_available, device_index, channel):
    """ For the analog channel, get the raw measurement (this may be a single value or multiple
    if sampling fast), convert to a voltage, and then apply the calibration to convert to 
    proper sensor units. One value is returned with any extra values sent to the buffer.
    """

    calibrated_values = []
    hDevice = config.hDevice[device_index]

    # get the raw measurement(s) from the channel. There may be one value or many values
    num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
            hDevice, channel, num_measurements_available) 

    for value in values:
        config.logger.debug("raw value to convert to voltage = " + str(value))
        op_type = ngio_sensor.ddsmem_get_operation_type(hDevice, channel)
        if op_type == 2: 
            probe_type = 3   # an op_type = 2 (10V) means probe type = 3 (10 V)
        else:
            probe_type = 2   # an op_type = 14 (5V) means probe type = 2 (5 V) 
        voltage = ngio_read.convert_to_voltage(hDevice, channel, value, probe_type)
        config.logger.debug("voltage = " + str(voltage))
        calibrated_value = apply_calibration(voltage, hDevice, channel)
        calibrated_values.append(calibrated_value)
        
    # The calibrated_values list may be one value, or multiple (if fast sampling)
    # Pull the first value off the calibrated_values list
    measurement = calibrated_values.pop(0)
    # If, after popping off the first value, there are still data, put them in the buffer
    if calibrated_values:
        config.logger.info("values to put in buffer, " + str(calibrated_values))
        buf.buffer_put(device_index, channel, calibrated_values)

    return measurement

def read_and_calibrate_digital_data(num_measurements_available, device_index, channel, key_value):
    """ Get the raw value from the digital channel and calibrate based on what sensor is connected.
    """

    calibrated_values = []
    hDevice = config.hDevice[device_index]

    # get the raw measurement(s) from the channel. There may be one value or many values
    num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
            hDevice, channel, num_measurements_available) 

    if key_value == 'motion':
        i = 0
        if i < len(values):
            for value, time_stamp in zip(values, time_stamps):
                config.logger.debug("motion value, timestamp = " + str(value) +', ' +str(time_stamp))
                if value == 0:
                    time1 = time_stamp
                elif value == 1:
                    time2 = time_stamp 
            i += 2     
            # calculate distance from microseconds: time/1000 = time for one way trip in ms
            # distance = v * time = 0.343 m/ms * t (this assumes 20 degrees C)
            t = (time2-time1)/1000
            v = 340/1000
            # The total distance is round trip (out and back). 
            # Divide by 2 to get distance from object to motion detector. 
            calibrated_value = v*t/2    # distance in meters
            calibrated_values.append(calibrated_value)

    if key_value == 'rotary_motion':
        for value in values:
            config.logger.debug("rotary value = " + str(value))
            calibrated_value = value
            calibrated_values.append(calibrated_value)

    if key_value == 'rotary_motion_high_res':
        for value in values:
            config.logger.debug("rotary value = " + str(value))
            calibrated_value = value/4
            calibrated_values.append(calibrated_value)

    if key_value == 'photogate_count':
        for value in values:
            config.logger.debug("photogate count value = " + str(value))
            calibrated_value = value
            calibrated_values.append(calibrated_value)

    # The calibrated_values list may be one value, or multiple (if fast sampling)
    # Pull the first value off the calibrated_values list
    measurement = calibrated_values.pop(0)
    # If, after popping off the first value, there are still data, put them in the buffer
    if calibrated_values:
        buf.buffer_put(device_index, channel, calibrated_values)

    return measurement

def read_and_calibrate_multi_pt_data(device_index, channel, num_measurements):
    """ Get the raw measurements, convert to voltage, and then 
    apply the calibration to convert to proper sensor units. The number of data points
    asked for are returned.
    """

    calibrated_values = []
    hDevice = config.hDevice[device_index]
        
    # get the raw measurement(s) from the channel. There may be one value or many values
    num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
            hDevice, channel, num_measurements) 

    for value in values:
        config.logger.debug("raw value to convert to voltage = " + str(value))
        op_type = ngio_sensor.ddsmem_get_operation_type(hDevice, channel)
        if op_type == 2: 
            probe_type = 3   # an op_type = 2 (10V) means probe type = 3 (10 V)
        else:
            probe_type = 2   # an op_type = 14 (5V) means probe type = 2 (5 V) 
        voltage = ngio_read.convert_to_voltage(hDevice, channel, value, probe_type)
        config.logger.debug("voltage = " + str(voltage))
        calibrated_value = apply_calibration(voltage, hDevice, channel)
        calibrated_values.append(calibrated_value)    

    return calibrated_values

def apply_calibration(voltage, hDevice, channel):
    """ Use the equation and calibration values to convert the
    sensor's reading in voltage to proper sensor units.
    """

    # pull out each sensor's calibration information. This is a dictionary with values of
    # {"equation":, "cal0":, "cal1":, "cal2":, "units":}

    equation = ngio_sensor.ddsmem_get_calibration_equation(hDevice, channel)
    config.logger.debug("calibration equation ch" +str(channel) +": " + str(equation))
    active_calpage = ngio_sensor.ddsmem_get_active_cal_page(hDevice, channel)
    K0, K1, K2, active_units = ngio_sensor.ddsmem_get_cal_page(
            hDevice, channel, index=active_calpage)

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