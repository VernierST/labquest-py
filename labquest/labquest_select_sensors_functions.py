import os
from struct import *   # use 'unpack' for sensor_id

from labquest import config
from labquest import ngio_sensor_functions as ngio_sensor
from labquest import ngio_send_cmd_get_resp as ngio_send


def configure_channels_and_sensors(*args):
    """
    Use the *args information to create various lists of what sensors are active. These lists are 
    used in the rest of the program to determine what channels to start, read, etc... If the user did
    not input *args, a prompt will take them through each channel to configure.
    """
    
    # Check the analog channels for Labquest Auto-ID sensors. 
    config.enabled_analog_channels = get_list_of_device_enabled_analog_channels()  
    if any(config.enabled_analog_channels):
        read_sensor_dds_memory()
                
    # If there are no *args, provide an input prompt for the user to select sensors
    if not args: 
        config.enabled_analog_channels = custom_analog_ch_setup()
        config.enabled_dig_channels, config.device_dig_channel_dictionary = custom_digital_ch_setup()

    # if the user has input *args (a dictionary), use that for configuring the channels
    else:
        config.enabled_analog_channels, config.enabled_dig_channels = configure_channels_using_dictionary(*args)
        config.device_dig_channel_dictionary = build_dig_channel_dictionary(*args)
         
    if any(config.enabled_dig_channels): 
        set_config_dig_chs_to_true_or_false()
        
    if any(config.enabled_analog_channels):
        # Build the device_channel_dictionary[{{}},{{}}] (this is different than the dict
        # used to configure the channels - this is just the sensor info in dict format)
        config.device_channel_dictionary = build_channel_dictionary()

        # Build the operation_type list
        config.op_type_list, config.probe_type_list = get_sensor_operation_type_list()

        # Build the list containing the calibration equation and calibration values
        config.sensor_cal_list = get_sensor_calibration_values()
    
    config.enabled_all_channels = []
    i = 0
    while i < len(config.hDevice):
        all_chs = []
        if any(config.enabled_analog_channels):
            all_chs.extend(config.enabled_analog_channels[i])
        if any(config.enabled_dig_channels):
            all_chs.extend(config.enabled_dig_channels[i])
        #config.enabled_all_channels = config.enabled_analog_channels[i] + config.enabled_dig_channels[i]
        config.enabled_all_channels.append(all_chs)

        channel_name_list = []
        if 1 in all_chs:
            channel_name_list.append('ch1')
        if 2 in all_chs:
            channel_name_list.append('ch2')
        if 3 in all_chs:
            channel_name_list.append('ch3')
        if 5 in all_chs:
            channel_name_list.append('dig1')
        if 6 in all_chs:
            channel_name_list.append('dig2')


        config.logger.debug("Device", i, "enabled channels: ", channel_name_list)
        i += 1

    return config.enabled_all_channels

    
def get_list_of_device_enabled_analog_channels():
    """ Return a 2D list of all channels that have LabQuest auto-id sensors connected (sensor id > 0)
    """
    enabled_channel_list = []

    for hDevice in config.hDevice:
        active_ch = []
        for channel in range (1,4):
            sensor_id = get_sensor_id(hDevice, channel)
            if sensor_id > 0:    # if the id > 0 then a sensor has been detected
                active_ch.append(channel)    
        enabled_channel_list.append(active_ch)
    
    return enabled_channel_list

def read_sensor_dds_memory():
    """For each enabled channel, read the sensor's dds memory (auto-id and resistor 
    id are done differently)
    """

    for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
        for channel in device_enabled_chs:
            sensor_id = get_sensor_id(hDevice, channel)
            #sensor_id = ngio_sensor.get_sensor_id(hDevice, channel)
            # if it is an Auto-id sensor, then auto-load the dds memory
            if sensor_id >= 20:
                ngio_sensor.ddsmem_read_record(hDevice, channel)
            # If it is a resistor-id sensor, then you have to manually load the dds memory
            elif sensor_id >0 and sensor_id <20:
                ddsmem_set_record(hDevice, channel, sensor_id)

def get_sensor_id(hDevice, channel):
    """ Each LabQuest sensor has a unique ID. Get that value
    """
    parameters = [0]*14
    command = 0x28   #GET_SENSOR_ID = 28
    parameters[0] = channel
    param_bytes = 1
    resp_buffer, resp_bytes = ngio_send.send_cmd_get_response(hDevice, command, parameters, param_bytes)
    
    # Convert the 4 byte structure of unsigned chars into a long. This results in a tuple, 
    # who's only value is the long
    bb = bytearray(resp_buffer)
    # note the "<l", this is the formatting, where < is for little endian, and l for long 
    sensor_id = unpack('<l', bb[0:4])
    
    return sensor_id[0]   # it's a tuple, the value is the first index of this tuple


def ddsmem_set_record(hDevice, channel, sensor_id):  
    """
    Some LabQuest sensors are resistor ID sensors. In this case, all of the sensor information is 
    stored in a text file. Read that text file to get the information, and then 'set' that info
    in NGIO ddsmem.
    """

    file_name = "resistorsensorlist.txt"
    file_folder = "labquest" + os.path.sep + "data"    # this text file lives in the "data" folder
    file_path = (os.path.dirname((os.path.dirname(__file__)))) + os.path.sep + file_folder + os.path.sep + file_name
    with open(file_path, 'r') as file:
        # The text file is made up of sensor info for multiple resistor id sensors
        file_content = file.readlines()
        file.close()
        # pull out the row from the text file corresponding to this resistor id sensor
        split_string = file_content[sensor_id-1]
        # turn the tab-delimited string into a list with all the restor id sensor info. Here is the info:
        # [ProductID,PrettyName,LongName,ShortName,OpType,TypRate,CalEq,NumCals,CalPage,Cal0K0,
        # Cal0K1,Cal0K2,Units0,Cal1K0,Cal1K1,Cal1K2,Units1,Cal2K0,Cal2K1,Cal2K2,Units2]
        resistor_sensor_info = split_string.split("\t")
        config.logger.debug("resistor sensor info = " + str(resistor_sensor_info))
    # Set the long name by indexing out the long name from the list
    long_name = resistor_sensor_info[2]
    ngio_sensor.ddsmem_set_long_name(hDevice, channel, long_name)
    short_name = resistor_sensor_info[3]
    ngio_sensor.ddsmem_set_short_name(hDevice, channel, short_name)
    op_type = int(resistor_sensor_info[4])
    ngio_sensor.ddsmem_set_operation_type(hDevice, channel, op_type)
    cal_equation = int(resistor_sensor_info[6])
    ngio_sensor.ddsmem_set_calibration_equation(hDevice, channel, cal_equation)
    highest_calpage_index = int(resistor_sensor_info[7])
    ngio_sensor.ddsmem_set_highest_valid_cal_page_index(hDevice, channel, highest_calpage_index)
    active_calpage_index = int(resistor_sensor_info[8])
    ngio_sensor.ddsmem_set_active_cal_page(hDevice, channel, active_calpage_index)  

    # Set the calpage (coeff a, b, c, and units for cal_index 0 are in columns 9,10,11 and 12)
    x = 0
    for cal_index in range (0, 3):
        coeff_a = float(resistor_sensor_info[9+x])
        coeff_b = float(resistor_sensor_info[10+x])
        coeff_c = float(resistor_sensor_info[11+x])
        units = (resistor_sensor_info[12+x])
        units = units.strip()    # the last units in the txt file have a /n that needs to be stripped
        ngio_sensor.ddsmem_set_cal_page(hDevice, channel, cal_index, coeff_a, 
                                    coeff_b, coeff_c, units )
        x += 4              


def custom_analog_ch_setup(): 
    """ This option provides the user with a way to configure a channel to read
    a non-Vernier sensor, or to read a LabQuest sensor's raw voltage. Returns an
    updated enabled channel list.
    """ 
        
    enabled_channel_list = []
    
    for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
        active_ch = []
        for channel in range(1,4):
            print("\n")
            print("Customize channel ", channel)

            # determine if this is a channel that has an auto-id sensor connected
            if channel in device_enabled_chs:
                max_index = ngio_sensor.ddsmem_get_highest_valid_cal_page_index(hDevice, channel)
                print("LabQuest sensor detected. Select a calibration page, or choose to read the sensor's raw voltage")
                
                for index in range(0, max_index + 1):
                    a,b,c,units = ngio_sensor.ddsmem_get_cal_page(hDevice, channel, index)
                    long_name = ngio_sensor.ddsmem_get_long_name(hDevice, channel)
                    #print(index, ":" "  cal", index, " = ", long_name, units, sep='')
                    print(index, ":" "  cal", index, " = ", long_name, units, sep='', end='\n')
                    #print(units)
                    if index == max_index:
                        print(index + 1, ":", "  raw_voltage = Potential(V)", sep='')
                        print('')

                if max_index == 0:
                    print("Enter 0 or 1:", end=' ')
                elif max_index == 1:
                    print("Enter 0, 1 or 2:", end=' ')
                else:
                    print("Enter 0, 1, 2 or 3:", end=' ')
                selected_calpage_index = int(input())
                
                # if the user selected the read Raw Voltage option
                if selected_calpage_index == max_index + 1:
                    set_channel_to_read_raw_voltage(hDevice, channel)
                # if the user selected one of the sensor's available calpages
                else:
                    ngio_sensor.ddsmem_set_active_cal_page(hDevice, channel, selected_calpage_index)
                active_ch.append(channel)
                
            # if this is a channel with no auto-id sensor connected
            else:
                print("No LabQuest sensor detected. If you want to connect and")
                print("read a non-LabQuest sensor on this channel select 'raw_voltage'")
                print("0:  no_sensor")
                print("1:  raw_voltage = Potential(V)")
                print('')
                print("Enter 0 or 1:", end=' ')
                custom_selection = int(input())
                if custom_selection == 1:
                    set_channel_to_read_raw_voltage(hDevice, channel)
                    active_ch.append(channel)
                else:
                    pass
        enabled_channel_list.append(active_ch)
    
    return enabled_channel_list 

def custom_digital_ch_setup(): 
    """ This option provides the user with a way to configure a digital channel to read
    a Vernier motion detector, photogate, rotary motion sensor, or dcu. Returns an
    updated enabled digital channel list.
    """ 
        
    enabled_dig_channel_list = []
    device_dig_channel_dictionary = []
    
    for hDevice in config.hDevice:
        active_dig_ch = []
        dig_ch_dictionary = {}
        dig_chs = ['no_sensor', 'motion', 'photogate_count', 'photogate_timing', 'rotary_motion', 
                    'rotary_motion_high_res', 'dcu', 'dcu_pwm']
        
        
        for channel in range(1,3):
            print("\n", "\n")
            print("Customize dig", channel)
            print("0: ", dig_chs[0])
            print("1: ", dig_chs[1])
            print("2: ", dig_chs[2])
            print("3: ", dig_chs[3])
            print("4: ", dig_chs[4])
            print("5: ", dig_chs[5])
            print("6: ", dig_chs[6])
            print("7: ", dig_chs[7])
            print("\n")
            print("Enter 0, 1, 2, 3, 4, 5, 6, or 7:", end=' ')
            custom_selection = int(input())

            if custom_selection in (1,2,3,4,5,6,7):
                active_dig_ch.append(channel+4)   # dig ch's are 5 and 6
                if channel == 1:
                    dig_ch_dictionary['dig1'] = (str(dig_chs[custom_selection]))
                else:
                    dig_ch_dictionary['dig2'] = (str(dig_chs[custom_selection]))
                device_dig_channel_dictionary.append(dig_ch_dictionary)

        enabled_dig_channel_list.append(active_dig_ch) 

    return enabled_dig_channel_list, device_dig_channel_dictionary
         

def set_channel_to_read_raw_voltage(hDevice, channel):
    """ Overwrite the ddsmem in order to make this channel read Raw Voltage (0-5V)
    """

    long_name = "Potential"
    ngio_sensor.ddsmem_set_long_name(hDevice, channel, long_name)
    short_name = "Pot"
    ngio_sensor.ddsmem_set_short_name(hDevice, channel, short_name)
    op_type = int(14)
    ngio_sensor.ddsmem_set_operation_type(hDevice, channel, op_type)
    cal_equation = int(1)
    ngio_sensor.ddsmem_set_calibration_equation(hDevice, channel, cal_equation)
    highest_calpage_index = int(0)
    ngio_sensor.ddsmem_set_highest_valid_cal_page_index(hDevice, channel, highest_calpage_index)
    active_calpage_index = int(0)
    ngio_sensor.ddsmem_set_active_cal_page(hDevice, channel, active_calpage_index) 
    # Set the calpage (coeff a, b, c, and units for cal_index 0 are in columns 9,10,11 and 12)
    coeff_a = float(0)
    coeff_b = float(1)
    coeff_c = float(0)
    units = ('(V)')
    cal_index = 0
    ngio_sensor.ddsmem_set_cal_page(hDevice, channel, cal_index, coeff_a, 
                                coeff_b, coeff_c, units ) 


def configure_channels_using_dictionary(*args):
    """  
    Create the 'enabled channel' lists for active analog and digital sensors based on the 
    *args values sent by the user.
    
    The key options are:
            'ch1', 'ch2', 'ch3', 'dig1', and 'dig2'
        The values for the 3 analog channels are:
            'default', 'cal0', 'cal1', 'cal2', 'raw_voltage'. 
        The dig channel values are:
            'motion', 'photogate', 'rotary_motion', 'rotary_motion_high_res', 'dcu', 'dcu_pwm. 
    """
    
    enabled_channel_list = []
    enabled_dig_ch_list = []
    # each argument is a dictionary of how to configure a device's channels. 
    # iterate through each device's dictionary
    i = 0
    for channel_setup in args:
        active_ch = []
        active_dig_ch = []
        # pull out each keyword, this will be the various channels (ch1, ch2, ch3, dig1, dig2)
        for key in channel_setup:

            if key in ('ch1', 'ch2', 'ch3'):

                if key == "ch1":
                    channel = 1
                elif key == "ch2":
                    channel = 2
                else:
                    channel = 3

                # now pull out each value of the key, the setup info (default, raw_voltage, etc..)
                
                # the raw_voltage setup does not require that an auto-id sensor was detected.
                if channel_setup[key] == 'raw_voltage':
                    config.logger.debug("channel to set to raw voltage = " + str(channel))
                    active_ch.append(channel)
                    set_channel_to_read_raw_voltage(config.hDevice[i], channel)
                # first check that an auto-id sensor was detected. If so allow default, cal0, etc..
                elif channel in config.enabled_analog_channels[i]:
                    active_ch.append(channel)                       
                    if channel_setup[key] == 'cal0':
                        config.logger.debug("channel to set to calpage 0 = " + str(channel))
                        ngio_sensor.ddsmem_set_active_cal_page(config.hDevice[i], channel, active_calpage=0)
                    elif channel_setup[key] == 'cal1':
                        config.logger.debug("channel to set to calpage 1 = " + str(channel))
                        ngio_sensor.ddsmem_set_active_cal_page(config.hDevice[i], channel, active_calpage=1)
                    elif channel_setup[key] == 'cal2':
                        config.logger.debug("channel to set to calpage 2 = " + str(channel))
                        ngio_sensor.ddsmem_set_active_cal_page(config.hDevice[i], channel, active_calpage=2) 
                    elif channel_setup[key] == 'default': 
                        config.logger.debug("channel for default calibration = " + str(channel))
                        pass    # do nothing because all auto-id sensors are configured already
                    else:
                        # this would be the case where they misspelled the value or used an invalid value
                        config.logger.warning("lq.select_sensors() dictionary argument has unrecognized value, 'default' will be used.")
        
                else:
                    config.logger.warning("Check the lq.select_sensors() argument. Either the dictionary value is not valid or the dictionary value is 'default', 'cal0', 'cal1', or 'cal2', but no Auto-ID sensor is detected on the specified channel")

            elif key in ('dig1', 'dig2'):

                if key == "dig1":
                    dig_ch = 5
                else:
                    dig_ch = 6
                active_dig_ch.append(dig_ch)

                # now pull out each value of the key, the setup info (motion, rotary_motion, etc.. )
                if channel_setup[key] in ('motion', 'photogate_count', 'photogate_timing', 
                                         'rotary_motion', 'rotary_motion_high_res', 'dcu', 'dcu_pwm'):
                    pass
                else:
                    config.logger.warning("dictionary value not valid") 

            else:
                config.logger.warning("dictionary key not valid")

        enabled_channel_list.append(active_ch) 
        enabled_dig_ch_list.append(active_dig_ch) 
        i += 1 

    return enabled_channel_list, enabled_dig_ch_list 

def build_dig_channel_dictionary(*args):
    """
    Create a dictionary that just has information on how the digital channels are configured.
    """

    if not any(config.enabled_dig_channels):
        device_dig_channel_dictionary = []
    else:
        device_dig_channel_dictionary = []
        for channel_setup in args:
            dig_ch_dictionary = {}
            # pull out each keyword, this will be the various channels (ch1, ch2, ch3, dig1, dig2)
            for key in channel_setup:
                if key == "dig1":
                    dig1_sensor = channel_setup[key]
                    dig_ch_dictionary['dig1'] = (str(dig1_sensor))
                if key == "dig2":
                    dig_ch_dictionary['dig2'] = str((channel_setup[key]))

            device_dig_channel_dictionary.append(dig_ch_dictionary)

    return device_dig_channel_dictionary

def set_config_dig_chs_to_true_or_false():
    """
    There is a config.py file that stores information about how the channels are configured.
    This information is used throughout the program. This function sets a True/False for 
    what digital devices are being used in the program.
    """
    
    for dig_dict in config.device_dig_channel_dictionary:

        if 'motion' in dig_dict.values():
            config.motion = True
        if 'photogate_count'in dig_dict.values():
            config.photogate = True
        if 'photogate_timing'in dig_dict.values():   # timing and count might need their own true/false
            config.photogate_timing = True
        if 'rotary_motion' in dig_dict.values():
            config.rotary_motion = True
        if 'rotary_motion_high_res' in dig_dict.values():
            config.rotary_motion_high_res = True
        if 'dcu'in dig_dict.values():
            config.dcu = True
        if 'dcu_pwm' in dig_dict.values():
            config.dcu_pwm = True

def build_channel_dictionary():
    """ 1D list of each devices analog channel info. The channel info is a 2D library
    For example
    [{ch1:{sensor info dictionary}, ch2:{sensor info dictionary}, ch3:{sensor info dictionary}}] 
    Get the name of the sensor in ch1 of dev0 = (device_channel_dictionary[0]["ch1"]["name"])
    """

    device_channel_dictionary = []

    for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
        # Each labquest device will have a dictionary for the 3 channels, each channel will have
        # a dictionary that contains sensor info
        ch1 = {}
        ch2 = {}
        ch3 = {}
        # start with an empty 2D dictionary called "channel_dictionary"
        channel_dictionary = {"ch1":ch1, "ch2":ch2, "ch3":ch3}
        # get the sensor info for each enabled channel
        for channel in device_enabled_chs:
            long = ngio_sensor.ddsmem_get_long_name(hDevice, channel)
            short = ngio_sensor.ddsmem_get_short_name(hDevice, channel)
            op_type = ngio_sensor.ddsmem_get_operation_type(hDevice, channel)
            cal_eq = ngio_sensor.ddsmem_get_calibration_equation(hDevice, channel)
            num_cal_indices = ngio_sensor.ddsmem_get_highest_valid_cal_page_index(hDevice, channel)
            active_calpage = ngio_sensor.ddsmem_get_active_cal_page(hDevice, channel)
            cal0k0, cal0k1, cal0k2, units0 = ngio_sensor.ddsmem_get_cal_page(hDevice, channel, index=0)
            cal1k0, cal1k1, cal1k2, units1 = ngio_sensor.ddsmem_get_cal_page(hDevice, channel, index=1)
            cal2k0, cal2k1, cal2k2, units2 = ngio_sensor.ddsmem_get_cal_page(hDevice, channel, index=2)

            # fill each enabled channel with the sensor info
            if channel ==1:
                channel_dictionary["ch1"] = {"long_name":long, "short_name":short, "op_type":op_type, 
                                                "calibration_equation":cal_eq, "number_calibration_indices":num_cal_indices,
                                                "active_calpage":active_calpage, "cal0k0":cal0k0, "cal0k1":cal0k1,
                                                "cal0k2":cal0k2,"units0":units0, "cal1k0":cal1k0, "cal1k1":cal1k1, 
                                                "cal1k2":cal1k2, "units1":units1,"cal2k0":cal2k0, "cal2k1":cal2k1, 
                                                "cal2k2":cal2k2, "units2":units2}
            elif channel == 2:
                channel_dictionary["ch2"] = {"long_name":long, "short_name":short, "op_type":op_type, 
                                                "calibration_equation":cal_eq, "number_calibration_indices":num_cal_indices,
                                                "active_calpage":active_calpage, "cal0k0":cal0k0, "cal0k1":cal0k1,
                                                "cal0k2":cal0k2,"units0":units0, "cal1k0":cal1k0, "cal1k1":cal1k1, 
                                                "cal1k2":cal1k2, "units1":units1,"cal2k0":cal2k0, "cal2k1":cal2k1, 
                                                "cal2k2":cal2k2, "units2":units2}
            elif channel == 3:
                channel_dictionary["ch3"] = {"long_name":long, "short_name":short, "op_type":op_type, 
                                                "calibration_equation":cal_eq, "number_calibration_indices":num_cal_indices,
                                                "active_calpage":active_calpage, "cal0k0":cal0k0, "cal0k1":cal0k1,
                                                "cal0k2":cal0k2,"units0":units0, "cal1k0":cal1k0, "cal1k1":cal1k1, 
                                                "cal1k2":cal1k2, "units1":units1,"cal2k0":cal2k0, "cal2k1":cal2k1, 
                                                "cal2k2":cal2k2, "units2":units2}

        device_channel_dictionary.append(channel_dictionary)
        
    return device_channel_dictionary

def get_sensor_operation_type_list():
    """ Return op_type_list and probe_type_list. This info is required for how an analog channel is 
    configured and read.
    """

    op_type_list = []
    probe_type_list = []

    for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
        op_type_by_device = []
        probe_type_by_device = []
        # get the sensor info for each enabled channel
        for channel in device_enabled_chs:
            op_type = ngio_sensor.ddsmem_get_operation_type(hDevice, channel)

            if op_type == 2: 
                probe_type = 3   # an op_type = 2 (10V) means probe type = 3 (10 V)
            else:
                probe_type = 2   # an op_type = 14 (5V) means probe type = 2 (5 V) 

            op_type_by_device.append(op_type)
            probe_type_by_device.append(probe_type)

        # build the 2D op_type and probe_type sensor list 
        op_type_list.append(op_type_by_device)
        probe_type_list.append(probe_type_by_device)
 
    return op_type_list, probe_type_list

def get_sensor_calibration_values():
    """ Return sensor_cal_list
    """

    sensor_cal_list = []

    for hDevice, device_enabled_chs in zip(config.hDevice, config.enabled_analog_channels):
        sensor_cal_by_device = []
        # get the sensor info for each enabled channel
        for channel in device_enabled_chs:
            sensor_cal_dict = {}
            
            cal_eq = ngio_sensor.ddsmem_get_calibration_equation(hDevice, channel)
            active_calpage = ngio_sensor.ddsmem_get_active_cal_page(hDevice, channel)
            active_cal0, active_cal1, active_cal2, active_units = ngio_sensor.ddsmem_get_cal_page(
                    hDevice, channel, index=active_calpage)
            
            sensor_cal_dict = {"equation":cal_eq, "cal0":active_cal0, "cal1":active_cal1, "cal2":active_cal2,
                                "units":active_units, "active_calpage":active_calpage}

            # build a list of the sensor's equation and calibration values for this device
            sensor_cal_by_device.append(sensor_cal_dict)
        
        sensor_cal_list.append(sensor_cal_by_device)

    return sensor_cal_list




                                                
                