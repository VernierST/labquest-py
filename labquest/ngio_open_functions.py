from ctypes import *

from labquest import config


def search_for_device(device_type):
    """
    Purpose:	The NGIO library maintains a separate list of available devices for each supported device type.
				NGIO_SearchForDevices() updates the list for the specified device type.

				For each device list a signature is maintained that is incremented every time the list changes. 

	Return:		0 iff successful, else -1.
    """

    # Get a pointer to the SearchForDevices function
    p_search_for_devices = config.dll.NGIO_SearchForDevices
    # Configure the SearchForDevices arguments
    p_search_for_devices.argtypes = [c_ssize_t, c_uint32, c_uint32, c_int32, POINTER(c_uint32)]
    # Set the SearchForDevices function return type
    p_search_for_devices.restype = c_int32
    # Set parameters
    device_type = c_uint32(device_type)
    comm_transport_id = c_uint32(1) #USB has a value of 1
    p_params = c_int32(0)
    p_device_list_signature = c_uint32(0)
    # Call the SearchForDevices function in the DLL using the specified device type
    search_for_devices_return = p_search_for_devices(
           config.hLib, device_type, comm_transport_id, p_params, byref(p_device_list_signature))
    if search_for_devices_return == -1:
        config.logger.debug("ERROR calling NGIO_SearchForDevices")
    # A device list signature value > 0 means a device was found
    return int(p_device_list_signature.value)
 
def open_device_list_snapshot():
    """
    Return: Handle to device list snapshot if successful, else NULL.
    """
    # Get a pointer to the OpenDeviceListSnapshot function
    p_open_device_list_snapshot = config.dll.NGIO_OpenDeviceListSnapshot
    # Configure the OpenDeviceListSnapshot arguments
    p_open_device_list_snapshot.argtypes = [c_ssize_t, c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
    # Set the OpenDeviceListSnapshot function return type (not sure if ssc_ssize_t is correct?)
    p_open_device_list_snapshot.restype = c_ssize_t
    # Set parameters 
    p_num_devices = c_uint32(0)  #pointer to storage location for the number of devices
    p_device_list_signature = c_uint32(0)
    # Call the OpenDeviceListSnapshot function in the DLL
    hDeviceList = p_open_device_list_snapshot(config.hLib, config.device_type, byref(p_num_devices), 
                                              byref(p_device_list_signature))
    # Check the OpenDeviceListSnapshot return value.  If a handle value is returned, success!
    if hDeviceList == 0:
        config.logger.debug("ERROR calling NGIO_OpenDeviceListSnapshot")
    # Return: Handle to device list snapshot if successful, else NULL.
    return hDeviceList,int(p_num_devices.value)

def snapshot_get_nth_entry(hDeviceList, index):
    """
    Pass the device name string placed in *pDevnameBuf to NGIO_Device_Open() to open the device.
    """
    # Get a pointer to the DeviceListSnapshot_GetNthEntry function
    p_snapshot_get_nth_entry = config.dll.NGIO_DeviceListSnapshot_GetNthEntry
    # Configure the DeviceListSnapshot_GetNthEntry arguments
    p_snapshot_get_nth_entry.argtypes = [c_ssize_t, c_uint32, c_char_p, c_uint32, POINTER(c_uint32)]
    # Set the DeviceListSnapshot_GetNthEntry function return type (not sure if ssc_ssize_t is correct?)
    p_snapshot_get_nth_entry.restype = c_int32
    # Set parameters
    n = c_uint32(index)
    p_devname_buf = c_char_p(b"\0" * 220)
    buf_size = c_uint32(220)
    p_device_status_mask = c_uint32(0) 
    # Call the DeviceListSnapshot_GetNthEntry function in the DLL
    device_snapshot_get_nth_return = p_snapshot_get_nth_entry(
            hDeviceList, n, p_devname_buf, buf_size, byref(p_device_status_mask))  

    device_name = p_devname_buf.value
    # Check the DeviceListSnapshot_GetNthEntry return value. Return: 0 if successful, else -1!
    if device_snapshot_get_nth_return == -1:
        config.logger.debug("ERROR calling NGIO_DeviceListSnapshot_GetNthEntry")
    return device_name


def close_device_list_snapshot(hDeviceList):
    """
    Close the list created by NGIO_OpenDeviceListSnapshot().
    Return:	0 iff successful, else -1.
    """
    # Get a pointer to the CloseDeviceListSnapshot function
    p_close_device_list_snapshot = config.dll.NGIO_CloseDeviceListSnapshot
    # Configure the CloseDeviceListSnapshot arguments
    p_close_device_list_snapshot.argtypes = [c_ssize_t]
    # Set the SearchForDevices function return type
    p_close_device_list_snapshot.restype = c_int32
    # Call the CloseDeviceListSnapshot function in the DLL
    close_device_list_snapshot_return = p_close_device_list_snapshot(hDeviceList)
    # Check the CloseDeviceListSnapshot return value. Return: 0 if successful, else -1!
    if close_device_list_snapshot_return == -1:
        config.logger.debug("ERROR calling NGIO_CloseDeviceListSnapshot")   
    return close_device_list_snapshot_return

def device_open(p_devname_buf):
    """
    Open a device with the name returned by NGIO_DeviceListSnapshot_GetNthEntry.

    Return:	handle to open device if successful (hDevice), else NULL.
    """
    # Get a pointer to the DeviceOpen function
    p_device_open = config.dll.NGIO_Device_Open
    # Configure the DeviceOpen arguments
    p_device_open.argtypes = [c_ssize_t, c_char_p, c_uint8]
    # Set the DeviceOpen function return type (not sure if ssc_ssize_t is correct?)
    p_device_open.restype = c_ssize_t
    # Set parameters
    p_name = c_char_p(p_devname_buf)
    demand_exclusive_ownership = c_uint8(0) #not sure if this should be u8 or bool
    # Call the DeviceOpen function in the DLL
    hDevice = p_device_open(config.hLib, p_name, demand_exclusive_ownership)
    # Check the DeviceOpen return value.  If a handle value is returned, success!
    # Return:	handle to open device if successful (hDevice), else NULL.
    config.logger.debug("Device handle (hDevice) = " + str(hDevice))
    return hDevice

def acquire_exclusive_ownership(hDevice):
    """
    Tell the LabQuest's built in data collection app to stop collecting data and then grab exclusive ownership
	of LabQuest's data acquisition facilities(the DAQ).
    """

    # Get a pointer to the function
    p_acquire_exclusive_ownership = config.dll.NGIO_Device_AcquireExclusiveOwnership
    # Configure the arguments
    p_acquire_exclusive_ownership.argtypes = [c_ssize_t, c_uint32]
    # Set the return type
    p_acquire_exclusive_ownership.restype = c_int32
    # Set parameters
    timeout = c_uint32(12000)
    # Call the command in the DLL
    aquire_exclusive_ownership_return = p_acquire_exclusive_ownership(hDevice, timeout)

    # Check the  return value. Return: 0 if successful, else -1!
    if aquire_exclusive_ownership_return == -1:
        config.logger.debug("ERROR calling NGIO_CloseDeviceListSnapshot")   
    return aquire_exclusive_ownership_return
