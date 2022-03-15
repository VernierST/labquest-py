from ctypes import *

from labquest import config


def get_num_measurements_available(hDevice, channel):
    """
    Return:	number of measurements currently stored in the NGIO Measurement Buffer for the specified channel.
    """
    
    # Get a pointer to the GetNumMeasurementsAvailable function
    p_get_num_measurements_available = config.dll.NGIO_Device_GetNumMeasurementsAvailable
    # Configure the GetNumMeasurementsAvailable arguments
    p_get_num_measurements_available.argtypes = [c_ssize_t, c_byte]
    # Set the GetNumMeasurementsAvailable function return type
    p_get_num_measurements_available.restype = c_int32
    # Set parameters
    channel = c_byte(channel) # Analog 1 = 1
    # Call the GetNumMeasurementsAvailable function in the DLL
    max_count = p_get_num_measurements_available(hDevice, channel)
    # Check the GetNumMeasurementsAvailable return value. Looking for a value >= 1 
    return max_count

def read_raw_measurements(hDevice, channel, max_count):
    """
    Retrieve measurements from the NGIO Measurement Buffer for a specified channel. The measurements reported
	by this routine are removed from the NGIO Measurement Buffer. This routine
	returns immediately, so the return value may be less than maxCount.
    """
    # Get a pointer to ReadRawMeasurements
    p_read_raw_measurements = config.dll.NGIO_Device_ReadRawMeasurements
    # Configure the ReadRawMeasurements arguments
    p_read_raw_measurements.argtypes = [c_ssize_t, c_byte, POINTER(c_int32), POINTER(c_ssize_t), c_uint32]
    # Set the ReadRawMeasurements return type
    p_read_raw_measurements.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_measurements_buf = (c_int32 *max_count)(0) #this value comes from GetNumMeasurementsAvailable
    p_time_stamp = (c_ssize_t *max_count)(0) #this value comes from GetNumMeasurementsAvailable
    max_count = c_uint32(max_count)
    # Call ReadRawMeasurements in the DLL
    read_raw_measurements_return = p_read_raw_measurements(hDevice, channel, p_measurements_buf, p_time_stamp, max_count)

    # note the p_measurements_buf and p_time_stamp are array objects, not the values.
    # iterate these in the labquest code with for loop (for value in values) to convert from object to value
    return read_raw_measurements_return, p_measurements_buf, p_time_stamp
    
    

def convert_to_voltage(hDevice, channel, value, probe_type):
    """
    This routine converts a raw measurement obtained from NGIO_Device_GetLatestRawMeasurement() or 
	NGIO_Device_ReadRawMeasurements() into a voltage value. The range of possible output voltages
	is generally implied by the probeType.
	
	Return:		volts
    """
    # Get a pointer to ConvertToVoltage
    p_convert_to_voltage = config.dll.NGIO_Device_ConvertToVoltage
    # Configure the ConvertToVoltage arguments
    p_convert_to_voltage.argtypes = [c_ssize_t, c_byte, c_int32, c_int32]
    # Set the ConvertToVoltage return type
    p_convert_to_voltage.restype = c_float
    # Set parameters
    channel = c_byte(channel) # Analog 1 = 1
    raw_measurement = c_int32(value) # this is the value from ReadRawMeasurements
    probe_type = c_int32(probe_type) #this should come from probe info - operation type. Analog 5V = 2, 10V = 3
    # Call ConvertToVoltage in the DLL
    convert_to_voltage_return = p_convert_to_voltage(hDevice, channel, raw_measurement, probe_type)
    # Check the ConvertToVoltage return value. No error returned from this call
    return convert_to_voltage_return