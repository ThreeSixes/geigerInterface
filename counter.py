#!/usr/bin/python

###############
### Imports ###
###############

import time
import traceback
import datetime


############################
### Master counter class ###
############################




class geigerInterface():
    def __init__(self, mode, hwPlatform, cps = False, flags = False, debug = False, quiet = False, time = 0):
        """
        Geiger counter interface class. Madatory arguments are mode and hwPlatform, which should be an instance or child object of counterIface.
        """
        
        # Constants and tunable parameters
        self.c_ct_slow = 22            # Number of samples in slow mode.
        self.c_ct_fast = 4             # Number of samples in fast mode.
        
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
        self.flags = self.f_accum_accum | self.f_trend_unk
        
        # Hold samples.
        self.samples = []
        
        self.cpsOn = False # Show CPS?
        self.flagsOn = False # Show flags?
        self.averageOn = True # Show averages?
        self.debugOn = False # Debug?
        self.liveOutput = True # Do we dump data in real time?
        self.scount = 0
        self.runtime = 0 # How long have we been running?
        self.accumCts = 0 # How many counts do we have?
        self.timed = False # Are we running in timed mode?
        self.timeLimit = 0 # What is our time limit
        
        # Select sample count based on mode.
        if mode == "fast":
            # Fast mode
            self.averageOn = True
            self.scount = self.c_ct_fast
            self.flags = self.flags | self.f_mode_fast
            
        elif mode == "slow":
            # Slow mode.
            self.averageOn = True
            self.scount = self.c_ct_slow
            self.flags = self.flags | self.f_mode_slow
            
        elif mode == "stream":
            # Stream mode
            self.averageOn = False
            self.cpsOn = True
            self.flags = self.flags | self.f_mode_stream
        
        elif mode == "roll":
            # Rolling mode. Keeps adding counts until the program is killed.
            self.averageOn = False
            self.cpsOn = False
            self.flags = self.flags | self.f_mode_roll
            self.liveOutput = False
            
        else:
            # This straight up shouldn't have happened. Crash and burn.
            raise RuntimeError("Invalid mode. Should be a string containing one of the following: fast, slow, stream, roll")
        
        # If we have activated counts per second set the flag.
        if cps == True:
            self.cpsOn = True
        
        # Show flags?
        if flags == True:
            self.flagsOn = True
        
        # Should we debug?
        if debug == True:
            self.__hw.setDebug(True)
            self.debugOn = True
        
        # Live output?
        if quiet == True:
            self.liveOutput = False
        
        # Timer?
        if time > 0:
            self.timed = True
            self.timeLimit = time


    def setFlag(self, whichFlag, whichValue):
        """
        Set a given flag to a given value.
        """
        
        if self.debugOn == True:
            print("Flags in: %x" %self.flags)
        
        # Get temproary flag value that blanks out the flag.
        tFlag = (~whichFlag) & self.flags
        
        # Set our flag to the given value.
        self.flags = tFlag | whichValue
        
        if self.debugOn == True:
            print("Flags out: %x" %self.flags)
        
        return
    
    
    def parseFlags(self):
        """
        Parse flags to a short string.
        """
        # Blank return value.
        retVal = ""
        
        # Store flags as we parse them.
        allFlags = []
        
        # Get the accumulator flag.
        accFlag = self.flags & self.f_accum
        trendFlag = self.flags & self.f_trend
        modeFlag = self.flags & self.f_mode
        
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
        n
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
        
        # Return value.
        return retVal
    
    def parseTimeArg(self, timeStr):
        """
        Parse timer arguments. If we just see a number let's assume seconds. If there is an 'm' after the argument assume minutes.
        """
        
        # Number of seconds.
        retVal = 0
        
        
        
        return retVal
    
    
    def run(self):
        """
        Run the counter.
        """
        
        # Flag keeprunning as true.
        keepRunning = True
        
        try:
            # Set up our hardware interface.
            self.__hw.setup()
            
            # Get config.
            devConfig = self.__hw.getConfig()
            
            print("Counter hardware platform is %s." %devConfig['desc'])
            
            if self.debugOn == True:
                print("Hardware config information:\n%s" %devConfig['config'])
            
            # Start hardware interface...
            self.__hw.start()
            
            while keepRunning:
                try:
                    # Measure for 1 second
                    time.sleep(1)
                    
                    # Snag counter results.
                    thisReading = self.__hw.poll()
                    
                    # Get mode flags.
                    modeFlg = self.flags & self.f_mode
                    
                    # If we're in rolling mode increment the runtime.
                    if  modeFlg == self.f_mode_roll:
                        # Roll accumulator.
                        self.accumCts += thisReading
                    
                    # If we're in rolling or timer mode...
                    if (modeFlg == self.f_mode_roll) or (self.timed == True):
                        # Increment timer.
                        self.runtime += 1
                    
                    # Are we averaging?
                    if self.averageOn == True:
                        # Make sure we have no more than the specified number of samples.
                        del self.samples[(self.scount - 1):]
                        
                        # Prepend this reading.
                        self.samples[:0] = [thisReading]
                        
                        # Get the number of samples.
                        curCount = len(self.samples)
                        
                        # Get our averages.
                        average = float(sum(self.samples)) / float(curCount)
                        
                        # CPM
                        cpm = average * 60.0
                        
                        # If we are accumulating...
                        if self.flags & self.f_accum == self.f_accum_accum:
                            # If we have enough counts flag it.
                            if curCount == self.scount:
                                # We have enough readings.
                                self.setFlag(self.f_accum, self.f_accum_complete)
                
                    # If we weant to output text live:   
                    if self.liveOutput == True:
                        # Dump the things we should dump.
                        print("--")
                        
                        if self.flagsOn == True:
                            flagStr = self.parseFlags()
                            print("Flags: %s (0x%x)" %(flagStr, self.flags))
                        
                        if self.cpsOn == True:
                            print("%s CPS" %thisReading)
                        
                        if self.averageOn == True:
                            print("%s CPM" %round(cpm, 3))
                
                    # If we're in timed mode make sure we haven't exceeded our runtime.
                    if self.timed == True:
                        # If we've hit our time limit this cycle stop the loop.
                        if self.runtime == self.timeLimit:
                            keepRunning = False
                
                except:
                    # Stop the loop.
                    keepRunning = False
                    
                    # Pass the exception up the stack.
                    raise
            
            # Stop the harware counter.
            self.__hw.stop()
            
        except KeyboardInterrupt:
            print("Caught keyboard interrupt. Quitting.")
        
        except:
            # If we somehow screw the pooch...
            tb = traceback.format_exc()
            print("Unhandled exception:\n%s" %tb)
        
        finally:
            # If we're in rolling mode make sure we give final stats after the program is killed.
            if (self.flags & self.f_mode) == self.f_mode_roll:
                # Make sure we don't divide by zero.
                if self.runtime > 0:
                    # Average counts over our run time...
                    avgCts = float(self.accumCts) / float(self.runtime)
                    
                    # CPS -> CPM.
                    finalCpm = avgCts * 60.0
                    
                    print("Total counts %s in %s sec." %(self.accumCts, self.runtime))
                    print("Avg CPM over %s sec: %s" %(self.runtime, round(finalCpm, 3)))
                    
                    # If we want stats in counts per second as well...
                    if self.cpsOn == True:
                        print("Avg CPS over %s sec: %s" %(self.runtime, round(avgCts, 3)))
                    
                else:
                    print("We ran for < 1 sec., not averaging data.")
            
            try:
                # Clean up the hardware interface.
                self.__hw.cleanup()
            
            except:
                tb = traceback.format_exc()
                print("Failed to close LabJack U3:\n%s" %tb)
    

#######################
# Main execution body #
#######################

if __name__ == "__main__":
    import argparse

    # Set up command line interface.
    parser = argparse.ArgumentParser(description = "Geiger counter interface", epilog = "Fast mode averages counts over a 4 second period, and slow mode averages counts over a 22 second period. This is modeled from the Ludlum model 3 geiger counter. It is intended that this program get support for storing data to files.")
    parser.add_argument('--accumulate', action='store_true', help = 'Keep a sum of all detected counts.')
    parser.add_argument('--cps', action='store_true', help = 'Show live counts per second.')
    parser.add_argument('--hw', choices=['dummy', 'u3'], required = True, help = 'Set counter hardware platform. The choices are "dummy" which does nothing and "u3" for a LabJack U3.')
    parser.add_argument('--debug', action='store_true', help = 'Debug')
    parser.add_argument('--flags', action='store_true', help = 'Display flags.')
    parser.add_argument('--mode', choices=['fast', 'slow', 'stream', 'roll'], required = True, help = 'Set mode option. Fast averages samples over 4 sec., Slow averages samples over 22 sec. Stream mode implies --cps and does not average. Roll mode keeps adding an average as long as it runs, and dumps stats at the end. Roll mode also implies --quiet.')
    parser.add_argument('--time', type = int, help = 'Time in seconds to run.')
    parser.add_argument('--quiet', action='store_true', help = 'Minimal command line output.')
    args = parser.parse_args()
    
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
    
    ctr = geigerInterface(args.mode, hwPlat, cps = args.cps, flags = args.flags, debug = args.debug, quiet = args.quiet, time = args.time)
    
    ctr.run()