###############
### Imports ###
###############

import datetime

###############
### Imports ###
###############

class datalayer:
    def __init__(self, storageMode, counterMode):
        """
        Data layer for autoGeiger. Supports data storage.
        """
        
        # Store operational mode parameters.
        self.__stgMode = storageMode
        self.__ctrMode = counterMode
        
        # Set parameters as needed.
        if storageMode == "csv":
            # Create a default file name in case we don't have one specified.
            self.__fileName = "geiger-%s.csv" %datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S")
            self.__file = None # Don't open the file for appending yet... we might change the file name before storing a data point.
    
    def __del__(self):
        """
        Destructor.
        """
        
        # If we are storing a CSV file...
        if self.__stgMode == 'file':
            try:
                # Make our best effort to close said file...
                self.__file.close()
            except:
                # Don't care if the file can't be closed.
                None
            
    
    def __appendCsv(self, dataPoint):
        """
        Append datapoint to the CSV file.
        """
        
        try:
            # If we don't have a file to work with yet open it for writing.
            if self.__file == None:
                # Create file object.
                self.__file = open(self.__fileName, 'a')
            
            # Append the entry to the file.
            self.__file.write("\"%s\", %s\n" %(dataPoint[0].strftime("%Y-%m-%d %H:%M:%S"), dataPoint[1]))
        
        except:
            raise
    
    def setStorageProps(self, properties):
        """
        Set data storage properties.
        """
        
        # Are we in csv mode?
        if self.__stgMode == "csv":
            try:
                # Try to set fileName as this is the only parameter we expect.
                self.__fileName = properties['fileName']
            except:
                None
    
    def storeDatapoint(self, dataPoint):
        """
        Store a given datapoint. Accepts a tuple with a date and a count.
        """
        
        # If we're in CSV mode attempt to add a line to the CSV file.
        if self.__stgMode == "csv":
            # Give it a shot...
            try:
                self.__appendCsv(dataPoint)
            
            except:
                raise