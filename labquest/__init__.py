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
from labquest import labquest_buffer_functions as buffer
buf = buffer.lq_buffer()

class LabQuest:
	""" The labquest module creates an easy way to interact with Vernier LabQuest devices.
	"""

	VERSION = "1.0.0"

	""" A class used for labquest communication."""
	
	# Variables passed between the functions are stored in the config.py file
	 

	def __init__(self):
		""" Load the NGIO shared library (dll or framework), retrieve the library handle (hLib), and get 
		the NGIO library version number.
		"""

		config.logger = logging.getLogger(__name__)

		dll_version = init.load_ngio_library_get_version()
		config.logger.info("Version " + self.VERSION)
		config.logger.info("NGIO library: Version " + dll_version)

	def get_version(self):
		""" Get the library version

		Returns:
			labquest version number (int)
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
			str1 = "No LabQuest device found \n\n"
			str2 = "Troubleshooting tips... \n"
			str3 = "Reconnect the USB cable \n"
			str4 = "Try a different USB port \n"
			str5 = "Try a different USB cable \n"
			str6 = "Turn on LabQuest units that have a power button \n"
			str7 = "Open GA (Graphical Analysis) to verify a good connection \n"
			str8 = "GA must be installed on Win computers to install a required driver \n"
			config.logger.info(str1 + str2 + str3 +str4 +str5 +str6 +str7 +str8)  

			return_value = -1
		
		else:
			return_value = 0	
		
		return return_value

	def select_sensors(self, ch1='no_sensor', ch2='no_sensor', ch3='no_sensor', dig1='no_sensor', dig2='no_sensor', device=0):
		""" Configure ch1, ch2, ch3, dig1, and dig2 with sensors. If connecting a LabQuest analog 
		sensor to ch1, ch2 or ch3, set the value to 'lq_sensor'. See Args below for other options.

		Args: 
			ch1, ch2, and ch3 (str):
			'lq_sensor', 'lq_sensor_cal0', 'lq_sensor_cal1', 'lq_sensor_cal2', 'raw_voltage', 'no_sensor'. 

			dig1 and dig2 (str):
			'motion', 'photogate_count', 'photogate_timing', 'rotary_motion', 'rotary_motion_high_res', 
			'dcu', 'dcu_pwm', 'no_sensor' 

			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1
			
		Example: 
			A Vernier LabQuest temp sensor connected to ch1 and wanting to read in degrees
			Celsius (which is the default calibration for this lq sensor):
				select_sensors(ch1='lq_sensor')
		Example:
			A Vernier Temp sensor connected to ch1 and wanting degrees Fahrenheit, and a motion
			detector connected to dig1:
				select_sensors(ch1='lq_sensor_cal1', dig1='motion')
		"""

		# if no devices or no device handles were found then exit this function
		if not config.device_type or not config.hDevice:
			config.logger.info("setup_channels() not executed due to no device or device handle")
			return	   

		active_sensor_channels = sensor.configure_channels(device, ch1, ch2, ch3, dig1, dig2)
		if not any(active_sensor_channels):
			config.logger.info("No sensors configured or detected")
		else:
			config.logger.info("Channels configured: " + str(active_sensor_channels))
			pass

	def sensor_info(self, ch, device=0):
		""" Returns analog sensor information, such as the calibration equations that are stored
		on the sensor. This only applies to analog sensors connected to ch1, ch2, or ch3.

		Args: 
			ch (str): Options include 'ch1', 'ch2', 'ch3'  

			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1
		"""			 
		
		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			config.logger.info("sensor_info() not executed due to no device, device handle, or sensors")
			return		 
		
		# analog sensor info is configured in the labquest_select_sensors_functions.py, and stored in the config file
		sensor_info = info.get_sensor_info(device, ch)
		
		return sensor_info

	def enabled_sensor_info(self, ch, device=0):
		""" Returns sensors' name and units (good for column headers).

		Args: 
			ch (str): Options include 'ch1', 'ch2', 'ch3', 'dig1', 'dig2'.  

			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1
		
		Returns:
			sensor_info (str): Sensor's long name with units, e.g. 'Force (N)' 
		"""

		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			config.logger.info("enabled_sensor_info() not executed due to no device, device handle, or sensors")
			return 

		enabled_sensor_info = info.get_sensor_long_name_and_units(device, ch)

		return enabled_sensor_info

	   
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
			config.logger.info("start() not executed due to no device, device handle, or sensors")
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

		# create a buffer for each active channel. For fast sampling there may be more than one value 
		# returned in a read(). One value is returned and the rest are stored in this buffer.
		buf.buffer_init()

		# start data collection
		start.start_measurements()						  

		
	def read(self, ch, device=0):
		""" Take single point readings from the desired channel.

		Args: 
			ch (str): Options include 'ch1', 'ch2', 'ch3', 'dig1', 'dig2'.  

			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1
		
		Returns:
			measurement: A single data point for the selected channel. 
		"""	  
		
		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			config.logger.info("read() not executed due to no device, device handle, or sensors")
			return		 
		
		measurement = read.get_measurement(device, ch)
		return measurement

	def read_multi_pt(self, ch, num_measurements_to_read, device=0):
		""" Take a specified number of multi-point readings from the selected channel. This
		only applies to analog sensors connected to ch1, ch2, or ch3.

		Args: 
			ch (str): Options include 'ch1', 'ch2', 'ch3'

			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1

			num_measurements_to_read (int):  number of samples to collect.

		Returns:
			measurements[]: a list containing the packet of data from each 
			configured sensor. The list will contain the number of measurements 
			asked for in the argument. 
		"""	  
		
		# if no devices, no device handle, or no sensors then exit this function
		if not config.device_type or not config.hDevice or not any(config.enabled_all_channels):
			config.logger.info("read_multi_pt() not executed due to no device, device handle, or sensors")
			return		 
		
		measurements = read.get_multi_pt_measurements(device, ch, num_measurements_to_read)

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
			config.logger.info("stop() not executed due to no device, device handle, or sensors")
			return	  

		# Stop the measurements and clear the ngio measurement buffer and the data buffer()
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

	
	def dcu(self, ch, value, device=0):
		""" Control the output lines of the DCU

		Args: 
			ch (str): Options include 'dig1' or 'dig2'

			value (int): send the DCU a value from 0-15 to turn lines on and off.
			
			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1
		"""
		
		dcu.set_io_line(ch, value, device)

	def dcu_pwm_dig1(self, frequency_Hz, duty_cycle, device=0):
		""" Control the DCU's PWM output, this occurs on the DCU's line D4. The DCU must be connected 
		to dig1 (PWM is not available on channel dig2)
		
		Args: 
			frequency_Hz (int): 2.5 Hz (0.4 sec period) to 1,000,000 Hz (1 microsecond period).

			duty_cycle (int):  set the duty cycle with a value of 0 to 100

			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1
		"""
		
		dcu.set_pwm(frequency_Hz, duty_cycle, device)


	def photogate_timing(self, ch, samples, timeout, device=0):
		"""Perform photogate timing

		Args: 
			ch (str): Options include 'dig1' or 'dig2'
			
			samples(int): number of timing samples to record

			timeout: (seconds) Maximum time to wait for all samples to be collected.

			device (int): If you have a single LabQuest connected, then device=0. 
			If you need to configure a second LabQuest device, then device=1

		Returns: 
			timing_values []: returns the photogate blocked time, unblocked time, 
			blocked time, unblocked time, etc..
		"""

		samples = samples + 2	# to get the number of samples requested, actually need 2 extra
		timeout = timeout/3   # the read takes 3x the timeout, so need to divide by 3 here
		timing_values = photo.get_photogate_timing(ch, samples, timeout, device)

		return timing_values
