

# Variables passed between the functions.

logger = None # global logging instance for this module

buffer = []    # buffer - a 2D list to store the excess data from a sensor when multi-points are collected
rotary_buffer = []
dll = None    # The NGIO library
hLib = None    # Library handle
#hDeviceList = None    # Handle to the device list snapshot
hDevice = []    # 1D list of Device Handles of the connected devices
device_type = None    # Original LQ, LQ Mini, LQ2, LQStream, or LQ3
#number_found_devices = None
#device_name = None
enabled_analog_channels = []   # 2D list of each device's active channels (sensors connected)
enabled_dig_channels = []    # 2d list of each device's active dig channels
enabled_all_channels = []    # 2D list of both analog and dig active channels
motion = False     # is a motion detector configured?
photogate = False    # is a photogate configured?
photogate_timing = False
rotary_motion = False    # is a rotary motion configured?
rotary_motion_high_res = False    # is a rotary motion (high res) configured?
dcu = False   # is a dcu configured?
dcu_pwm = False
sample_period = None
op_type_list = []    # 2D list of each sensor's op_type. This value is used in the read function
probe_type_list = []
sensor_cal_list = []    # 2D list of each sensor's calibration and equation info. Used in the read function
                        # {"equation":cal_eq, "cal0":active_cal0, "cal1":active_cal1, "cal2":active_cal2,
                            #   "units":active_units, "active_calpage":active_calpage}
device_dig_channel_dictionary = []    # 1D list of each devices dig channel info
device_channel_dictionary = []    # 1D list of each devices channel info. The channel info is a 2D library
                                    # each device will have info of each active channel. For example, dev0 has ch1,ch2 info
                                    # and dev1 has ch1 info. Index out the library for the device, and return the library attributes
                                    # [{ch1:{name:name, units:units}, ch2:{name:name, units:units}}, {ch1:{name:name, units:units}}]
                                    # Get the name of the sensor in ch1 of dev0 = (device_channel_dictionary[0]["ch1"]["name"])