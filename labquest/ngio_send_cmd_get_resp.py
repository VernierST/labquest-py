from ctypes import *

from labquest import config    # get the dll object from the config.py file


def send_cmd_get_response(hDevice, command, parameters, param_bytes): 
    """
    Send a command to the specified device hardware and wait for a response.
    """
    
    # Get a pointer to the SendCmdAndGetResponse function
    p_send_cmd_get_response = config.dll.NGIO_Device_SendCmdAndGetResponse
    # Configure the the SendCmdAndGetResponse function
    p_send_cmd_get_response.argtypes = [c_ssize_t, c_ubyte, POINTER(c_int8), c_uint32, 
                                                 POINTER(c_int8), POINTER(c_uint32), c_uint32]
    # Set the the SendCmdAndGetResponse function return type
    p_send_cmd_get_response.restype = c_int32
    # Set parameters
    command = c_uint8(command) 
    parameters_new = (c_int8 * 14)(parameters[0], parameters[1], parameters[2], parameters[3],
        parameters[4], parameters[5], parameters[6], parameters[7], parameters[8], parameters[9], parameters[10],
        parameters[11], parameters[12], parameters[13])
    param_bytes = c_uint32(param_bytes) #size of parameter array
    resp_buffer = (c_int8 *256)(0)
    resp_bytes = c_uint32(256)
    timeout_ms = c_uint32(2000)
    # Call the the SendCmdAndGetResponse function in the DLL
    send_cmd_get_response_return = p_send_cmd_get_response(
           hDevice, command, parameters_new, param_bytes, resp_buffer, resp_bytes, timeout_ms)
    # Check the the SendCmdAndGetResponse function return value. Return: 0 if successful, else -1!
    if send_cmd_get_response_return == -1:
        config.logger.debug("ERROR calling NGIO_send_cmd_get_response")
        
    return resp_buffer, resp_bytes.value