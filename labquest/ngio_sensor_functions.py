from ctypes import *

from labquest import config   # get the dll object that is stored in the config.py file


def ddsmem_read_record(hDevice, channel):
    """
    copies data stored on the sensor hardware to the SensorDDSRecord allocated on the host computer.
    """
    # Get a pointer to the DDSMem_ReadRecord command
    p_ddsmem_read_record = config.dll.NGIO_Device_DDSMem_ReadRecord
    # Configure the DDSMem_ReadRecord command arguments
    p_ddsmem_read_record.argtypes = [c_ssize_t, c_byte, c_bool, c_uint32]
    # Set the DDSMem_ReadRecord command return type
    p_ddsmem_read_record.restype = c_int32
    # Set parameters
    channel = c_byte(channel) 
    strict_dds_validation_flag = c_bool(False)
    timeout_ms = c_uint32(2000)
    # Call the DDS_ReadRecord command in the DLL
    ddsmem_read_record_return = p_ddsmem_read_record(hDevice, channel, strict_dds_validation_flag, timeout_ms)
    # Check the DDS_ReadRecord command return value.  If a 0 returned, success, else -1!
    if ddsmem_read_record_return == -1:
        config.logger.debug("ERROR calling DDSMem ReadRecord")


def ddsmem_get_long_name(hDevice, channel):
    """ Get the sensor's long name stored in the dds record
    """
    # Get a pointer to the DDSMem_GetLongName command
    p_ddsmem_get_long_name = config.dll.NGIO_Device_DDSMem_GetLongName
    # Configure the DDSMem_GetLongName command arguments
    p_ddsmem_get_long_name.argtypes = [c_ssize_t, c_byte, c_char_p, c_uint16]
    # Set the DDSMem_GetLongName command return type
    p_ddsmem_get_long_name.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_long_name = c_char_p(b"\0" * 100)
    max_num_bytes_to_copy = c_uint16(100)
    # Call the DDS_GetLongName command in the DLL
    ddsmem_get_long_name_return = p_ddsmem_get_long_name(hDevice, channel, p_long_name, max_num_bytes_to_copy )
    # Check the DDS_GetLongName command return value.  If a 0 returned, success, else -1!
    if ddsmem_get_long_name_return == -1:
        config.logger.debug("ERROR calling DDSMem GetLongName")
    config.logger.debug("sensor long name = " + str(p_long_name.value))
    return str(p_long_name.value.decode('utf-8'))


def ddsmem_set_long_name(hDevice, channel, long_name):
    """ Set a long name in the dds record for the given channel
    """
    # Get a pointer to the DDSMem_SetLongName command
    p_ddsmem_set_long_name = config.dll.NGIO_Device_DDSMem_SetLongName
    # Configure the DDSMem_SetLongName command arguments
    p_ddsmem_set_long_name.argtypes = [c_ssize_t, c_byte, c_char_p]
    # Set the DDSMem_SetLongName command return type
    p_ddsmem_set_long_name.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    # have to convert the long name string to bytes
    p_long_name = c_char_p(long_name.encode('utf-8'))
    # Call the DDS_SetLongName command in the DLL
    ddsmem_set_long_name_return = p_ddsmem_set_long_name(hDevice, channel, p_long_name)
    # Check the DDS_SetLongName command return value.  If a 0 returned, success, else -1!
    if ddsmem_set_long_name_return == -1:
        config.logger.debug("ERROR calling DDSMem SetLongName")


def ddsmem_get_short_name(hDevice, channel):
    """ Get the sensor's short name stored in the dds record
    """
    # Get a pointer to the DDSMem_GetShortName command
    p_ddsmem_get_short_name = config.dll.NGIO_Device_DDSMem_GetShortName
    # Configure the DDSMem_GetShortName command arguments
    p_ddsmem_get_short_name.argtypes = [c_ssize_t, c_byte, c_char_p, c_uint16]
    # Set the DDSMem_GetShortName command return type
    p_ddsmem_get_short_name.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_short_name = c_char_p(b"\0" * 100)
    max_num_bytes_to_copy = c_uint16(100)
    # Call the DDS_GetShortName command in the DLL
    ddsmem_get_short_name_return = p_ddsmem_get_short_name(hDevice, channel, p_short_name, max_num_bytes_to_copy)
    # Check the DDS_GetShortName command return value.  If a 0 returned, success, else -1!
    if ddsmem_get_short_name_return == -1:
        config.logger.debug("ERROR calling DDSMem GetShortName")
    config.logger.debug("sensor short name = " + str(p_short_name.value))
    return str(p_short_name.value.decode('utf-8'))


def ddsmem_set_short_name(hDevice, channel, short_name):
    """
    Set a short name in the dds record for the given channel
    """
    # Get a pointer to the DDSMem_SetShortName command
    p_ddsmem_set_short_name = config.dll.NGIO_Device_DDSMem_SetShortName
    # Configure the DDSMem_SetShortName command arguments
    p_ddsmem_set_short_name.argtypes = [c_ssize_t, c_byte, c_char_p]
    # Set the DDSMem_SetShortName command return type
    p_ddsmem_set_short_name.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    # have to convert the short name string to bytes
    p_short_name = c_char_p(short_name.encode('utf-8'))
    # Call the DDS_SetShortName command in the DLL
    ddsmem_set_short_name_return = p_ddsmem_set_short_name(hDevice, channel, p_short_name)
    # Check the DDS_SetShortName command return value.  If a 0 returned, success, else -1!
    if ddsmem_set_short_name_return == -1:
        config.logger.debug("ERROR calling DDSMem SetShortName")


def ddsmem_get_typ_sample_period(hDevice, channel):
    """
    Get the sample period stored in the dds record
    """
    # Get a pointer to the DDSMem_GetTypSamplePeriod command
    p_ddsmem_get_typ_sample_period = config.dll.NGIO_Device_DDSMem_GetTypSamplePeriod
    # Configure the DDSMem_GetTypSamplePeriod command arguments
    p_ddsmem_get_typ_sample_period.argtypes = [c_ssize_t, c_byte, POINTER(c_float)]
    # Set the DDSMem_GetTypSamplePeriod command return type
    p_ddsmem_get_typ_sample_period.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_typ_sample_period = c_float(0)
    # Call the DDS_GetTypSamplePeriod command in the DLL
    ddsmem_get_typ_sample_period_return = p_ddsmem_get_typ_sample_period(hDevice, channel, p_typ_sample_period)
    # Check the DDS_GetTypSamplePeriod command return value.  If a 0 returned, success, else -1!
    if ddsmem_get_typ_sample_period_return == -1:
        config.logger.debug("ERROR calling DDSMem GetTypSamplePeriod")
    config.logger.debug("typical sample period = " + str(p_typ_sample_period.value))
    return p_typ_sample_period.value


def ddsmem_get_calibration_equation(hDevice, channel):
    """
    Get the calibration equation stored in the dds record
    """
    # Get a pointer to the DDSMem_GetCalibrationEquation command
    p_ddsmem_get_calibration_equation = config.dll.NGIO_Device_DDSMem_GetCalibrationEquation
    # Configure the DDSMem_GetCalibrationEquation command arguments
    p_ddsmem_get_calibration_equation.argtypes = [c_ssize_t, c_byte, POINTER(c_byte)]
    # Set the DDSMem_GetCalibrationEquation command return type
    p_ddsmem_get_calibration_equation.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_calibration_equation = c_byte(0)
    # Call the DDS_GetCalibrationEquation command in the DLL
    ddsmem_get_calibration_equation_return = p_ddsmem_get_calibration_equation(
            hDevice, channel, p_calibration_equation)
    # Check the DDS_GetCalibrationEquation command return value.  If a 0 returned, success, else -1!
    if ddsmem_get_calibration_equation_return == -1:
        config.logger.debug("ERROR calling DDSMem GetCalibrationEquation")
    return p_calibration_equation.value


def ddsmem_set_calibration_equation(hDevice, channel, cal_equation):
    """
    Set a calibration equation in the dds record for the given channel
    """
    # Get a pointer to the DDSMem_SetCalibrationEquation command
    p_ddsmem_set_calibration_equation = config.dll.NGIO_Device_DDSMem_SetCalibrationEquation
    # Configure the DDSMem_SetCalibrationEquation command arguments
    p_ddsmem_set_calibration_equation.argtypes = [c_ssize_t, c_byte, c_char]
    # Set the DDSMem_SetCalibrationEquation command return type
    p_ddsmem_set_calibration_equation.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    calibration_equation = c_char(cal_equation)
    # Call the DDS_SetCalibrationEquation command in the DLL
    ddsmem_set_calibration_equation_return = p_ddsmem_set_calibration_equation(hDevice, channel, calibration_equation)
    # Check the DDS_SetCalibrationEquation command return value.  If a 0 returned, success, else -1!
    if ddsmem_set_calibration_equation_return == -1:
        config.logger.debug("ERROR calling DDSMem SetCalibrationEquation")


def ddsmem_get_active_cal_page(hDevice, channel):
    """
    Get the active calibration page index in the dds record. 3 pages can be stored (index = 0,1,2)
    """
    # Get a pointer to the DDSMem_GetActiveCalPage command
    p_ddsmem_get_active_cal_page = config.dll.NGIO_Device_DDSMem_GetActiveCalPage
    # Configure the DDSMem_GetActiveCalPage command arguments
    p_ddsmem_get_active_cal_page.argtypes = [c_ssize_t, c_byte, POINTER(c_ubyte)]
    # Set the DDSMem_GetActiveCalPage command return type
    p_ddsmem_get_active_cal_page.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_active_cal_page = c_ubyte(0)
    # Call the DDS_GetActiveCalPage command in the DLL
    p_ddsmem_get_active_cal_page_return = p_ddsmem_get_active_cal_page(
        hDevice, channel, p_active_cal_page)
    # Check the DDS_GetActiveCalPage command return value.  If a 0 returned, success, else -1!
    if p_ddsmem_get_active_cal_page_return == -1:
        config.logger.debug("ERROR calling DDSMem GetActiveCalPage")
    config.logger.debug("Active Cal Page = " + str(p_active_cal_page.value))
    return p_active_cal_page.value

def ddsmem_set_active_cal_page(hDevice, channel, active_calpage):
    """
    Set the active calibration page index (0,1,2) in the dds record for the given channel
    """
    # Get a pointer to the DDSMem_SetActiveCalPage command
    p_ddsmem_set_active_cal_page = config.dll.NGIO_Device_DDSMem_SetActiveCalPage
    # Configure the DDSMem_SetActiveCalPage command arguments
    p_ddsmem_set_active_cal_page.argtypes = [c_ssize_t, c_byte, c_ubyte]
    # Set the DDSMem_SetActiveCalPage command return type
    p_ddsmem_set_active_cal_page.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    active_cal_page = c_ubyte(active_calpage)
    # Call the DDS_SetActiveCalPage command in the DLL
    p_ddsmem_set_active_cal_page_return = p_ddsmem_set_active_cal_page(
        hDevice, channel, active_cal_page)
    # Check the DDS_SetActiveCalPage command return value.  If a 0 returned, success, else -1!
    if p_ddsmem_set_active_cal_page_return == -1:
        config.logger.debug("ERROR calling DDSMem SetActiveCalPage")

def ddsmem_get_highest_valid_cal_page_index(hDevice, channel):
    """
    Up to 3 calibration pages can be stored, but some sensors do not use all 3. If, for example
    a sensor had 2 cal pages, the highest valid index would be '1' (index 0 and 1). The 3rd calpage (index = 2)
    would not be used by this sensor.
    """
    # Get a pointer to the DDSMem_GetHighestValidCalPageIndex command
    p_ddsmem_get_highest_valid_cal_page_index = config.dll.NGIO_Device_DDSMem_GetHighestValidCalPageIndex
    # Configure the DDSMem_GetHighestValidCalPageIndex command arguments
    p_ddsmem_get_highest_valid_cal_page_index.argtypes = [c_ssize_t, c_byte, POINTER(c_ubyte)]
    # Set the DDSMem_GetHighestValidCalPageIndex command return type
    p_ddsmem_get_highest_valid_cal_page_index.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_highest_valid_cal_page_index = c_ubyte(0)
    # Call the DDS_GetHighestValidCalPageIndex command in the DLL
    p_ddsmem_get_highest_valid_cal_page_index_return = p_ddsmem_get_highest_valid_cal_page_index(
        hDevice, channel, p_highest_valid_cal_page_index)
    # Check the return value.  If a 0 returned, success, else -1!
    if p_ddsmem_get_highest_valid_cal_page_index_return == -1:
        config.logger.debug("ERROR calling DDSMem GetHighestValidCalPageIndex")
    config.logger.debug("Highest Valid Cal Page Index = " + str(p_highest_valid_cal_page_index.value))
    return p_highest_valid_cal_page_index.value

def ddsmem_set_highest_valid_cal_page_index(hDevice, channel, highest_calpage_index):
    """
    Set the highest valid cal page index in the dds record for the given channel. If, for example,
    there are 2 separate calibrations, the highest index would be '1' (index 0 and 1)
    """
    # Get a pointer to the DDSMem_SetHighestValidCalPageIndex command
    p_ddsmem_set_highest_valid_cal_page_index = config.dll.NGIO_Device_DDSMem_SetHighestValidCalPageIndex
    # Configure the DDSMem_SetHighestValidCalPageIndex command arguments
    p_ddsmem_set_highest_valid_cal_page_index.argtypes = [c_ssize_t, c_byte, c_ubyte]
    # Set the DDSMem_SetHighestValidCalPageIndex command return type
    p_ddsmem_set_highest_valid_cal_page_index.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    highest_valid_cal_page_index = c_ubyte(highest_calpage_index)
    # Call the DDS_SetHighestValidCalPageIndex command in the DLL
    p_ddsmem_set_highest_valid_cal_page_index_return = p_ddsmem_set_highest_valid_cal_page_index(
        hDevice, channel, highest_valid_cal_page_index)
    # Check the return value.  If a 0 returned, success, else -1!
    if p_ddsmem_set_highest_valid_cal_page_index_return == -1:
        config.logger.debug("ERROR calling DDSMem SetHighestValidCalPageIndex")

def ddsmem_get_cal_page(hDevice, channel, index):
    """
    Each of the three available cal pages can store 3 coefficients and 1 units value.

    Return:  calibration coefficients (a, b, and c) and units
    """
    # Get a pointer to the DDSMem_GetCalPage command
    p_ddsmem_get_cal_page = config.dll.NGIO_Device_DDSMem_GetCalPage
    # Configure the DDSMem_GetCalPage command arguments
    p_ddsmem_get_cal_page.argtypes = [c_ssize_t, c_byte, c_ubyte, POINTER(c_float), POINTER(c_float), 
                                      POINTER(c_float), c_char_p, c_uint16]
    # Set the DDSMem_GetCalPage command return type
    p_ddsmem_get_cal_page.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    cal_page_index = c_ubyte(index)
    p_calibration_coefficient_a = c_float(0)
    p_calibration_coefficient_b = c_float(0)
    p_calibration_coefficient_c = c_float(0)
    p_units = c_char_p(b"\0" * 20)
    max_num_bytes_to_copy = c_uint16(20)
    # Call the DDS_GetCalPage command in the DLL
    p_ddsmem_get_cal_page_return = p_ddsmem_get_cal_page(
        hDevice, channel, cal_page_index, p_calibration_coefficient_a, p_calibration_coefficient_b, 
        p_calibration_coefficient_c, p_units, max_num_bytes_to_copy)
    # Check the DDS_GetCalPage command return value.  If a 0 returned, success, else -1!
    if p_ddsmem_get_cal_page_return == -1:
        config.logger.debug("ERROR calling DDSMem GetCalPage")

    config.logger.debug("Coefficient A = " + str(p_calibration_coefficient_a.value))
    config.logger.debug("Coefficient B = " + str(p_calibration_coefficient_b.value))
    config.logger.debug("Coefficient C = " + str(p_calibration_coefficient_c.value))
    config.logger.debug("Units = " + str(p_units.value))

    return (p_calibration_coefficient_a.value, p_calibration_coefficient_b.value, 
       p_calibration_coefficient_c.value, p_units.value.decode('utf-8'))

def ddsmem_set_cal_page(hDevice, channel, index, a, b, c, units):
    """
    Set the three coefficients and units for the specified index in the dds record for the given channel
    """
    # Get a pointer to the DDSMem_SetCalPage command
    p_ddsmem_set_cal_page = config.dll.NGIO_Device_DDSMem_SetCalPage
    # Configure the DDSMem_SetCalPage command arguments
    p_ddsmem_set_cal_page.argtypes = [c_ssize_t, c_byte, c_ubyte, c_float, c_float, c_float, c_char_p]
    # Set the DDSMem_SetCalPage command return type
    p_ddsmem_set_cal_page.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    cal_page_index = c_ubyte(index)
    calibration_coefficient_a = c_float(a)
    calibration_coefficient_b = c_float(b)
    calibration_coefficient_c = c_float(c)
    # have to convert the units string to bytes
    p_units = c_char_p(units.encode('utf-8'))
    # Call the DDS_SetCalPage command in the DLL
    p_ddsmem_set_cal_page_return = p_ddsmem_set_cal_page(hDevice, channel, cal_page_index, 
        calibration_coefficient_a, calibration_coefficient_b, calibration_coefficient_c, p_units)
    # Check the DDS_SetCalPage command return value.  If a 0 returned, success, else -1!
    if p_ddsmem_set_cal_page_return == -1:
        config.logger.debug("ERROR calling DDSMem SetCalPage")

def ddsmem_get_operation_type(hDevice, channel):
    """
    Get the operation type for the sensor stored in dds memory.
    If (2 == OperationType) then the sensor is kProbeTypeAnalog10V, else kProbeTypeAnalog5V
    """  
    # Get a pointer to the DDSMem_GetOperationType command
    p_ddsmem_get_operation_type = config.dll.NGIO_Device_DDSMem_GetOperationType
    # Configure the DDSMem_GetOperationType command arguments
    p_ddsmem_get_operation_type.argtypes = [c_ssize_t, c_byte, POINTER(c_ubyte)]
    # Set the DDSMem_GetOperationType command return type
    p_ddsmem_get_operation_type.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    p_operation_type = c_ubyte(0)
    # Call the DDS_GetOperationType command in the DLL
    p_ddsmem_get_operation_type_return = p_ddsmem_get_operation_type(
        hDevice, channel, p_operation_type)
    # Check the DDS_GetOperationType command return value.  If a 0 returned, success, else -1!
    if p_ddsmem_get_operation_type_return == -1:
        config.logger.debug("ERROR calling DDSMem GetOperationType")
    config.logger.debug("Operation Type = " + str(p_operation_type.value))
    return p_operation_type.value 

def ddsmem_set_operation_type(hDevice, channel, op_type):
    """
    Set operation type in the dds record for the given channel.
    If (2 == OperationType) then the sensor is kProbeTypeAnalog10V, else kProbeTypeAnalog5V
    """  
    # Get a pointer to the DDSMem_SetOperationType command
    p_ddsmem_set_operation_type = config.dll.NGIO_Device_DDSMem_SetOperationType
    # Configure the DDSMem_SetOperationType command arguments
    p_ddsmem_set_operation_type.argtypes = [c_ssize_t, c_byte, c_ubyte]
    # Set the DDSMem_SetOperationType command return type
    p_ddsmem_set_operation_type.restype = c_int32
    # Set parameters
    channel = c_byte(channel)
    op_type = c_ubyte(op_type)
    # Call the DDS_SetOperationType command in the DLL
    p_ddsmem_set_operation_type_return = p_ddsmem_set_operation_type(
        hDevice, channel, op_type)
    # Check the DDS_SetOperationType command return value.  If a 0 returned, success, else -1!
    if p_ddsmem_set_operation_type_return == -1:
        config.logger.debug("ERROR calling DDSMem SetOperationType")
