import traceback
from hwInterface import counterIface

try:
	import serial
except:
	raise RuntimeError("To interface with the Arduino serial counter please ensure the python library pyserial is installed.")

class arduSerHardware(counterIface):	
	def setDebug(self, debugOn):
		"""
		Enable or disable debugging.
		"""
		
		print("Set debugging on: %s" %debugOn)
		
		if debugOn == True:
			self._debug = True
		
		else:
			self._debug = False
		
		return
	
	def setTextOut(self, textOut):
		"""
		Turn text output on or off.
		"""
		
		# Set the flag.
		if textOut == True:
			self._textOut = True
		else:
			self._textOut = False
		
		return

	def setSerialProps(self, dev, baud = 115200):
		"""
		Set serial properties. Accepts two arguments: dev, the device e.g. /dev/ttyACM0 and baud which is an integer representing the baud rate to use on the serial port the default is 115200.
		"""
		
		# Set the class-wide vars up for the I2C bus ID and target address.
		self.__serialPort = dev
		self.__serialBaud = baud
		
		if self._debug == True:
			print("Serial property set called. Port is %s, baud rate is %s." %(dev, baud))
		
		return


	def setup(self):
		"""
		Set up and configure counter hardware interface
		"""
		
		if self._debug == True:
			print("Set up Arduino counter hardware on serial port...")

		try:
			self.__serialPort
		
		except NameError:
			# Default to this because Arduinos show up as ttyACM0
			self.__serialPort = '/dev/ttyACM0'
			
			if self._debug == True:
				print("Serial port not specified. Defaulting to %s." %self.__serialPort)
		
		except:
			raise
		
		try:
			self.__serialBaud
		
		except NameError:
			# Which bus is this on?
			self.__serialBaud = 115200
			
			if self._debug == True:
				print("Baud rate not specified. Defaulting to %s." %self.__serialBaud)
		
		except:
			raise
		
		
		try:
			# Set up serial port object.
			self.__ser = serial.Serial(self.__serialPort, self.__serialBaud, timeout = 5)
		
		except:
			raise
		
		return


	def getConfig(self):
		"""
		Get current configuration of the hardware as a string.
		"""
		
		retVal = {
			"desc": "Arduino counter via serial",
			"config": {
					"device": self.__serialPort,
					"baudRate": self.__serialBaud
				}
			}
		
		return retVal

	def poll(self):
		"""
		Poll the counter.
		"""
		# Blank return value.
		retVal = 0
		
		# We don't have the droids/line we're looking for...
		noLine = True
		
		if self._debug == True:
			print("Poll counter hardware...")
		
		# Keep going until we get a line we want...
		while noLine:
			try:
				# Wait for a line we're interested in...
				thisLine = self.__ser.readline()
				
				# See if we can find he CPS line.
				foundAt = thisLine.find("CPS: ")
				
				# Nailed it!
				if foundAt == 0:
					# Got a CPM message.
					noLine = False
			
			except:
				raise
		
		try:
			# Make sure we properly type-convert our counts per second.
			parts = thisLine.split(" ")
			
			# Try to grab the number coming across as an integer.
			retVal = int(parts[1])
		
		except:
			raise
		
		return retVal

	def cleanup(self):
		"""
		Do any necessary cleanup on the hardware counter before shutting down.
		"""
		
		if self._debug == True:
			print("Counter hardware cleanup...")
		
		try:
			# Close the serial port.
			self.__ser.close()
		
		except:
			if self._debug == True:
				tb = traceback.format_exc()
				print("Failed to close Arduino serial port:\n%s" %tb)
		
		return