"""
    These are some basic utils utilized throughout our codebase.
    
    @author: Chad Spensky
    @organization: MIT Lincoln Laboratory
    © 2015 Massachusetts Institute of Technology
"""

def linux_set_time(time_tuple):
    """
        Set the system time, based on a datetime tuple.
        
        Credit: http://stackoverflow.com/questions/12081310/python-module-to-change-system-date-and-time
    """
    import sys
    import datetime
    import ctypes
    import ctypes.util
    import time

    # /usr/include/linux/time.h:
    #
    # define CLOCK_REALTIME                     0
    CLOCK_REALTIME = 0

    # /usr/include/time.h
    #
    # struct timespec
    #  {
    #    __time_t tv_sec;            /* Seconds.  */
    #    long int tv_nsec;           /* Nanoseconds.  */
    #  };
    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]

    librt = ctypes.CDLL(ctypes.util.find_library("rt"))

    ts = timespec()
    ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
    ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

    # http://linux.die.net/man/3/clock_settime
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))
    
    
def count_ones(bitmask):
    """
        Count the number of ones (hops) in our bitmask
        
        @param bitmask: bitmask of node ids in our path.
    """
    ones = 0
    while bitmask != 0:
        # Check if least significant bit is 1
        if bitmask & 1 == 1:
            ones += 1
        # Shift over 1
        bitmask >>= 1
        
    return ones
    
    
def import_config(filename):
    """
        Import our configuration from a file
        
        @param filename: Filename to importat as our configuration
        
        @return: Configuation class (Similar to class returned by argparse 
    """
    # Just want to return everything as a class
    class Config:
        debug = False
        def __init__(self, **entries): 
            self.__dict__.update(entries)
        
    # Open our config file
    import ConfigParser
    c_parser = ConfigParser.SafeConfigParser()
    c_parser.read(filename)
    
    # read everything into a dict
    config_dict = {}
    for section in c_parser.sections():
        
        for item in c_parser.items(section):
            config_dict[item[0]] = item[1]
    
    # Initialize and object from our dict
    args = Config(**config_dict)
    
    # Cast appropriate params
    args.node_id = int(args.node_id)
    if args.debug == "0":
        args.debug = False
    
    return args
