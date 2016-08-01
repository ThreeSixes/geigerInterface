###############
### Imports ###
###############

import u3
import traceback
from hwInterface import counterIface


#######################################
### LabJack U3 hareware abstraction ###
#######################################

class u3Hardware(counterIface):
	def setup(self):
		"""
		Set up and configure counter hardware interface
		"""
		
		# LabJack U3 settings..
		u3CounterOffset = 4
		u3FIOAnalog = 15
		
		try:
			# Create LabJack U3 object and set debugging.
			self.__u3 = u3.U3()
		
		except:
			raise
		
		if self._debug == True:
			print("Set up LabJack U3 with counter offset of %s and FIOAnalog of %s..." %(u3CounterOffset, u3FIOAnalog))
		
		try:
			# Configure LabJack U3
			self.__u3.configIO(EnableCounter0 = True, TimerCounterPinOffset = u3CounterOffset, FIOAnalog = u3FIOAnalog)
		
		except:
			raise
		
		return
	
	def getConfig(self):
		"""
		Get current LabJack U3 setup.
		"""
		
		retVal = {"desc": "LabJack U3"}
		
		try:
			# Get config metadata from the LabJack U3.
			retVal.update({"config": self.__u3.configU3()})
		
		except:
			raise
		
		return retVal
	
	def poll(self):
		"""
		Poll Counter0 on LabJack U3. Returns counts as an integer.
		"""
		
		# Return value.
		retVal = 0
		
		if self._debug == True:
			print("Poll counter hardware...")
		
		try:
			# Get results.
			retVal = self.__u3.getFeedback(u3.Counter0(Reset = True))[0]
		
		except:
			raise
		
		return retVal
	
	def cleanup(self):
		"""
		Do any necessary cleanup on the LabJack U3 before shutting down.
		"""
		
		if self._debug == True:
			print("Counter hardware cleanup...")
		
		try:
			# Reset the device before closing.
			self.__u3.reset(hardReset = True)
		
		except:
			raise
		
		finally:	
			try:
				# Close the device and free it up.
				self.__u3.close()
			
			except:
				raise
