"""
    This is a simple example script showing our GPS module
    
    @author: Chad Spensky
    @organization: MIT Lincoln Laboratory
    © 2015 Massachusetts Institute of Technology
"""

# CATAN
import catan.utils as utils
from catan.gps import GPSReceiver


if __name__ == "__main__":
    
    gps = GPSReceiver(serial_interface="/dev/ttyUSB1")
        
    while True:
        coords = gps.get_coordinates()
        
        print coords
        
        time = gps.get_time()
        
        if time is not None:
            print time.timetuple()
            utils.linux_set_time(time.timetuple())
        
