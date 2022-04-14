from ctypes import *

from labquest import config


def device_close(hDevice):
    """ Close a specified device. After this routine runs, the hDevice handle is no longer valid.
    """

    # Get a pointer to the device_close command
    p_device_close = config.dll.NGIO_Device_Close
    # Configure the device_close command arguments
    p_device_close.argtypes = [c_ssize_t]
    # Set the device_close command return type
    p_device_close.restype = c_int32
    # Set parameters
    # Call the device_close command in the DLL
    device_close_return = p_device_close(hDevice)

    # LQ Stream will sometimes drop NGIO as soon as Close as been sent. This can result 
    # in a -1 error being sent. We do not want to count this as an error and so we are 
    # dropping the Error out from this function call. 
    
    return device_close_return

def ngio_uninit():
    """ Call NGIO_Uninit() once to 'undo' NGIO_Init().
    """
     # Get a pointer to the Uninit function
    p_uninit = config.dll.NGIO_Uninit
    # Configure the Uninit arguments
    p_uninit.argtypes = [c_ssize_t]
    # Set the Uninit function return type
    p_uninit.restype = c_int32
    # Output parameters
    # Call the NGIO_Uninit function in the DLL
    uninit_return = p_uninit(config.hLib)
    # Check the return value (0 if successful, else -1)
    if uninit_return == -1:
        config.logger.debug("ERROR calling NGIO_Uninit")  