from labquest import config
from labquest import labquest_read_functions as read
from labquest import ngio_read_functions as ngio_read


def get_photogate_timing(ch, samples, timeout, device_index):
    """  When the number of photogate samples asked for are available, read the data.
    Note that there may be a maximum number of samples that can be asked for.
    """

    timing_values = []

    if ch == 'dig1':
            channel = 5
    if ch == 'dig2':
            channel = 6
    # use the timeout as the sample_period in this instance
    sample_period = timeout
    num_measurements_needed = samples
     
    num_measurements_available = read.number_measurements_available(
            sample_period, device_index, channel, num_measurements_needed)
    
    if num_measurements_available == 0:
        config.logger.debug("Timed Out - no photogate measurements available to read")
    else:
        #count, timing = read.read_photogate_data(num_measurements_available)
        timing = read_photogate_timing(num_measurements_available, device_index, channel)
        timing_values = convert_to_semi_period(timing)
    
    return timing_values

def read_photogate_timing(num_measurements_available, device_index, channel):
    """ For each active channel, get the timestamp measurements.
    """

    timing_values = []
    hDevice = config.hDevice[device_index]

    num_of_measurements, values, time_stamps = ngio_read.read_raw_measurements(
        hDevice, channel, num_measurements_available) 

    for time in time_stamps:
        timing_values.append(time) 

    return timing_values

def convert_to_semi_period(timing_list):
    """ Convert from absolute time to incremental time (time between readings). This
    provides the time blocked, the time unblocked, the time blocked, unblocked, etc..
    """
    
    timing_values = []
    # remove the first value, it is not used
    timing_list.pop(0)

    i = 0
    while i < len(timing_list)-1:
        value = (timing_list[i +1] - timing_list[i])/1000000
        timing_values.append(value)

        i += 1

    return timing_values

    
