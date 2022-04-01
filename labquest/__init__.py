# -*- coding: utf-8 -*-
import logging
import importlib.util
import platform

from labquest import config
from labquest import labquest_init_functions as init
from labquest import labquest_open_functions as open
from labquest import labquest_read_functions as read
from labquest import labquest_select_sensors_functions as sensor
from labquest import labquest_sensor_info_functions as info
from labquest import labquest_start_functions as start
from labquest import labquest_stop_close_functions as stop
from labquest import labquest_dcu_functions as dcu
from labquest import labquest_photogate_timing_functions as photo

class LabQuest:
	""" The labquest module wraps the hidapi and bleak modules to create an easy way to
	interact with Vernier GoDirect devices.
	"""

	VERSION = "0.1.3"

	""" A class used for labquest communication."""
	
	# Variables passed between the functions are stored in the config.py file
	 

	def __init__(self):
		""" Load the NGIO shared library (dll), retrieve the library handle (hLib), and get 
		the dll library version number.
		"""

		config.logger = logging.getLogger(__name__)

		dll_version = init.load_ngio_library_get_version()
		config.logger.info("Version " + self.VERSION)
		config.logger.info("NGIO library: Version " + dll_version)

	def get_version(self):
		""" Get the library version

		Returns:
			godirect version number (int)
		"""
		return self.VERSION

	def open(self):
		"""Open and get a device handle (hDevice) for each LabQuest device.
		
		Determine the device type connected (LQ Mini, LQ3, LQ2, LQ Stream, or Original LQ), 
		and how many of that type. 

		Returns:
			0 if successful, else -1!
		"""

		device_type_name = open.open_labquest_devices()
		if device_type_name == "no_device":
			config.logger.debug("No LabQuest device found")  
			return_value = -1
		else:
			return_value = 0	
		
		return return_value


	def select_sensors(self, *args):
		""" Configure your LabQuest channels. if the select_sensors argument is left blank, 
			a list of sensor channels is provided by a prompt in the terminal for the user 
			to select from. To run code without a prompt, set the argument as a library
			(or libraries, if connecting multiple LabQuest devices)
		
		Args: 
			* args: a library for each device, where the key refers to the 
			channel, and the value refers to how the channel is configured. 
			
			The key options are:
				'ch1', 'ch2', 'ch3', 'dig1', and 'dig2'. 
			The values for the 3 analog channels are:
				'default', 'cal0', 'cal1', 'cal2', 'raw_voltage'. 
			The dig channel values are:
				'motion', 'photogate', 'rotary_motion', 'rotary_motion_high_res', 'dcu', 'dcu_pwm'. 
			
		Example: 
			Temp sensor connected to channel 1 and wanting to read in degrees Celsius:
				select_sensors('ch1':'default')
		Example:
			Temp sensor connected to channel 1, wanting degrees Fahrenheit, and a non-Vernier
			sensor connected to ch2:
				select_sensors('ch1':'cal1', 'ch2':'raw_voltage')
		"""

		# if no devices or no device handles were found then exit this function
		if not config.device_type or not config.hDevice:
			return	   

		active_sensor_channels = sensor.configure_channels_and_sensors(*args)
		if not any(active_sensor_channels):
			config.logger.debug("No sensors configured or detected")
		else:
			config.logger.info("Channels configured: " + str(active_sensor_channels))
			pass


	def sensor_info(self, device=0, channel=1):
		""" Returns sensor information, such as the calibration equation that is stored
		on the sensor.   
		"""			 
		
		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			return		 
		
		# analog sensor info is configured in the labquest_select_sensors_functions.py, and stored in the config file
		sensor_info = info.get_sensor_info(device, channel)
		
		return sensor_info

	def enabled_sensor_info(self):
		""" Returns each enabled sensors' name and units (good for column headers).

		Returns:
			sensor_info[]: A 1D list that includes each enabled sensors' long name with 
			units, e.g. ['Force (N)', 'X-axis acceleration (m/s²)'].  
		"""

		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			return 

		enabled_sensor_info_list = info.get_sensor_long_name_and_units()

		if len(enabled_sensor_info_list) == 1:
			return enabled_sensor_info_list[0]
		else:
			return enabled_sensor_info_list

	   
	def start(self, period=None, reset_dig_counter=True):
		""" Start collecting data from the sensors that were selected in the select_sensors() function. 
		
		Args: 
			period (int): Milliseconds between samples. If period is left blank, a prompt in the 
			terminal allows the user to enter the period . 

			reset_dig_counter(boolean): If reset_dig_counter =True, the digital counter for rotary 
			motion and photogate counting will be reset to zero.
		"""   

		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			return 

		# If the period argument is left blank provide an input prompt for the user to enter the period.
		if period == None: 
			if config.photogate_timing:	
				period = 1000	# photogate_timing does not use a sample period, so just give it a value
			elif config.dcu_pwm and not any(config.enabled_analog_channels) and not config.motion:
				period = 1000	# dcu pwm does not use sample period
			elif config.dcu and not any(config.enabled_analog_channels) and not config.motion:
				period = 1000	# dcu does not use sample period
			else:
				print("select period (ms):", end=' ')
				period = int(input())
		
		# Set the measurement period. Needs to be in seconds. So convert from milliseconds to seconds
		sample_period = period/1000

		# Set the analog input value, the mask value, and sampling mode
		start.configure_channels_to_start(sample_period, reset_dig_counter)

		# start data collection
		start.start_measurements()						  

		
	def read(self):
		""" Take single point readings from the enabled sensors and return the readings.

		Returns:
			measurements: A single data point for each enabled sensor. If
			a single sensor is connected, just the data point is returned. Otherwise a list
			containing each configured sensor's data point. 
		"""	  
		
		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			return		 
		
		measurements = read.get_all_measurements()

		if not measurements:
			return None
		elif len(measurements) == 1:
			return measurements[0]
		else:
			return measurements

	def read_multi_pt(self, num_measurements_to_read):
		""" Take multi-point readings from the enabled sensors 

		Args: 
			num_measurements_to_read (int):  number of samples to collect.

		Returns:
			measurements[]: a list containing the packet of data from each 
			configured sensor. The list will contain the number of measurements 
			asked for in the argument. 
		"""	  
		
		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			return		 
		
		measurements = read.get_multi_pt_measurements(num_measurements_to_read)

		if not measurements:
			return None
		elif len(measurements) == 1:
			return measurements[0]
		else:
			return measurements

	
	def stop(self, stop_measurements=True, stop_dcu=True, stop_pwm=True):
		""" Stop data collection, turn off dcu lines, stop pwm output

		Args:
			stop_measurements(bool): if True, stop data acquisition

			stop_dcu(bool): if True, and the DCU has been configured, all DCU
			lines will be turned off.

			stop_pwm(bool): if True, and PWM has been configured, the pwm
			output will be stopped.
		"""

		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			return	  

		# Stop the measurements and clear the ngio measurement buffer and the config.buffer
		if stop_measurements:
			stop.stop_measurements_clear_buffer()

		if stop_dcu and config.dcu:
			dcu.dcu_all_lines_off()

		if stop_pwm and config.dcu_pwm:
			dcu.stop_pwm()


	def close(self):
		""" Close all devices. After this routine runs, the device handle (hDevice) is 
		no longer valid.
		"""
		
		stop.close()

	
	def dcu(self, *values):
		""" Control the output lines of the DCU

		Args: 
			*values: send the DCU a value from 0-15 to turn lines on and off. 
		"""
		
		dcu.set_io_line(*values)

	def dcu_pwm(self, frequency_Hz, duty_cycle):
		""" Control the PWM output from line D4 of dig1
		
		Args: 
			frequency_Hz (int): 2.5 Hz (0.4 sec period) to 1,000,000 Hz (1 microsecond period).

			duty_cycle (int):  set the duty cycle with a value of 0 to 100
		"""
		
		dcu.set_pwm(frequency_Hz, duty_cycle)


	def photogate_timing(self, samples, timeout):
		"""Perform photogate timing

		Args: 
			samples(int): number of timing samples to record

			timeout: (seconds) Maximum time to wait for all samples to be collected.

		Returns: 
			timing_values: returns the photogate blocked time, unblocked time, 
			blocked time, unblocked time, etc..
		"""

		samples = samples + 2	# to get the number of samples requested, actually need 2 extra
		timeout = timeout/3   # the read takes 3x the timeout, so need to divide by 3 here
		timing_values = photo.get_photogate_timing(samples, timeout)

		return timing_values
