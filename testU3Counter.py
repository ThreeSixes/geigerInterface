#!/usr/bin/python

import u3
import time
import traceback

try:
    # Init the U3.
    d = u3.U3()
    
    # U3 protocol debug.
    #d.debug = True
    
    # Set up our I/O
    d.configIO(EnableCounter0 = True, TimerCounterPinOffset = 4, FIOAnalog = 15)
    
    while True:
        # Measure for 1 second
        time.sleep(1)
        
        # Snag results and reset counter.
        x = d.getFeedback(u3.Counter0(Reset = True))
        
        # Get on-the-fly CPS and CPM values.
        cps = x[0]
        cpm = x[0] * 60
        
        # Dump them.
        print("--")
        print("%s CPS" %cps)
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
