from labquest import config
from labquest import ngio_library_functions as ngio_lib


def load_ngio_library_get_version():
    """ Find and load the NGIO library and give it the variable name, "dll"
    """
    
    
    # save the dll object to the config file
    config.dll = ngio_lib.load_library() 
    
    # save the Library Handle (hLib) to the config file
    config.hLib = ngio_lib.ngio_init()

    # Get the NGIO dll version number
    major_version, minor_version = ngio_lib.ngio_get_dll_version()
    dll_version = str(major_version) +"." + str(minor_version)
    
    return dll_version
   
