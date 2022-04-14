from ctypes import *

from labquest import config    # get the dll object from the config.py file


def set_measurement_period(hDevice, channel, period):
    """
    Set the measurement period to a specified number of seconds. The device will report measurements
    to the host computer at the measurement period interval once measurements have been started if the
    sampling mode for a channel is periodic. These measurements are held in the NGIO Measurement 
    Buffer allocated for each channel. 

    If all channels are sampled at the same rate, call NGIO_Device_SetMeasurementPeriod(channel = -1).
    """
    # Get a pointer to the SetMeasurementPeriod function
    p_set_measurement_period = config.dll.NGIO_Device_SetMeasurementPeriod
    # Configure the SetMeasurementPeriod arguments
    p_set_measurement_period.argtypes = [c_ssize_t, c_byte, c_double, c_uint32]
    # Set the SetMeasurementPeriod function return type
    p_set_measurement_period.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    desired_period = c_double(period)
    set_period_timeout_ms = c_uint32(2000)
    # Call the SetMeasurementPeriod function in the DLL
    set_measurement_period_return = p_set_measurement_period(hDevice, channel, desired_period, set_period_timeout_ms)
    # Check the SetMeasurementPeriod return value. Return: 0 if successful, else -1!
    if set_measurement_period_return == -1:
        config.logger.debug("ERROR calling SetMeasurementPeriod")

def get_measurement_period(hDevice, channel):
    """
    Get the measurement period
    """
    # Get a pointer to the GetMeasurementPeriod function
    p_get_measurement_period = config.dll.NGIO_Device_GetMeasurementPeriod
    # Configure the GetMeasurementPeriod arguments
    p_get_measurement_period.argtypes = [c_ssize_t, c_byte, POINTER(c_double), c_uint32]
    # Set the GetMeasurementPeriod function return type
    p_get_measurement_period.restype = c_int32
    # Set parameters
    channel = c_byte(channel) # use channel = -1
    p_period = c_double(0)
    set_period_timeout_ms = c_uint32(2000)
    # Call the GetMeasurementPeriod function in the DLL
    get_measurement_period_return = p_get_measurement_period(hDevice, channel, p_period, set_period_timeout_ms)
    # Check the GetMeasurementPeriod return value. Return: 0 if successful, else -1!
    if get_measurement_period_return == -1:
        config.logger.debug("ERROR calling GetMeasurementPeriod")
    return str(p_period.value)

