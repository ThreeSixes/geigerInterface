class counterIface(object):
	def __init__(self):
		"""
		Template class to communicate with physical counter hardware. Override methods that the hardware requires.
		"""
		
		# Debug and text output flags.
		self._debug = False
		self._textOut = False
	
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

	def setup(self):
		"""
		Set up and configure counter hardware interface
		"""
		
		if self._debug == True:
			print("Punt: Set up counter hardware...")
		
		return
	
	def getConfig(self):
		"""
		Get current configuration of the hardware as a string.
		"""
		
		return "No hardware present."

	def start(self):
		"""
		Start the hardware counter.
		"""
		
		if self._debug == True:
			print("Punt: Start counter hardware...")
		
		return
	
	def poll(self):
		"""
		Poll the counter.
		"""
		
		if self._debug == True:
			print("Punt: Poll counter hardware...")
		
		return 0
	
	def stop(self):
		"""
		Stop the hardware counter.
		"""
		
		if self._debug == True:
			print("Punt: Stop counter hardware...")
		
		return
	
	def cleanup(self):
		"""
		Do any necessary cleanup on the hardware counter before shutting down.
		"""
		
		if self._debug == True:
			print("Punt: Counter hardware cleanup...")
		
		return

