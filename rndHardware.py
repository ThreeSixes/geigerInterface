###############
### Imports ###
###############

import random
import traceback
from hwInterface import counterIface


#######################################
### LabJack U3 hareware abstraction ###
#######################################

class rndHardware(counterIface):
	def setup(self):
		"""
		Set up and configure counter hardware interface
		"""
		
		# Set random min and max.
		self.__rndMin = 0
		self.__rndMax = 500
		
		# Set up random number generator.
		self.__rnd = random.Random()
		self.__rnd.seed()
		
		return
	
	def getConfig(self):
		"""
		Get current config.
		"""
		
		return {"desc": "Python PRNG", "config": {"randomMin": self.__rndMin, "randomMax": self.__rndMax}}

	def poll(self):
		"""
		Random number generator
		"""
		
		return self.__rnd.randrange(self.__rndMin, self.__rndMax) 