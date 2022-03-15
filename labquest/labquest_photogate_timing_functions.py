from labquest import config
from labquest import labquest_read_functions as read


def get_photogate_timing(samples, timeout):
    """  When the number of photogate samples asked for are available, read the data.
    Note that there may be a maximum number of samples that can be asked for.
    """

    timing_values = []
     # use the timeout as the sample_period in this instance
     
    # readings because the first is not used and the times require 2 readings that are subtracted.
    num_measurements_available = read.number_measurements_available_digital(timeout, samples)
    if not any(num_measurements_available):
        config.logger.debug("Timed Out - no photogate measurements available to read")
    else:
        max_num_measurements_available = max(num_measurements_available)
        
        count, timing = read.read_photogate_data(max_num_measurements_available)
        timing_values = convert_to_semi_period(timing)
    
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

    
