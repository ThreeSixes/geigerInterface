#!/usr/bin/python

###############
### Imports ###
###############

import datetime
import time
import traceback

############################
### Master counter class ###
############################

class geigerInterface():
    def __init__(self, hwPlatform, mode = "class", cps = False, flags = False, debug = False, quiet = False, time = 0):
        """
        Geiger counter interface class. Madatory arguments are mode and hwPlatform, which should be an instance or child object of counterIface.
        """
        
        # Constants and tunable parameters
        self.__c_ct_slow = 22            # Number of samples in slow mode.
        self.__c_ct_fast = 4             # Number of samples in fast mode.
        
        # Flags
        self.f_accum = 0x01            # Bit position of accumulator flags. 
        self.f_accum_accum = 0x00      # This flag means we're still accumulating data.
        self.f_accum_complete = 0x01   # This flag means we have a full sample to average from.
        
        self.f_trend = 0x06            # Bit position of the trend flag.
        self.f_trend_stable = 0x00     # Stable readings.
        self.f_trend_up     = 0x02     # Readings increasing.
        self.f_trend_dn     = 0x04     # Readings decreasing.
        self.f_trend_unk    = 0x06     # Not sure.
        
        self.f_mode = 0x18             # Bit position of the mode flag.
        self.f_mode_fast = 0x00        # Fast averaging mode.
        self.f_mode_slow = 0x08        # Slow averaging mode.
        self.f_mode_stream = 0x10      # Streaming mode.
        self.f_mode_roll = 0x18        # Rolling mode.
        
        
        # Set up hardware.
        self.__hw = hwPlatform
        
        # Set default flags.
        self.__flags = self.f_trend_unk
        
        # Hold samples.
        self.__samples = []
        
        # Set mode.
        self.__mode = mode
        
        self.__cpsOn = False # Show CPS?
        self.__flagsOn = False # Show flags?
        self.__debugOn = False # Debug?
        self.__liveOutput = True # Do we dump data in real time?
        self.__runtime = 0 # How long have we been running?
        self.__accumCts = 0 # How many counts do we have?        
        self.__timed = False # Are we running in timed mode?
        self.__timeLimit = 0 # What is our time limit
        self.__textOut = True # By default we are quiet.
        
        # Printed timestamp format.
        self.__tsFormat = '%Y-%m-%d %H:%M:%S.%f UTC'
        
        # Set mdoe.
        self.__mode = mode
        
        # If we have activated counts per second set the flag.
        if cps == True:
            self.__cpsOn = True
        
        # Show flags?
        if flags == True:
            self.__flagsOn = True
        
        # Should we debug?
        if debug == True:
            self.__hw.setDebug(True)
            self.__debugOn = True
        
        # Live output?
        if quiet == True:
            self.__textOut = False
        
        # Timer?
        if time > 0:
            self.__timed = True
            self.__timeLimit = time
    
    def __liveCountPrint(self, cps):
        """
        Print data from all 'live' modes that print data as it comes in. cps should be a float.
        """
        
        try:
            # If we're set up to print things besides debug statements in the first place...
            if self.__textOut == True:
            
                # First we get CPM since we always use it.
                cpm = cps * 60.0
                
                # Dump the things we should dump.
                print("--")
                
                if self.__flagsOn == True:
                    flagStr = self.parseFlags()
                    print("Flags: %s (0x%x)" %(flagStr, self.__flags))
                    
                if self.__cpsOn == True:
                    print("%s CPS" %round(cps, 3))
                            
                print("%s CPM" %round(cpm, 3))
        
        except:
            raise
        
        return
    
    def __parseTimeArg(self, timeStr):
        """
        Parse timer arguments. If we just see a number let's assume seconds. If there is an 'm' after the argument assume minutes.
        """
        
        # Number of seconds.
        retVal = 0
        
        ### NOT YET IMPLEMENTED. NEEDS TO BE DONE!
        
        
        return retVal
    
    def bufferAvg(self, thisReading, smplBuffSz):
        """
        Handle buffered averaging, where the buffer contains up to smplBuffSz samples, and the newest reading is thisReading. Returns the average of the buffer.
        This method is used by both modeFast() and modeSlow() - the difference being different smplBuffSz values.
        """
        
        # Default return value is zero.
        retVal = 0
        
        
        try:
            # Make sure we have no more than the specified number of samples.
            del self.__samples[(smplBuffSz - 1):]
            
            # Prepend this reading.
            self.__samples[:0] = [thisReading]
            
            # Get the number of samples.
            curCount = len(self.__samples)
            
            # Get our averages.
            retVal = float(sum(self.__samples)) / float(curCount)
            
            # Do we have a full buffer?
            if curCount == smplBuffSz:
                # Set complete flag.
                self.setFlag(self.f_accum, self.f_accum_complete)
            
            else:
                # Set accumulator flag.
                self.setFlag(self.f_accum, self.f_accum_accum)
        except:
            raise
        
        return retVal
    
    def modeFast(self, latestCount):
        """
        Fast mode handler. Stores up to 4 seconds worth of data in a buffer and averages those samples.
        """
        
        try:
            # Handle counts.
            avg = self.bufferAvg(latestCount, self.__c_ct_fast)
            
            # Print the things.
            self.__liveCountPrint(avg)
            
            # Store the things.
            ### NOT YET IMPLEMENTED.
        
        except:
            raise
        
        return
    
    def modeSlow(self, latestCount):
        """
        Slow mode handler. Stores up to 22 seconds worth of data in a buffer and averages those samples.
        """
        
        try:
            # Handle counts.
            avg = self.bufferAvg(latestCount, self.__c_ct_fast)
            
            # Print the things.
            self.__liveCountPrint(avg)
            
            # Store the things.
            ### NOT YET IMPLEMENTED.
        
        except:
            raise
        
        return
    
    def modeStream(self, latestCount):
        """
        Continuously print counts on the screen without averaging until the program is killed or runs out of time.
        """
        try:
            # Print the things.
            self.__liveCountPrint(latestCount)
            
            # Store the things.
            ### NOT YET IMPLEMENTED.
            
        except:
            raise
        
        return
    
    def modeRoll(self, latestCount):
        """
        Take samples continuously and keep running until the program is killed or runs out of time.
        """
        
        try:
            # Accumulate new sample data.
            self.__accumCts += latestCount
            
            # Increment runtime counter.
            self.__runtime += 1
        
        except:
            raise
        
        return

    def setFlag(self, whichFlag, whichValue):
        """
        Set a given flag to a given value.
        """
        
        try:
            if self.__debugOn == True:
                print("Flags in: %x" %self.__flags)
            
            # Get temproary flag value that blanks out the flag.
            tFlag = (~whichFlag) & self.__flags
            
            # Set our flag to the given value.
            self.__flags = tFlag | whichValue
            
            if self.__debugOn == True:
                print("Flags out: %x" %self.__flags)
        
        except:
            raise
        
        return
    
    
    def parseFlags(self):
        """
        Parse flags to a short string.
        """
        # Blank return value.
        retVal = ""
        
        try:
            # Store flags as we parse them.
            allFlags = []
            
            # Get the accumulator flag.
            accFlag = self.__flags & self.f_accum
            trendFlag = self.__flags & self.f_trend
            modeFlag = self.__flags & self.f_mode
            
            # Complete set of readings?
            if accFlag == self.f_accum_complete:
                # Completed loading values into the accumulator.
                allFlags.append('C')
            elif accFlag == self.f_accum_accum:
                # Still accumulating.
                allFlags.append('A')
            else:
                # Bad value.
                allFlags.append('!')
            
            # Trend?
            if (trendFlag) == self.f_trend_stable:
                # Readings stable.
                allFlags.append('S')
            elif (trendFlag) == self.f_trend_up:
                # Still accumulating.
                allFlags.append('U')
            elif (trendFlag) == self.f_trend_dn:
                # Still accumulating.
                allFlags.append('D')
            elif (trendFlag) == self.f_trend_unk:
                # Still accumulating.
                allFlags.append('?')
            else:
                # Bad value.
                allFlags.append('!')
            
            # Mode?
            if modeFlag == self.f_mode_fast:
                # Fast
                allFlags.append('F')
            elif modeFlag == self.f_mode_slow:
                # Slow
                allFlags.append('S')
            elif modeFlag == self.f_mode_stream:
                # Stream
                allFlasgs.append('T')
            else:
                # Bad value.
                allFlags.append('!')
            
            # Build a nice string.
            retVal = ''.join(allFlags)
            
        
        except:
            raise
        
        # Return value.
        return retVal
    
    def runCli(self):        
        # Select sample count based on mode.
        if self.__mode == "fast":
            # Fast mode
            self.__flags = self.__flags | self.f_mode_fast
                    
            # Run with fast mode callback.
            self.run(self.modeFast)
            
        elif self.__mode == "slow":
            # Slow mode.
            self.__flags = self.__flags | self.f_mode_slow
            
            # Run with slow mode callback.
            self.run(self.modeSlow)
            
        elif self.__mode == "stream":
            # Stream mode
            self.__flags = self.__flags | self.f_mode_stream
            
            # Run with stream mode callback.
            self.run(self.modeStream)
        
        elif self.__mode == "roll":
            # Rolling mode. Keeps adding counts until the program is killed.
            self.__flags = self.__flags | self.f_mode_roll
            
            # Run with roll mode callback.
            self.run(self.modeRoll)
        
        else:
            # This straight up shouldn't have happened. Crash and burn.
            raise RuntimeError("Invalid mode specified. Should be a string containing one of the following for CLI mode: fast, slow, stream, roll")
    
    def run(self, callBack):
        """
        Run the counter. Every time a sample is taken the callback method is called.
        """
        
        # Flag keeprunning as true.
        self.__keepRunning = True
        
        try:
            # Set up our hardware interface.
            self.__hw.setup()
            
            # Get config.
            devConfig = self.__hw.getConfig()
            
            if self.__textOut == True:
                print("Counter hardware platform is %s." %devConfig['desc'])
            
            if self.__debugOn == True:
                print("Hardware config information:\n%s" %devConfig['config'])
            
            # When are we starting?
            self.__dtsStart = datetime.datetime.utcnow()
            
            # In case we bomb out make sure we have some sort of end DTS.
            self.__dtsEnd = self.__dtsStart
            
            if self.__textOut == True:
                # Print start time
                print("Start time: %s" %self.__dtsStart.strftime(self.__tsFormat))
            
            while self.__keepRunning:
                try:
                    # Measure for 1 second
                    time.sleep(1)
                    
                    # Snag counter results.
                    thisReading = self.__hw.poll()
                    
                    # Execute our callback with the current reading.
                    callBack(thisReading)
                    
                    # If we're in timed mode make sure we haven't exceeded our runtime.
                    if self.__timed == True:
                        # If we've hit our time limit this cycle stop the loop.
                        if self.__runtime == self.__timeLimit:
                            self.keepRunning = False
                
                except:
                    # Stop the loop.
                    self.__keepRunning = False
                    
                    # Pass the exception up the stack.
                    raise
            
            # When are we starting?
            self.__dtsEnd = datetime.datetime.utcnow()
            
            # Stop the harware counter.
            self.__hw.stop()
        
        except:
            raise
        
        finally:
            if self.__textOut == True:
                print("Run statistics:")
                
                # Print start time
                print("Start time: %s" %self.__dtsStart.strftime(self.__tsFormat))
                
                # Print end time
                print("End time: %s" %self.__dtsEnd.strftime(self.__tsFormat))
                
                # Store the things.
                ### NOT YET IMPLEMENTED.
                
                # If we're in rolling mode make sure we give final stats after the program is killed.
                if (self.__flags & self.f_mode) == self.f_mode_roll:
                    # Make sure we don't divide by zero.
                    if self.__runtime > 0:
                        # Average counts over our run time...
                        avgCts = float(self.__accumCts) / float(self.__runtime)
                        
                        # CPS -> CPM.
                        finalCpm = avgCts * 60.0
                        
                        print("Total counts %s in %s sec." %(self.__accumCts, self.__runtime))
                        print("Avg CPM over %s sec: %s" %(self.__runtime, round(finalCpm, 3)))
                        
                        # If we want stats in counts per second as well...
                        if self.__cpsOn == True:
                            print("Avg CPS over %s sec: %s" %(self.__runtime, round(avgCts, 3)))
                        
                    else:
                        raise runtimeError("We ran for < 1 sec., not averaging data.")
                
            try:
                # Clean up the hardware interface.
                self.__hw.cleanup()
            
            except:
                raise
    

#######################
# Main execution body #
#######################

if __name__ == "__main__":
    import argparse

    # Set up command line interface.
    parser = argparse.ArgumentParser(description = "Geiger counter interface", epilog = "Fast mode averages counts over a 4 second period, and slow mode averages counts over a 22 second period. This is modeled from the Ludlum model 3 geiger counter. It is intended that this program get support for storing data to files.")
    parser.add_argument('--accumulate', action='store_true', help = 'Keep a sum of all detected counts.')
    parser.add_argument('--cps', action='store_true', help = 'Show live counts per second.')
    parser.add_argument('--hw', choices=['dummy', 'random', 'u3'], required = True, help = 'Set counter hardware platform. The choices are "dummy" which does nothing, "random" which generates random numbers, and "u3" for a LabJack U3.')
    parser.add_argument('--debug', action='store_true', help = 'Debug')
    parser.add_argument('--flags', action='store_true', help = 'Display flags.')
    parser.add_argument('--mode', choices=['fast', 'slow', 'stream', 'roll'], required = True, help = 'Set mode option. Fast averages samples over 4 sec., Slow averages samples over 22 sec. Stream mode implies --cps and does not average. Roll mode keeps adding an average as long as it runs, and dumps stats at the end. Roll mode also implies --quiet.')
    parser.add_argument('--time', type = int, help = 'Time in seconds to run.')
    parser.add_argument('--quiet', action='store_true', help = 'Minimal command line output.')
    args = parser.parse_args()
    
    if args.quiet == False:
        print("Counter start, mode is %s" %args.mode)
    
    # Which hardware platform do we have?
    if args.hw == "u3":
        # We have a LabJack U3.
        import u3Hardware
        hwPlat = u3Hardware.u3Hardware()
    
    elif args.hw == "dummy":
        # We have a dummy class that will just read zeroes.
        import hwInterface
        hwPlat = hwInterface.counterIface()
    
    elif args.hw == "random":
        # Use the random number generator.
        import rndHardware
        hwPlat = rndHardware.rndHardware()
    
    try:
        # Set up geiger counter object.
        ctr = geigerInterface(hwPlat, args.mode, cps = args.cps, flags = args.flags, debug = args.debug, quiet = args.quiet, time = args.time)
        
        # Run the geiger counter.
        ctr.runCli()
    
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Quitting.")
    
    except:
        tb = traceback.format_exc()
        print("Caught unhandled exception:\n%s" %tb)