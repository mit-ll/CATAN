# © 2015 Massachusetts Institute of Technology

import sys
import os
import serial

def main():
    if len(sys.argv) > 1:
        #get the name of the 
        ser_name = sys.argv[1]
        try:
            ser = serial.Serial(ser_name, 9600, rtscts=True)
            ser.timeout = .01
        except OSError as err:
           print err
           print "Couldn't open serial connection"
           exit(1)
        except serial.serialutil.SerialException as err:
           print err
           exit(1)

        #set radio to KISS mode
        ser.write("kiss on\r\n"); 
        ser.readlines();
        ser.write("restart\r\n");
        ser.readlines();

        ser.write("kiss on\r\n"); 
        out1 = ser.readlines();
        ser.write("restart\r\n");
        out2 = ser.readlines();

	#if successful the second time set the kiss mode to on
        # we should not get any response from the read operation
	if not out1:
            print "Kiss mode set for "+ser_name
            exit(0)
        else:
            print "ERROR setting KISS mode for "+ser_name
            exit(1)

    else:
        print "Usage: %s <serial_port>" % sys.argv[0]
        exit(1)

if __name__ == "__main__":
    main()
