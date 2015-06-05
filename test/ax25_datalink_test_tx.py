# © 2015 Massachusetts Institute of Technology

import sys
import serial
import logging
logger = logging.getLogger(__name__)
import time

from catan.datalink import AX25_KISS_Transmitter

      
def main():
    if len(sys.argv) > 1:
        myport = sys.argv[1]
    else: 
        print "Usage: %s PORT" % sys.argv[0]
        exit(1)
        
    try:
        transmitter = AX25_KISS_Transmitter(callfrom="KI4SNH-1", port=myport)
    except serial.SerialException as e:
        print e
        exit(1)

    logging.basicConfig(level=logging.INFO)
    N = 240
    d = 0
    transmitter.send("start")
    time.sleep(d)
    for i in range(0x41, 0x41 + 20):
        print "run "+chr(i)
        print "bytes written = %d" % transmitter.send(N*chr(i))
        time.sleep(d)
    transmitter.send("end")
    time.sleep(d)

    #need to hold the serial connection open 
    #  until the data has been written out of the buffer
    print "Tx waiting"
    time.sleep(0) 
    
    print "Tx done"


if __name__ == "__main__":
    main()
