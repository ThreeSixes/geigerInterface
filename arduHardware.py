import traceback
from hwInterface import counterIface


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
			import serial
		except:
			raise RuntimeError("To interface with the Arduino serial counter please ensure the python library pyserial is installed.")
			
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
				raise
		
		return


class arduI2cHardware(counterIface):	
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

	def setI2cProps(self, i2cBusID = 1, targetI2cAddr = 0x35):
		"""
		Set I2C properties. Accepts two optional arguments: the I2C bus ID set by 'i2cBusID' which defaults to 1, and 'targetI2cAddr' which defaults to 0x35.
		The target address property should match the one in geigerInterface.ino, and the i2cBusID can be found using i2cdetect -y [0....n] where 0....n are numbers from 0 to n that represent individual I2C buses attached to a system. On newer Raspberry Pis it's 1 which is where we derive the default.
		"""
		
		# Set the class-wide vars up for the I2C bus ID and target address.
		self.__i2cBus = i2cBusID
		self.__i2cAddr = targetI2cAddr
		
		if self._debug == True:
			print("I2C property set called. I2C bus ID is %s, target address is %s." %(i2cBusID, hex(targetI2cAddr)))
		
		return

	def setup(self):
		"""
		Set up and configure counter hardware interface
		"""
		
		# Use threading.
		import threading
		
		# Keep track of the last CPS reading.
		self.__lastReading = 0
		
		if self._debug == True:
			print("Set up Arduino counter hardware on I2C bus...")
		
		try:
			import quick2wire.i2c as qI2c
		
		except:
			raise RuntimeError("To interface with the Arduino 16-bit I2C counter please ensure the python library quick2wire is installed.")
		
		try:
			self.__myAddr
		
		except NameError:
			self.__i2cAddr = 0x35
			
			if self._debug == True:
				print("I2C address not specified. Defaulting to %s." %hex(self.__i2cAddr))
		
		except:
			raise
		
		try:
			self.__i2cBus
		
		except NameError:
			# Which bus is this on?
			self.__i2cBus = 1
			
			if self._debug == True:
				print("I2C bus ID not specified. Defaulting to %s." %self.__i2cBus)
		except:
			raise
		
		try:
			# Set up I2C master.
			self.__i2cMaster = qI2c.I2CMaster(self.__i2cBus)
		
		except:
			raise
		
		return
	
	def getConfig(self):
		"""
		Get current configuration of the hardware as a string.
		"""
		
		retVal = {
			"desc": "Arduino counter via I2C",
			"config": {
					"i2cBusID": self.__i2cBus,
					"i2cAddr": self.__i2cAddr
				}
			}
		
		return retVal
	
	def __pollwerThread(self):
		"""
		Continuously scan for new CPS data.
		"""
		
		
		
		return
	
	def poll(self):
		"""
		Poll the counter.
		"""
		# Blank return value.
		retVal = 0
		
		if self._debug == True:
			print("Poll counter hardware...")
		
		try:
			# Get I2C transaction data.
			counterReturn = self.__i2cMaster.transaction(self.__i2c.reading(self.__i2cAddr, 2))
		
		except:
			raise
		
		try:
			#TESTME: Actually test this when test hardware is set up.
			counterBytes = bytearray(counterReturn[0])
			
			# Build the 16 bit integer from the counter bytes.
			retVal = (counterBytes[0] << 8) | counterBytes[1]
		except:
			raise
		
		return retVal