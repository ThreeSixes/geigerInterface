#!/usr/bin/python

###############
### Imports ###
###############

import u3
import time
import traceback
import argparse
from pprint import pprint

#####################################
### Flasgs and tunable parameters ###
#####################################

# Constants and tunable parameters
c_ct_slow = 22            # Number of samples in slow mode.
c_ct_fast = 4             # Number of samples in fast mode.

# Flags
f_accum = 0x01            # Bit position of accumulator flags. 
f_accum_accum = 0x00      # This flag means we're still accumulating data.
f_accum_complete = 0x01   # This flag means we have a full sample to average from.

f_trend = 0x06            # Bit position of the trend flag.
f_trend_stable = 0x00     # Stable readings.
f_trend_up     = 0x02     # Readings increasing.
f_trend_dn     = 0x04     # Readings decreasing.
f_trend_unk    = 0x06     # Not sure.

f_mode = 0x18             # Bit position of the mode flag.
f_mode_fast = 0x00        # Fast averaging mode.
f_mode_slow = 0x08        # Slow averaging mode.
f_mode_stream = 0x18      # Streaming mode.


#################
### Variables ###
#################

# Set default flags.
flags = f_accum_accum | f_trend_unk

# Hold samples.
samples = []

cpsOn = False # Show CPS?
flagsOn = False # Show flags?
averageOn = True # Show averages?
keepRunning = True # Keep running?
debugOn = False # Debug?

#######################
### Utility methods ###
#######################

def setFlag(whichFlag, whichValue):
    """
    Set a given flag to a given value.
    """
    global flags
    
    if debugOn == True:
        print("Flags in: %x" %flags)
    
    # Get temproary flag value that blanks out the flag.
    tFlag = (~whichFlag) & flags
    
    # Set our flag to the given value.
    flags = tFlag | whichValue
    
    if debugOn == True:
        print("Flags out: %x" %flags)
    
    return


def parseFlags():
    """
    Parse flags to a short string.
    """
    global flags
    
    # Blank return value.
    retVal = ""
    
    # Store flags as we parse them.
    allFlags = []
    
    # Get the accumulator flag.
    accFlag = flags & f_accum
    trendFlag = flags & f_trend
    modeFlag = flags & f_mode
    
    # Complete set of readings?
    if accFlag == f_accum_complete:
        # Completed loading values into the accumulator.
        allFlags.append('C')
    elif accFlag == f_accum_accum:
        # Still accumulating.
        allFlags.append('A')
    else:
        # Bad value.
        allFlags.append('!')
    
    # Trend?
    if (trendFlag) == f_trend_stable:
        # Readings stable.
        allFlags.append('S')
    elif (trendFlag) == f_trend_up:
        # Still accumulating.
        allFlags.append('U')
    elif (trendFlag) == f_trend_dn:
        # Still accumulating.
        allFlags.append('D')
    elif (trendFlag) == f_trend_unk:
        # Still accumulating.
        allFlags.append('?')
    else:
        # Bad value.
        allFlags.append('!')
    
    # Mode?
    if modeFlag == f_mode_fast:
        # Fast
        allFlags.append('F')
    elif modeFlag == f_mode_slow:
        # Slow
        allFlags.append('S')
    elif modeFlag == f_mode_stream:
        # Stream
        allFlasgs.append('T')
    else:
        # Bad value.
        allFlags.append('!')
    
    # Build a nice string.
    retVal = ''.join(allFlags)
    
    # Return value.
    return retVal

def parseTimeArg(timeStr):
    """
    Parse timer arguments. If we just see a number let's assume seconds. If there is an 'm' after the argument assume minutes.
    """
    
    # Number of seconds.
    retVal = 0
    
    
    
    return retVal


###########################
### Main execution body ###
###########################

# Set up command line interface.
parser = argparse.ArgumentParser(description = "Geiger counter interface", epilog = "Fast mode averages counts over a 4 second period, and slow mode averages counts over a 22 second period. This is modeled from the Ludlum model 3 geiger counter.")
parser.add_argument('--accumulate', action='store_true', help = 'Keep a sum of all detected counts.')
parser.add_argument('--cps', action='store_true', help = 'Show live counts per second.')
parser.add_argument('--debug', action='store_true', help = 'Debug')
parser.add_argument('--flags', action='store_true', help = 'Display flags.')
parser.add_argument('--mode', choices=['fast', 'slow', 'stream'], required = True, help = 'Set mode option. Fast averages over 4 sec., Slow averages over 22 sec. Stream mode implies --cps and does not average.')
parser.add_argument('--time', type = int, help = 'Time in seconds to run.')
args = parser.parse_args()

print("Counter start, mode is %s" %args.mode)

# Select sample count based on mode.
if args.mode == "fast":
    # Fast mode
    averageOn = True
    scount = c_ct_fast
    flags = flags | f_mode_fast
    
elif args.mode == "slow":
    # Slow mode.
    averageOn = True
    scount = c_ct_slow
    flags = flags | f_mode_slow
    
elif args.mode == "stream":
    # Stream mode
    averageOn = False
    cpsOn = True
    flags = flags | f_mode_stream
    
else:
    # This straight up shouldn't have happened. Crash and burn.
    raise RuntimeError("Invalid mode. This should not have happened.")

# If we have activated counts per second set the flag.
if args.cps == True:
    cpsOn = True

# Show flags?
if args.flags == True:
    flagsOn = True

# Should we debug?
if args.debug == True:
    debugOn = True

try:
    # Init the U3.
    d = u3.U3()
    
    # U3 protocol debug.
    d.debug = debugOn
    
    # Set up our I/O
    d.configIO(EnableCounter0 = True, TimerCounterPinOffset = 4, FIOAnalog = 15)
    
    while keepRunning:
        # Measure for 1 second
        time.sleep(1)
        
        # Snag results and reset counter.
        thisReading = d.getFeedback(u3.Counter0(Reset = True))
        
        if averageOn == True:
            # Make sure we have no more than the specified number of samples.
            del samples[(scount - 1):]
            
            # Prepend this reading.
            samples[:0] = thisReading
            
            curCount = len(samples)
            
            # Get our averages.
            average = sum(samples) / curCount
            
            # CPM
            cpm = average * 60
            
            # If we are accumulating...
            if flags & f_accum == f_accum_accum:
                # If we have enough counts flag it.
                if curCount == scount:
                    # We have enough readings.
                    setFlag(f_accum, f_accum_complete)
        
        # Dump the things we should dump.
        print("--")
        
        if flagsOn == True:
            flagStr = parseFlags()
            print("Flags: %s (0x%x)" %(flagStr, flags))
        
        if cpsOn == True:
            print("%s CPS" %thisReading[0])
        
        if averageOn == True:
            print("%s CPM" %cpm)
        
except KeyboardInterrupt:
    print("Caught keyboard interrupt. Quitting.")

except:
    # If we somehow screw the pooch...
    tb = traceback.format_exc()
    print("Unhandled exception:\n%s" %tb)

finally:
    try:
        d.close()
    
    except:
        tb = traceback.format_exc()
        print("Failed to close LabJack U3:\n%s" %tb)
