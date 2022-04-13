from ctypes import *
import os
import platform
import struct


from labquest import config

def load_library():
    """ Load the NGIO shared library into memory. There are three different NGIO libraries. One for
    Mac, one for Windows running 32-bit Python, and one for Windows running 64-bit Python. Determine
    which library to use.

    Returns:
        pointer to the library
    """
    library_folder = "labquest" + os.path.sep + "data"
    os_name = platform.system()
    if os_name == 'Windows':
        python_bits = struct.calcsize("P") * 8
        if python_bits == 64:
            dll_name = "NGIO_lib_for_64bit_python"
        else:
            dll_name = "NGIO_lib_for_32bit_python"
    elif os_name == 'Darwin':
        dll_name = "libNGIOUniversal.dylib"
    else:
        config.logger.debug(str(os_name) + " not supported. Only Darwin (Mac) and Windows OS supported.")
    config.logger.debug("Name of the shared library to open: " + str(dll_name))
    
    
    # This code will use the path to the directory of this file to create the path to the dll file
    #dll_file_path = (os.path.dirname(__file__)) + os.path.sep + dll_name
    dll_file_path = os.path.dirname((os.path.dirname(__file__))) + os.path.sep + library_folder + os.path.sep + dll_name
    config.logger.debug("File path to locate the NGIO shared library:  " + str(dll_file_path))
    dll = cdll.LoadLibrary(dll_file_path)
    
    return dll


def ngio_init():
    """ Call NGIO_Init() once before making any other NGIO function calls.
    Return:		
        NGIO Library Handle (hLib) if successful, else NULL.
    """
    p_init = config.dll.NGIO_Init
    # The Init function does not accept any arguments
    p_init.argtypes = None
    # Set the Init function return type (not sure if int64 is correct?)
    #p_init.restype = c_int64
    p_init.restype = c_ssize_t
    # Call the NGIO_Init function in the DLL
    hLib = p_init(None)
    # Check the return value.  If a handle value = 0, then did not open
    if hLib == 0:
        config.logger.debug("Unable to open NGIO Library Handle (hLib) in the Init")
    return hLib


def ngio_get_dll_version():
    """ Get the NGIO version number.
    Return:		
        major and minor version numbers of the NGIO library
    """
    # Get a pointer to the GetDLLVersion function
    p_get_dll_version = config.dll.NGIO_GetDLLVersion
    # Configure the GetDLLVersion arguments
    #p_get_dll_version.argtypes = [c_int64, POINTER(c_uint16), POINTER(c_uint16)]
    p_get_dll_version.argtypes = [c_ssize_t, POINTER(c_uint16), POINTER(c_uint16)]
    # Set the GetDLLVersion function return type
    p_get_dll_version.restype = c_int32
    # Output parameters
    maj = c_uint16()
    min = c_uint16()
    # Call the NGIO_GetDLLVersion function in the DLL
    get_dll_version_return = p_get_dll_version(config.hLib, byref(maj), byref(min))
    # Check the return value (0 if successful, else -1)
    if get_dll_version_return == -1:
        config.logger.debug("ERROR opening NGIO_GetDLLVersion")   
    #return "Found NGIO library: Version " + str(maj.value) +"." + str(min.value)
    return maj.value, min.value